# 🕷️ Python Web Scraping & Data Extraction Toolkit

A collection of resilient, production-ready Python web scrapers and automated data extraction pipelines. Built to demonstrate clean parsing, pagination handling, anti-blocking considerations, and structured exports (CSV & JSON).

---

## 📦 What's Inside

| Scraper Script | Target Type | Key Features | Output Formats |
| :--- | :--- | :--- | :--- |
| **`ecommerce_scraper.py`** | E-Commerce Catalogs | Multi-page pagination, price normalization, star-rating mapping, availability checks | CSV, JSON |
| **`remote_job_scraper.py`** | Job Boards & Live Feeds | Real-time lead generation, keyword & skill filtering, timestamp conversion | CSV, JSON |
| **`reddit_task_scanner.py`** | Community & Forum Feeds | TLS fingerprint impersonation (`curl_cffi`), anti-bot bypass, opportunity detection | CSV, JSON |

---

## 📊 Sample Extracted Data

### 1. E-Commerce Catalog (`sample_data/sample_books.csv`)
Extracted from a multi-page product catalog with price cleaning and rating normalization:

| Title | Price (GBP) | Rating (/5) | In Stock | URL |
| :--- | :---: | :---: | :---: | :--- |
| **A Light in the Attic** | £51.77 | ⭐⭐⭐ | Yes | [Link](http://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html) |
| **Tipping the Velvet** | £53.74 | ⭐ | Yes | [Link](http://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html) |
| **Soumission** | £50.10 | ⭐ | Yes | [Link](http://books.toscrape.com/catalogue/soumission_998/index.html) |
| **Sharp Objects** | £47.82 | ⭐⭐⭐⭐ | Yes | [Link](http://books.toscrape.com/catalogue/sharp-objects_997/index.html) |

### 2. Live Job & Lead Feeds (`sample_data/sample_jobs.csv`)
Aggregated real-time positions filtered by technical skillsets:

| Position | Company | Location | Tags | Date Posted |
| :--- | :--- | :--- | :--- | :---: |
| **Scientific Account Executive** | Adaptyv | Lausanne | `api, sales, golang, engineer` | 2026-10-31 |
| **AWS Cloud Solutions Architect** | Cloudary SAS | Remote | `docker, postgres, sql, api, cloud` | 2026-10-30 |

---

## 🚀 Quickstart & Usage

### 1. Setup
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/python-web-scrapers.git
cd python-web-scrapers

# Install requirements
pip install -r requirements.txt
```

### 2. Run E-Commerce Scraper
Scrapes products across multiple pages with built-in rate-limiting:
```bash
python ecommerce_scraper.py --pages 5 --csv output_books.csv
```

### 3. Run Remote Jobs / Lead Scraper
Filter by specific keywords:
```bash
python remote_job_scraper.py --keywords python backend engineer --limit 25
```

---

## 🛠️ Tech Stack & Methodologies
- **Languages & Libraries:** Python 3, `BeautifulSoup4`, `requests`, `curl-cffi`, `urllib`
- **Techniques Used:**
  - Robust CSS selector parsing & regex data cleanup.
  - Rate-limit handling & respectful crawling delays (`time.sleep`).
  - Handling modern anti-bot protections via TLS browser impersonation.
  - Automated structured export to clean UTF-8 CSV and JSON.

---

## 💼 Freelance Services & Custom Scraping
Need custom data extraction, web automation, or a dedicated scraper for your project?

- **Custom Web Scrapers**: E-commerce, directories, real-estate, lead generation.
- **Data Cleanup & Formatting**: Raw HTML/JSON into clean Excel/CSV/Google Sheets.
- **Automation Scripts**: Scheduled tasks, price monitoring, Discord/Telegram notification bots.
- **Fast Turnaround**: Most scripts delivered within 24–48 hours.

📩 **Get in Touch:** DM me on Reddit / Discord or open an issue here!
