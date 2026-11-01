import argparse
import csv
import json
import logging
import re
import time
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

BASE_URL = "http://books.toscrape.com/catalogue/"
START_URL = "http://books.toscrape.com/catalogue/page-1.html"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def clean_price(price_str: str) -> float:
    match = re.search(r"[\d\.]+", price_str)
    return float(match.group()) if match else 0.0

def scrape_books(max_pages: int = 3, delay: float = 0.5):
    """
    Scrapes e-commerce product catalog with pagination, clean data parsing,
    and structured output.
    """
    current_page = 1
    current_url = START_URL
    all_products = []

    logging.info(f"Starting e-commerce scrape (Max pages: {max_pages})")

    while current_url and current_page <= max_pages:
        logging.info(f"Scraping Page {current_page}: {current_url}")
        try:
            resp = requests.get(current_url, headers=HEADERS, timeout=10)
            if resp.status_code != 200:
                logging.error(f"Failed to fetch {current_url} (HTTP {resp.status_code})")
                break

            soup = BeautifulSoup(resp.content, "html.parser")
            product_cards = soup.select("article.product_pod")

            if not product_cards:
                logging.warning(f"No products found on page {current_page}.")
                break

            for card in product_cards:
                # Title
                title_elem = card.select_one("h3 a")
                title = title_elem["title"] if (title_elem and "title" in title_elem.attrs) else title_elem.text.strip()
                relative_link = title_elem["href"] if title_elem else ""
                product_url = urljoin(BASE_URL, relative_link)

                # Price
                price_elem = card.select_one("p.price_color")
                price = clean_price(price_elem.text) if price_elem else 0.0

                # Rating
                rating_elem = card.select_one("p.star-rating")
                rating = 0
                if rating_elem:
                    classes = rating_elem.get("class", [])
                    for c in classes:
                        if c in RATING_MAP:
                            rating = RATING_MAP[c]
                            break

                # Availability
                avail_elem = card.select_one("p.instock.availability")
                in_stock = "In stock" in avail_elem.text if avail_elem else False

                all_products.append({
                    "title": title,
                    "price_gbp": price,
                    "rating_out_of_5": rating,
                    "in_stock": in_stock,
                    "url": product_url
                })

            # Check next page
            next_btn = soup.select_one("li.next a")
            if next_btn and "href" in next_btn.attrs:
                current_url = urljoin(current_url, next_btn["href"])
                current_page += 1
                time.sleep(delay)
            else:
                logging.info("Reached the last available page.")
                break

        except Exception as e:
            logging.error(f"Error on page {current_page}: {e}")
            break

    logging.info(f"Scraping finished. Extracted {len(all_products)} products across {current_page} pages.")
    return all_products

def save_csv(data, filename: str):
    if not data:
        return
    keys = data[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    logging.info(f"Saved {len(data)} records to CSV: {filename}")

def save_json(data, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logging.info(f"Saved {len(data)} records to JSON: {filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Multi-page E-Commerce Scraper")
    parser.add_argument("--pages", type=int, default=3, help="Number of pages to scrape (default: 3)")
    parser.add_argument("--csv", type=str, default="sample_data/sample_books.csv", help="Output CSV path")
    parser.add_argument("--json", type=str, default="sample_data/sample_books.json", help="Output JSON path")
    args = parser.parse_args()

    products = scrape_books(max_pages=args.pages)
    if products:
        import os
        os.makedirs("sample_data", exist_ok=True)
        save_csv(products, args.csv)
        save_json(products, args.json)
