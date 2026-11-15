import argparse
import logging
import time
from typing import Dict, List, Optional
import requests
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

class EndpointCheck(BaseModel):
    name: str
    url: str
    expected_status: int = 200
    max_latency_ms: float = 2000.0
    required_keyword: Optional[str] = None

class CheckResult(BaseModel):
    name: str
    url: str
    status_code: int
    latency_ms: float
    status_passed: bool
    latency_passed: bool
    keyword_passed: bool
    all_passed: bool
    error_message: Optional[str] = None

def run_automated_health_checks(checks: List[EndpointCheck]) -> List[CheckResult]:
    """
    Executes automated QA regression & health assertions against web targets.
    Measures uptime, status code compliance, latency, and content integrity.
    """
    results = []
    headers = {"User-Agent": "AutomatedQABot/1.0 (Testing Suite)"}

    logging.info(f"Running automated assertions across {len(checks)} target endpoints...")

    for check in checks:
        start_time = time.time()
        try:
            resp = requests.get(check.url, headers=headers, timeout=5)
            latency_ms = round((time.time() - start_time) * 1000, 2)

            status_ok = resp.status_code == check.expected_status
            latency_ok = latency_ms <= check.max_latency_ms
            keyword_ok = (check.required_keyword in resp.text) if check.required_keyword else True

            passed = status_ok and latency_ok and keyword_ok

            results.append(CheckResult(
                name=check.name,
                url=check.url,
                status_code=resp.status_code,
                latency_ms=latency_ms,
                status_passed=status_ok,
                latency_passed=latency_ok,
                keyword_passed=keyword_ok,
                all_passed=passed
            ))

            log_fn = logging.info if passed else logging.warning
            log_fn(f"[{'PASS' if passed else 'FAIL'}] {check.name} - Status: {resp.status_code}, Latency: {latency_ms}ms")

        except Exception as e:
            latency_ms = round((time.time() - start_time) * 1000, 2)
            results.append(CheckResult(
                name=check.name,
                url=check.url,
                status_code=0,
                latency_ms=latency_ms,
                status_passed=False,
                latency_passed=False,
                keyword_passed=False,
                all_passed=False,
                error_message=str(e)
            ))
            logging.error(f"[FAIL] {check.name} encountered error: {e}")

    return results

def print_qa_report(results: List[CheckResult]):
    passed_count = sum(1 for r in results if r.all_passed)
    print("\n" + "=" * 65)
    print(f"  AUTOMATED QA REGRESSION & HEALTH REPORT: {passed_count}/{len(results)} PASSED")
    print("=" * 65)
    print(f"{'Endpoint':<25} | {'Status':<7} | {'Latency':<10} | {'Result':<6}")
    print("-" * 65)
    for r in results:
        res_str = "✅ PASS" if r.all_passed else "❌ FAIL"
        print(f"{r.name:<25} | {r.status_code:<7} | {r.latency_ms:<7} ms | {res_str}")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    # Default test suite targets
    test_endpoints = [
        EndpointCheck(name="Books To Scrape Catalog", url="http://books.toscrape.com/", expected_status=200, max_latency_ms=3000),
        EndpointCheck(name="RemoteOK Public API", url="https://remoteok.com/api", expected_status=200, max_latency_ms=3000),
        EndpointCheck(name="HackerNews API Item", url="https://hacker-news.firebaseio.com/v0/item/8863.json", expected_status=200, max_latency_ms=2000, required_keyword="dhouston"),
    ]
    qa_results = run_automated_health_checks(test_endpoints)
    print_qa_report(qa_results)
