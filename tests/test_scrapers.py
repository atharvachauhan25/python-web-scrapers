import os
import pytest
from bs4 import BeautifulSoup
from pydantic import ValidationError

from ecommerce_scraper import clean_price, RATING_MAP
from data_pipeline import ScrapedProduct, validate_and_clean_products, export_styled_excel
from api_monitor import EndpointCheck, CheckResult

def test_clean_price():
    """Verify regex price normalization handles various currency formats."""
    assert clean_price("£51.77") == 51.77
    assert clean_price("$19.99") == 19.99
    assert clean_price("Price: 100.50 EUR") == 100.50
    assert clean_price("0.00") == 0.0
    assert clean_price("Free") == 0.0

def test_rating_map():
    """Verify star rating mapping covers standard classes."""
    assert RATING_MAP["One"] == 1
    assert RATING_MAP["Two"] == 2
    assert RATING_MAP["Three"] == 3
    assert RATING_MAP["Four"] == 4
    assert RATING_MAP["Five"] == 5

def test_mock_html_product_extraction():
    """Test HTML parsing logic against isolated DOM fixture."""
    mock_html = """
    <article class="product_pod">
        <h3><a href="sample-book_1/index.html" title="Mastering Python Testing">Mastering Python Testing</a></h3>
        <p class="price_color">£29.99</p>
        <p class="star-rating Four"></p>
        <p class="instock availability"><i class="icon-ok"></i> In stock</p>
    </article>
    """
    soup = BeautifulSoup(mock_html, "html.parser")
    card = soup.select_one("article.product_pod")

    title = card.select_one("h3 a")["title"]
    price = clean_price(card.select_one("p.price_color").text)
    rating_class = [c for c in card.select_one("p.star-rating").get("class", []) if c in RATING_MAP][0]
    rating = RATING_MAP[rating_class]
    in_stock = "In stock" in card.select_one("p.instock.availability").text

    assert title == "Mastering Python Testing"
    assert price == 29.99
    assert rating == 4
    assert in_stock is True

def test_pydantic_valid_product():
    """Verify that correctly formatted product dictionaries pass schema validation."""
    data = {
        "title": "Clean Code",
        "price_gbp": 35.00,
        "rating_out_of_5": 5,
        "in_stock": True,
        "url": "http://example.com/clean-code"
    }
    prod = ScrapedProduct(**data)
    assert prod.title == "Clean Code"
    assert prod.price_gbp == 35.00
    assert prod.rating_out_of_5 == 5

def test_pydantic_invalid_product_rejects():
    """Verify that corrupted data (negative price, out of bound rating) raises ValidationError."""
    with pytest.raises(ValidationError):
        ScrapedProduct(title="Broken Book", price_gbp=-10.0, rating_out_of_5=3, url="http://example.com")

    with pytest.raises(ValidationError):
        ScrapedProduct(title="", price_gbp=10.0, rating_out_of_5=3, url="http://example.com")

    with pytest.raises(ValidationError):
        ScrapedProduct(title="Too high rating", price_gbp=10.0, rating_out_of_5=99, url="http://example.com")

def test_validate_and_clean_filter():
    """Verify batch validation filters out invalid records gracefully."""
    raw_list = [
        {"title": "Valid Book", "price_gbp": 15.0, "rating_out_of_5": 4, "in_stock": True, "url": "http://test.com/1"},
        {"title": "", "price_gbp": 10.0, "rating_out_of_5": 2, "in_stock": True, "url": "http://test.com/2"}, # Empty title
        {"title": "Negative Book", "price_gbp": -5.0, "rating_out_of_5": 1, "in_stock": True, "url": "http://test.com/3"} # Bad price
    ]
    cleaned = validate_and_clean_products(raw_list)
    assert len(cleaned) == 1
    assert cleaned[0].title == "Valid Book"

def test_excel_export_generation(tmp_path):
    """Verify that export_styled_excel produces a valid, non-empty .xlsx file."""
    output_file = str(tmp_path / "test_report.xlsx")
    products = [
        ScrapedProduct(title="Book A", price_gbp=12.50, rating_out_of_5=3, in_stock=True, url="http://test.com/a"),
        ScrapedProduct(title="Book B", price_gbp=24.00, rating_out_of_5=5, in_stock=False, url="http://test.com/b")
    ]
    export_styled_excel(products, output_file)

    assert os.path.exists(output_file)
    assert os.path.getsize(output_file) > 1000 # Valid xlsx file header size
