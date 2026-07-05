import requests
import pandas as pd

from urllib.parse import urljoin
from urllib.parse import urlparse
from bs4 import BeautifulSoup

url = input("Enter the URL of the SuccessFactors job listing page: ")

response = requests.get(url)
print(response.status_code)

company_name = urlparse(url).netloc.split('.')[-2]
print(f"Company name: {company_name}")

soup = BeautifulSoup(response.content, "html.parser")

# total number of job listings
pagination = soup.find("span", class_="paginationLabel")
total_results = pagination.find_all("b")[1].get_text(strip=True)
total_results = int(total_results)
print(f"Total job listings: {total_results}")

# listings on current page
listings = soup.find_all("tr", class_="data-row")
print(f"Current page job listings: {len(listings)}")

all_jobs = []
processed_count = 0

while processed_count < total_results:
    if processed_count > 0:
        # Move to the next page of job listings
        current_page_url = urljoin(url, f"{processed_count}")
        print(f"Moving to next page: {current_page_url}")
        response = requests.get(current_page_url)
        soup = BeautifulSoup(response.content, "html.parser")

        # listings on current page
        listings = soup.find_all("tr", class_="data-row")
        print(f"Current page job listings: {len(listings)}")

    # Scraping loop for 1 page of job listings
    for listing in listings:
        partial_joburl = listing.find("a", class_="jobTitle-link")["href"] if listing.find("a", class_="jobTitle-link") else None
        joburl = urljoin(url, partial_joburl) if partial_joburl else None
        print(joburl)
        listing_data = {}
        for td in listing.find_all("td"):
            raw_headers = td.get("headers", [])
            if raw_headers:
                header_id = "_".join(raw_headers)
            else:
                header_id = "unknown"
            text = td.get_text(separator=" ", strip=True)
            listing_data[header_id] = text

        responsejob = requests.get(joburl)
        soupjob = BeautifulSoup(responsejob.content, "html.parser")

        jobtext = soupjob.find_all("div", class_="joblayouttoken")
        texts = []
        for el in jobtext:
            text = el.get_text(strip=True)
            texts.append(text)

        full_job_description = "\n".join(texts)
        combined_listing_data = {
            "joburl": joburl,
            **listing_data, 
            "job_description": full_job_description}
        all_jobs.append(combined_listing_data)
        processed_count += 1
        print(f"Processed {processed_count}/{total_results} job listings.")
    

df = pd.DataFrame(all_jobs)
df.to_csv(f"{company_name}_jobs.csv", index=False)

print(f"Scraping completed. Total jobs scraped: {len(all_jobs)}. Data saved to '{company_name}_jobs.csv'.")
