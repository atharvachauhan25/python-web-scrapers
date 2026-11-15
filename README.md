# 🕷️ Python Web Scraping, Automation & QA Testing Suite

[![CI Test Suite](https://github.com/atharvachauhan25/python-web-scrapers/actions/workflows/ci.yml/badge.svg)](https://github.com/atharvachauhan25/python-web-scrapers/actions)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![Code Style](https://img.shields.io/badge/code%20style-PEP%208-green.svg)](https://peps.python.org/pep-0008/)
[![Test Framework](https://img.shields.io/badge/tested%20with-pytest-yellow)](https://docs.pytest.org/)

A production-grade Python toolkit combining **resilient web scraping**, **automated data validation pipelines (Pydantic)**, **formatted multi-column Excel reporting (`xlsxwriter`)**, and **automated web/API regression testing**.

---

## 📦 What's Inside

| Module / Script | Category | Core Capabilities | Output Formats |
| :--- | :--- | :--- | :--- |
| **`ecommerce_scraper.py`** | Web Scraping | Multi-page pagination, price normalization, star-rating mapping, availability checks | CSV, JSON |
| **`remote_job_scraper.py`** | Lead Generation | Live remote tech job aggregator, keyword/skill filtering, timestamp parsing | CSV, JSON |
| **`reddit_task_scanner.py`** | Forum & Social | TLS fingerprint impersonation (`curl_cffi`), anti-bot bypass, opportunity detection | CSV, JSON |
| **`data_pipeline.py`** | Data Engineering | **Pydantic schema validation**, corrupt data filtering, styled multi-tab Excel export | Styled `.xlsx` |
| **`api_monitor.py`** | Automation & QA | Automated health assertions, status verification, latency benchmarks & QA reporting | Console, Markdown |
| **`tests/test_scrapers.py`** | Automated Testing | Unit & integration test suite (`pytest`) covering parsing, edge cases, and schemas | Test Reports |

---

## 🧪 Automated Testing & QA Suite (`pytest`)

The codebase includes an automated test suite executed via GitHub Actions on every commit and pull request.

```bash
# Run the complete test suite
pytest -v
```

### Coverage Highlights:
- ✅ **Price normalization edge cases**: Accurately extracts floats from currency symbols (`£51.77`, `$19.99`, `Free` -> `0.0`).
- ✅ **Mock DOM extraction**: Unit tests verify HTML parsing without live network dependencies.
- ✅ **Pydantic schema constraints**: Strictly rejects corrupted records (negative prices, missing titles, out-of-range star ratings).
- ✅ **Excel report generation**: Verifies non-empty binary `.xlsx` generation with proper styles.

---

## 🛡️ Data Validation & Formatted Excel Export

Instead of dumping unvalidated raw data, `data_pipeline.py` enforces data contracts using **Pydantic**:

```python
class ScrapedProduct(BaseModel):
    title: str = Field(..., min_length=1)
    price_gbp: float = Field(..., ge=0.0)
    rating_out_of_5: int = Field(..., ge=0, le=5)
    in_stock: bool = True
    url: str
```

It exports directly to a formatted Excel workbook (`sample_data/sample_books.xlsx`) featuring:
- Custom styled navy-blue header row with centered alignment.
- Numeric currency formatting (`£#,##0.00`).
- Automated column width adjustments for clean readability.

---

## 🩺 Automated API & Website Health Monitor

`api_monitor.py` runs automated regression assertions against live web endpoints:

```bash
python api_monitor.py
```

### Sample Automated QA Output:
```text
=================================================================
  AUTOMATED QA REGRESSION & HEALTH REPORT: 3/3 PASSED
=================================================================
Endpoint                  | Status  | Latency    | Result
-----------------------------------------------------------------
Books To Scrape Catalog   | 200     | 1436.06 ms | ✅ PASS
RemoteOK Public API       | 200     | 804.81  ms | ✅ PASS
HackerNews API Item       | 200     | 656.50  ms | ✅ PASS
=================================================================
```

---

## 🚀 Quickstart & Installation

```bash
# Clone the repository
git clone https://github.com/atharvachauhan25/python-web-scrapers.git
cd python-web-scrapers

# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest -v

# Run scrapers & generate sample data
python ecommerce_scraper.py --pages 3
python data_pipeline.py
python api_monitor.py
```

---

## 💼 Freelance Services
Need custom data pipelines, scraping bots, or automated testing tools?

- **Custom Web Scrapers**: Resilient against anti-bot challenges and layout changes.
- **Data Engineering**: Data cleaning, schema validation, and styled Excel / Google Sheets delivery.
- **QA & Automation**: API regression tests, scheduled uptime monitors, and Telegram/Discord alerting bots.
- **Fast Turnaround**: 24–48 hours delivery with full documentation and source code.

📩 **Contact:** DM on Reddit / Discord or open a GitHub issue!
