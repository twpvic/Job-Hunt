import json
import time
import requests
import pandas as pd
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright

url = input("Enter the URL of the Workday job listing page: ")

# Parse the URL to extract the tenant, company name, and site
parsed_url = urlparse(url)
tenant = parsed_url.netloc.split('.')[0] 
company_name = tenant
print(f"Company name (Tenant): {company_name}")

path_parts = parsed_url.path.strip('/').split('/')
SITE = path_parts[1] if len(path_parts) >= 2 else "External"
BASE = f"https://{parsed_url.netloc}"
API_URL = f"{BASE}/wday/cxs/{tenant}/{SITE}/jobs"


PAGE_SIZE = 20          # Workday's default page size for this endpoint
REQUEST_DELAY = 0.5
DETAIL_DELAY = 0.8      # delay between job-detail page loads


# Phase 1: Get all job listings via the Workday JSON API
def fetch_all_listings():
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })

    listings = []
    offset = 0
    total = None

    while True:
        payload = {
            "appliedFacets": {},
            "limit": PAGE_SIZE,
            "offset": offset,
            "searchText": ""
        }
        resp = session.post(API_URL, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        if total is None:
            total = data.get("total", 0)
            print(f"Total jobs found: {total}")

        job_postings = data.get("jobPostings", [])
        if not job_postings:
            break

        for job in job_postings:
            title = job.get("title", "")
            location = job.get("locationsText", "") or job.get("location", "")
            posted_date = job.get("postedOn", "")
            external_path = job.get("externalPath", "")  # e.g. /job/Singapore/Title_REQID
            job_id = job.get("bulletFields", [None])[0] if job.get("bulletFields") else ""

            full_link = f"{BASE}/en-US/{SITE}{external_path}" if external_path else ""

            listings.append({
                "title": title,
                "location": location,
                "posted_date": posted_date,
                "job_id": job_id,
                "link": full_link,
            })

        offset += PAGE_SIZE
        print(f"Fetched {len(listings)} / {total}")

        if offset >= total:
            break

        time.sleep(REQUEST_DELAY)

    return listings


# Phase 2: Visit each job page and scrape full details
def scrape_job_details(listings):
    """
    Opens each job's detail page with Playwright and extracts the full
    job description plus any structured fields Workday exposes
    (job ID, time type, posted date confirmation, etc).
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for i, job in enumerate(listings, 1):
            if not job["link"]:
                job["description"] = ""
                continue

            try:
                page.goto(job["link"], wait_until="domcontentloaded", timeout=30000)
                page.wait_for_selector(
                    '[data-automation-id="jobPostingDescription"]',
                    timeout=15000
                )

                description = page.locator(
                    '[data-automation-id="jobPostingDescription"]'
                ).inner_text()

                # Optional structured fields commonly present on Workday job pages
                def safe_text(selector):
                    try:
                        return page.locator(selector).first.inner_text()
                    except Exception:
                        return ""

                job["description"] = description
                job["job_req_id"] = safe_text('[data-automation-id="job-posting-id"]')
                job["time_type"] = safe_text('[data-automation-id="time"]')

                print(f"[{i}/{len(listings)}] Scraped: {job['title']}")

            except Exception as e:
                print(f"[{i}/{len(listings)}] FAILED: {job['title']} -> {e}")
                job["description"] = ""

            time.sleep(DETAIL_DELAY)

        browser.close()

    return listings



if __name__ == "__main__":
    print("Phase 1: Fetching job listings from Workday API...")
    all_jobs = fetch_all_listings()

    # Save a raw checkpoint in case Phase 2 fails partway through[cite: 1]
    with open("listings_checkpoint.json", "w") as f:
        json.dump(all_jobs, f, indent=2)

    print(f"\nPhase 2: Scraping {len(all_jobs)} job detail pages...")
    all_jobs = scrape_job_details(all_jobs)

    print("\nPhase 3: Saving data...")
    # Export to CSV using pandas to match the SuccessFactors script style
    df = pd.DataFrame(all_jobs)
    output_filename = f"{company_name}_jobs.csv"
    df.to_csv(output_filename, index=False)

    print(f"Scraping completed. Total jobs scraped: {len(all_jobs)}. Data saved to '{output_filename}'.")