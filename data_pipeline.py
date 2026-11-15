import csv
import json
import logging
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, field_validator
import xlsxwriter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")

class ScrapedProduct(BaseModel):
    """
    Data validation schema for scraped e-commerce products.
    Ensures clean data contracts before loading into databases or spreadsheets.
    """
    title: str = Field(..., min_length=1, description="Product title")
    price_gbp: float = Field(..., ge=0.0, description="Price in GBP (must be >= 0)")
    rating_out_of_5: int = Field(..., ge=0, le=5, description="Star rating between 0 and 5")
    in_stock: bool = Field(default=True, description="Stock availability status")
    url: str = Field(..., description="Absolute product URL")

    @field_validator("title")
    @classmethod
    def clean_title(cls, v: str) -> str:
        cleaned = v.strip()
        if not cleaned:
            raise ValueError("Title cannot be empty")
        return cleaned

class ScrapedJob(BaseModel):
    """
    Data validation schema for remote tech jobs.
    """
    title: str
    company: str
    location: str = "Remote"
    tags: str = ""
    date_posted: str
    apply_url: str

def validate_and_clean_products(raw_data: List[dict]) -> List[ScrapedProduct]:
    """
    Validates a list of raw dictionaries against the Pydantic schema,
    discarding or flagging corrupted entries.
    """
    validated = []
    dropped = 0
    for item in raw_data:
        try:
            validated.append(ScrapedProduct(**item))
        except Exception as e:
            dropped += 1
            logging.warning(f"Validation failed for record: {item.get('title', 'Unknown')} - {e}")
    
    logging.info(f"Validation complete: {len(validated)} passed, {dropped} dropped.")
    return validated

def export_styled_excel(products: List[ScrapedProduct], output_filepath: str):
    """
    Exports validated data into a beautifully formatted Excel sheet
    with styled headers, auto-adjusted columns, and numeric formatting.
    """
    workbook = xlsxwriter.Workbook(output_filepath)
    worksheet = workbook.add_worksheet("Products")

    # Styles
    header_fmt = workbook.add_format({
        "bold": True,
        "font_color": "#FFFFFF",
        "bg_color": "#1F4E79",
        "border": 1,
        "align": "center",
        "valign": "vcenter"
    })
    currency_fmt = workbook.add_format({"num_format": "£#,##0.00", "align": "right"})
    center_fmt = workbook.add_format({"align": "center"})
    text_fmt = workbook.add_format({"align": "left"})

    headers = ["Product Title", "Price (GBP)", "Rating (/5)", "Stock Status", "Product URL"]
    for col_idx, h in enumerate(headers):
        worksheet.write(0, col_idx, h, header_fmt)

    for row_idx, item in enumerate(products, start=1):
        worksheet.write(row_idx, 0, item.title, text_fmt)
        worksheet.write(row_idx, 1, item.price_gbp, currency_fmt)
        worksheet.write(row_idx, 2, f"{'⭐' * item.rating_out_of_5} ({item.rating_out_of_5}/5)", center_fmt)
        worksheet.write(row_idx, 3, "In Stock" if item.in_stock else "Out of Stock", center_fmt)
        worksheet.write(row_idx, 4, item.url, text_fmt)

    # Auto-adjust column widths
    worksheet.set_column(0, 0, 40)
    worksheet.set_column(1, 1, 15)
    worksheet.set_column(2, 2, 18)
    worksheet.set_column(3, 3, 16)
    worksheet.set_column(4, 4, 45)

    workbook.close()
    logging.info(f"Successfully generated formatted Excel report: {output_filepath}")

if __name__ == "__main__":
    # Example conversion of existing sample data
    import os
    sample_csv = "sample_data/sample_books.csv"
    if os.path.exists(sample_csv):
        with open(sample_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            raw = [row for row in reader]
            # Convert types from CSV strings
            for r in raw:
                r["price_gbp"] = float(r["price_gbp"])
                r["rating_out_of_5"] = int(r["rating_out_of_5"])
                r["in_stock"] = r["in_stock"].lower() == "true"
            
            validated = validate_and_clean_products(raw)
            export_styled_excel(validated, "sample_data/sample_books.xlsx")
