import argparse
import csv
import json
import logging
import time
from curl_cffi import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

DEFAULT_SUBREDDITS = ["slavelabour", "DoneDirtCheap", "forhire"]

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def scan_reddit_tasks(subreddits=None, keywords=None, limit=25):
    """
    Monitors freelance subreddits for [TASK] and [HIRING] posts,
    bypassing anti-bot / TLS fingerprinting using curl_cffi (impersonating Chrome).
    """
    if subreddits is None:
        subreddits = DEFAULT_SUBREDDITS

    found_tasks = []

    for sub in subreddits:
        url = f"https://www.reddit.com/r/{sub}/new.json?limit={limit}"
        logging.info(f"Scanning r/{sub} for opportunities...")

        try:
            # Impersonate modern browser TLS profile to prevent 403 / 429 rate limiting
            resp = requests.get(url, impersonate="chrome120", headers=HEADERS, timeout=10)

            if resp.status_code != 200:
                logging.warning(f"r/{sub} returned HTTP {resp.status_code}")
                continue

            data = resp.json().get("data", {}).get("children", [])
            for item in data:
                post = item.get("data", {})
                title = post.get("title", "")
                flair = str(post.get("link_flair_text", "")).lower()
                title_lower = title.lower()

                # Detect client tasks / hiring posts
                is_task = (
                    "[task]" in title_lower
                    or "task" in flair
                    or "hiring" in flair
                    or "[hiring]" in title_lower
                )

                if is_task:
                    # Optional keyword filtering
                    if keywords:
                        match = any(kw.lower() in title_lower or kw.lower() in post.get("selftext", "").lower() for kw in keywords)
                        if not match:
                            continue

                    created_utc = post.get("created_utc", 0)
                    minutes_ago = int((time.time() - created_utc) / 60) if created_utc else 0

                    found_tasks.append({
                        "subreddit": f"r/{sub}",
                        "title": title,
                        "bids_comments": post.get("num_comments", 0),
                        "posted_minutes_ago": minutes_ago,
                        "url": f"https://reddit.com{post.get('permalink', '')}",
                        "author": post.get("author", ""),
                        "preview_snippet": post.get("selftext", "").strip().replace("\n", " ")[:240]
                    })

        except Exception as e:
            logging.error(f"Error querying r/{sub}: {e}")

    logging.info(f"Scan complete. Found {len(found_tasks)} relevant task listings.")
    return found_tasks

def save_csv(data, filename: str):
    if not data:
        return
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    logging.info(f"Saved {len(data)} tasks to CSV: {filename}")

def save_json(data, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved {len(data)} tasks to JSON: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Real-time Reddit Freelance Lead Scanner")
    parser.add_argument("--subs", nargs="+", default=DEFAULT_SUBREDDITS, help="Subreddits to check")
    parser.add_argument("--keywords", nargs="+", default=None, help="Optional keywords to filter by (e.g. python scrape audio)")
    parser.add_argument("--limit", type=int, default=25, help="Posts per subreddit (default: 25)")
    parser.add_argument("--csv", type=str, default="sample_data/sample_reddit_tasks.csv", help="Output CSV path")
    parser.add_argument("--json", type=str, default="sample_data/sample_reddit_tasks.json", help="Output JSON path")
    args = parser.parse_args()

    tasks = scan_reddit_tasks(subreddits=args.subs, keywords=args.keywords, limit=args.limit)
    if tasks:
        import os
        os.makedirs("sample_data", exist_ok=True)
        save_csv(tasks, args.csv)
        save_json(tasks, args.json)
