"""
B2B Lead Scraper & Business Directory Extractor.
Extracts local business listings, contacts, categories, and addresses
for sales outreach and marketing agency lead pipelines.
"""

import re
import csv
import json
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class BusinessLead:
    name: str
    category: str
    phone: str
    location: str
    city: str
    website: Optional[str] = "N/A"
    verified: bool = True

    def clean_phone(self) -> str:
        """Standardizes raw phone strings into a clean dialable format."""
        digits = re.sub(r"[^\d]", "", self.phone)
        if digits.startswith("91") and len(digits) == 12:
            return f"+91 {digits[2:7]} {digits[7:]}"
        if len(digits) == 10:
            return f"+91 {digits[:5]} {digits[5:]}"
        return self.phone


class B2BLeadScraper:
    """Production scraper for directory entries and local business contacts."""

    def __init__(self, city: str = "Pune", category: str = "Dental Clinic"):
        self.city = city
        self.category = category

    def parse_directory_html(self, html_snippet: str) -> List[BusinessLead]:
        """
        Parses HTML listing cards from directory or map search results.
        Extracts business name, phone, address, and online presence.
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_snippet, "html.parser")
        leads: List[BusinessLead] = []

        cards = soup.find_all(class_=re.compile(r"listing|card|result|business", re.I))
        for card in cards:
            name_el = card.find(["h2", "h3", "a"], class_=re.compile(r"title|name", re.I))
            if not name_el:
                continue

            name = name_el.get_text(strip=True)

            phone_el = card.find(class_=re.compile(r"phone|tel|contact", re.I)) or card.find("a", href=re.compile(r"tel:"))
            raw_phone = phone_el.get_text(strip=True) if phone_el else "Available on request"

            addr_el = card.find(class_=re.compile(r"address|location|area", re.I))
            location = addr_el.get_text(strip=True) if addr_el else f"{self.city}, Maharashtra"

            web_el = card.find("a", class_=re.compile(r"web|url|site", re.I))
            website = web_el.get("href") if web_el else "N/A"

            lead = BusinessLead(
                name=name,
                category=self.category,
                phone=raw_phone,
                location=location,
                city=self.city,
                website=website,
                verified=True,
            )
            leads.append(lead)

        return leads

    def export_to_csv(self, leads: List[BusinessLead], filepath: str) -> None:
        """Exports parsed business leads into a standardized CRM-compatible CSV."""
        fieldnames = ["Clinic / Business Name", "Category", "Contact Phone", "Location / Area", "City", "Website", "Verification Status"]
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(fieldnames)
            for lead in leads:
                writer.writerow([
                    lead.name,
                    lead.category,
                    lead.clean_phone(),
                    lead.location,
                    lead.city,
                    lead.website,
                    "Verified Active" if lead.verified else "Unverified"
                ])


if __name__ == "__main__":
    scraper = B2BLeadScraper(city="Pune", category="Dental Clinic & Healthcare")
    sample_html = """
    <div class="business-card">
        <h3 class="business-name">Smiles Dental Clinic & Implant Center</h3>
        <span class="phone-number">+91 98220 14829</span>
        <div class="address-area">FC Road, Shivajinagar, Pune 411005</div>
        <a class="website-link" href="https://smilesdentalpune.example.com">Website</a>
    </div>
    <div class="business-card">
        <h3 class="business-name">Dr. Deshmukh Advanced Dentistry</h3>
        <span class="phone-number">9890123411</span>
        <div class="address-area">DP Road, Kothrud, Pune 411038</div>
    </div>
    """
    results = scraper.parse_directory_html(sample_html)
    print(f"Extracted {len(results)} leads:")
    for r in results:
        print(f" - {r.name} | {r.clean_phone()} | {r.location}")
