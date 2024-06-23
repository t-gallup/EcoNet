'''
*Version: 2.0 Published: 2021/03/09* Source: [NASA POWER](https://power.larc.nasa.gov/)
POWER API Multi-Point Download
This is an overview of the process to request data from multiple data points from the POWER API.
'''

import os, sys, time, json, urllib3, requests, multiprocessing
import pandas as pd

urllib3.disable_warnings()

def download_function(collection):
    ''' '''

    request, filepath = collection
    response = requests.get(url=request, verify=False, timeout=30.00).json()
    with open(filepath, 'w') as file_object:
        json.dump(response, file_object)
    print(pd.read_csv(file_object))

class Process():

    def __init__(self):

        self.processes = 5 # Please do not go more than five concurrent requests.

        self.request_template = r"https://power.larc.nasa.gov/api/temporal/daily/point?parameters=T2M,T2MDEW,T2MWET,TS,T2M_RANGE,T2M_MAX,T2M_MIN&community=RE&longitude={longitude}&latitude={latitude}&start=20150101&end=20150305&format=JSON"
        self.filename_template = "File_Lat_{latitude}_Lon_{longitude}.csv"

        self.messages = []

    def execute(self):

        locations = [(39.9373, -83.0485), (10.9373, -50.0485)]

        requests = []
        for latitude, longitude in locations:
            request = self.request_template.format(latitude=latitude, longitude=longitude)
            filename = self.filename_template.format(latitude=latitude, longitude=longitude)
            requests.append((request, filename))

        requests_total = len(requests)

        pool = multiprocessing.Pool(self.processes)
        x = pool.imap_unordered(download_function, requests)

        for i, df in enumerate(x, 1):
            sys.stderr.write('\rExporting {0:%}'.format(i/requests_total))

       

if __name__ == '__main__':
    Process().execute()