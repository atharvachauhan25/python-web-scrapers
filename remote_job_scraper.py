import argparse
import csv
import json
import logging
from datetime import datetime
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

API_URL = "https://remoteok.com/api"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

def fetch_remote_jobs(keywords=None, limit=50):
    """
    Fetches real-time remote tech jobs from RemoteOK, cleans tags,
    filters by desired roles/skills, and structures the output.
    """
    logging.info(f"Connecting to RemoteOK job feed...")
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            logging.error(f"Failed to fetch jobs (HTTP {response.status_code})")
            return []

        raw_items = response.json()
        jobs = []

        # The first element in RemoteOK API is metadata / legal notice
        job_entries = [item for item in raw_items if isinstance(item, dict) and "position" in item]

        for entry in job_entries:
            title = entry.get("position", "").strip()
            company = entry.get("company", "").strip()
            location = entry.get("location", "Remote").strip()
            tags = entry.get("tags", [])
            tags_str = ", ".join(tags) if isinstance(tags, list) else str(tags)
            url = entry.get("url", "")
            epoch_date = entry.get("epoch", 0)
            date_posted = (
                datetime.fromtimestamp(epoch_date).strftime("%Y-%m-%d")
                if epoch_date
                else "N/A"
            )

            # Filtering logic
            if keywords:
                search_corpus = f"{title} {company} {tags_str}".lower()
                matches = any(kw.lower() in search_corpus for kw in keywords)
                if not matches:
                    continue

            jobs.append({
                "title": title,
                "company": company,
                "location": location,
                "tags": tags_str,
                "date_posted": date_posted,
                "apply_url": url,
            })

            if len(jobs) >= limit:
                break

        logging.info(f"Retrieved and processed {len(jobs)} relevant remote positions.")
        return jobs

    except Exception as e:
        logging.error(f"Error fetching remote jobs: {e}")
        return []

def save_csv(data, filename: str):
    if not data:
        return
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    logging.info(f"Saved {len(data)} job listings to CSV: {filename}")

def save_json(data, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved {len(data)} job listings to JSON: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live Remote Jobs Scraper & Aggregator")
    parser.add_argument("--keywords", nargs="+", default=None, help="Filter by skills (e.g. python backend engineer)")
    parser.add_argument("--limit", type=int, default=30, help="Max records to return (default: 30)")
    parser.add_argument("--csv", type=str, default="sample_data/sample_jobs.csv", help="Output CSV path")
    parser.add_argument("--json", type=str, default="sample_data/sample_jobs.json", help="Output JSON path")
    args = parser.parse_args()

    results = fetch_remote_jobs(keywords=args.keywords, limit=args.limit)
    if results:
        import os
        os.makedirs("sample_data", exist_ok=True)
        save_csv(results, args.csv)
        save_json(results, args.json)
