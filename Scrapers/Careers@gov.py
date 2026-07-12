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


original_csv = pd.read_csv(output_filename)

new_csv = pd.DataFrame()

# 3. Map and transform the columns
# 'title' maps directly to 'jobTitle'
new_csv['title'] = original_csv['jobTitle']

# 'location' maps to 'location', filling empty values with 'Singapore' (default for gov.sg)
new_csv['location'] = original_csv['location'].fillna('Singapore')

# 'posted_date' comes from 'startDate' (which is in epoch milliseconds)
new_csv['posted_date'] = pd.to_datetime(original_csv['startDate'], unit='ms').dt.strftime('%Y-%m-%d')

# 'job_id' maps directly to 'jobId'
new_csv['job_id'] = original_csv['jobId']

# 'link' is constructed using the base careers.gov.sg URL and the jobId
new_csv['link'] = 'https://www.careers.gov.sg/job/' + original_csv['jobId'].astype(str)

# 'description' combines the job description, responsibilities, and requirements 
desc = original_csv['jobDescription'].fillna('')
resp = original_csv['jobResponsibilities'].fillna('')
req = original_csv['jobRequirements'].fillna('')

new_csv['description'] = desc + "\n\nResponsibilities:\n" + resp + "\n\nRequirements:\n" + req

# 'job_req_id' maps to the internal posting number
new_csv['job_req_id'] = original_csv['postingNo']

# 'time_type' maps to 'workArrangement' (e.g., Full-time, Part-time)
new_csv['time_type'] = original_csv['workArrangement'].fillna(original_csv['employmentType'])

# 4. Save the transformed data to a new CSV file
new_csv.to_csv(output_filename, index=False)
print(f"Successfully converted and saved to {output_filename}")