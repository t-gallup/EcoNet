import boto3

# Initialize a session using Amazon DynamoDB
client = boto3.client('dynamodb')

# Define the scan parameters
response = client.scan(
    TableName='AK-Wind-Data',
    FilterExpression='WDSP > :val',
    ExpressionAttributeValues={
        ':val': {'N': '5'}
    },
    ProjectionExpression='Station, WDSP',  # Replace with actual attributes you want to get
    ReturnConsumedCapacity='TOTAL'
)

# Print the response
print(response)
