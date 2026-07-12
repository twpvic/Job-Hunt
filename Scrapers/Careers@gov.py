import json
import time
import requests
import pandas as pd
import csv

Data_url = "https://raw.githubusercontent.com/opengovsg/careersgovsg-jobs-data/main/data/job-listings.csv"

output_filename = "careersgovsg-job-listings.csv"

response  = requests.get(Data_url)

if response.status_code == 200:
    with open(output_filename, "wb") as f:
        f.write(response.content)
    print(f"Data saved to '{output_filename}'")

else:
    print(f"Failed to fetch data. Status code: {response.status_code}")



