import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import numpy as np
from openai import OpenAI
import time
import matplotlib.pyplot as plt
import mpld3
import streamlit.components.v1 as components
import boto3
import seaborn as sns
import io
import base64
import json
import pandas as pd


client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
boto_client = boto3.client('dynamodb')

custom_prompt = "Give helpful and short responses. Make sure that if you include an abbreviation for a US state (like MI), make sure it is capitalized. Also if a place mentioned, make sure you list the state of origin (berkeley, CA for example)"

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase.json')
    firebase_admin.initialize_app(cred)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'login'

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o"

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "I can assist you in generating visualizations and providing detailed information about renewable energy sources, helping you enhance access and understanding."}]
    st.session_state.messages.append({"role": "assistant", "content": custom_prompt})

# CSS styles
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
    
    .stApp {
        background-image: url('https://images.unsplash.com/photo-1466611653911-95081537e5b7');
        background-size: cover;
        background-position: center;
    }
    .main-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        padding: 2rem;
        max-width: 400px;
        margin: 0 auto;
    }
    .title {
        font-family: 'Roboto', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTextInput > div > div > input {
        background-color: #2C2C2C;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        width: 100%;
    }
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.5);
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        padding: 0.5rem 2rem;
        border: none;
        border-radius: 20px;
        cursor: pointer;
        width: 100%;
    }
    .button-container {
        display: flex;
        justify-content: space-between;
        width: 100%;
        margin-top: 1rem;
    }
    .button-container > div {
        width: 48%;
    }
    .streamlit-expanderHeader {
        display: none;
    }
    .ai-message {
        color: black;  /* or any other color you prefer */
        background-color: #FFFFED;  
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    
    .user-message{
        color: black;
        background-color: #FFFFED;  
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def login_page():
    def f():
        try:
            user = auth.get_user_by_email(email)
            st.session_state.logged_in = True
            st.session_state.page = 'chatbot'
        except:
            st.warning('Login Failed')
            
    def g():
        try:
            user = auth.create_user(email=email, password=password, uid=username)
            st.session_state.logged_in = True
            st.balloons()
            st.session_state.page = 'chatbot'
        except: 
            st.warning('Sign-up Failed')

    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
        
        .stApp {
            background-image: url('https://images.unsplash.com/photo-1466611653911-95081537e5b7');
            background-size: cover;
            background-position: center;
        }
        .main-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            padding: 2rem;
            max-width: 400px;
            margin: 0 auto;
        }
        .title {
            font-family: 'Roboto', sans-serif;
            font-size: 2.5rem;
            font-weight: 700;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
        }
        .stTextInput > div > div > input {
            background-color: #2C2C2C;
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            width: 100%;
        }
        .stTextInput > div > div > input::placeholder {
            color: rgba(255, 255, 255, 0.5);
        }
        .stButton > button {
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
            padding: 0.5rem 2rem;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            width: 100%;
        }
        .button-container {
            display: flex;
            justify-content: space-between;
            width: 100%;
            margin-top: 1rem;
        }
        .button-container > div {
            width: 48%;
        }
        .streamlit-expanderHeader {
            display: none;
        }
        </style>
        """, unsafe_allow_html=True)

    st.markdown('<h1 class="title">EcoNet.AI</h1>', unsafe_allow_html=True)

    choice = st.selectbox('Login/Signup', ['Login', 'Sign up'])
    if choice == 'Login':
        email = st.text_input("Email", key="email")
        password = st.text_input("Password", type="password", key="password")
        st.button('Login', on_click=f)
    else:
        email = st.text_input('Email Address', key='email')
        password = st.text_input('Password', type='password')
        username = st.text_input('Enter your unique username', key='username')
        st.button('Create my account', on_click=g)
            
def fetch_data(full_response):
    response = boto_client.scan(
        TableName=full_response + '-Wind-Data',
        FilterExpression='WDSP BETWEEN :val1 AND :val2',
        ExpressionAttributeValues={
            ':val1': {'N': '9'},
            ':val2': {'N': '15'}
        },
        ProjectionExpression='Station, WDSP',  # Replace with actual attributes you want to get
        ReturnConsumedCapacity='TOTAL'
    )
    items = response['Items']
    processed_items = []
    for item in items:
        processed_item = {
            'WDSP': float(item['WDSP']['N']),
            'Station': item['Station']['S']
        }
        processed_items.append(processed_item)

    generate_plots_and_analysis(processed_items, 'WDSP')


            
def chatbot():
    st.title('Visualize and interact with Climate Data Easily')
    
    # Display existing messages
    for message in st.session_state.messages:
        if message["content"] != custom_prompt:
            with st.chat_message(message["role"]):
                if message["role"] == "assistant":
                    st.markdown(f'<div class="ai-message">{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)

    # Handle new user input
    if prompt := st.chat_input("Input your question here!"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Create the stream
            stream = client.chat.completions.create(
                model=st.session_state["openai_model"],
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            
            
            
            # Process the stream
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    # Update the message placeholder with the growing response
                    message_placeholder.markdown(f'<div class="ai-message">{full_response}</div>', unsafe_allow_html=True)
                    time.sleep(0.05)  # Small delay to control the stream speed
        
            s = contains_us_state_abbreviation(full_response)
            fetch_data(s)
            # After the stream is complete, add the full response to the session state
            st.session_state.messages.append({"role": "assistant", "content": full_response})

def contains_us_state_abbreviation(s):
    us_state_abbreviations = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    }
    
    # Split the string by non-alphanumeric characters to find words
    words = set(s.split())
    
    # Check if any word in the set of words is a US state abbreviation
    for word in words:
        if word in us_state_abbreviations:
            return word
        
    return "CA"


def generate_plots_and_analysis(df, target_column):
    plots_info = {}
    print(df)
    data = pd.DataFrame(df)
    # Plot correlation heatmap
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.barh(data['Station'], data['WDSP'], color='skyblue')
    ax.set_xlabel('Wind Speed (WDSP)')
    ax.set_ylabel('Station')
    ax.set_title('Wind Speeds at Various Stations')
    ax.grid(axis='x')
    # Analysis
    st.pyplot(fig)
    return plots_info

if st.session_state.page == 'chatbot':
    chatbot()
else:
    login_page()