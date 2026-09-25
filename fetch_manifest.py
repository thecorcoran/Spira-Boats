#!/usr/bin/env python3
"""
Spira International Digital Archive - Asset Discovery & Manifest Generator
Queries Wayback Machine CDX API for spirainternational.com and generates
structured manifests for boat plans, BOMs, technical reports, manuals, and drawings.
"""

import json
import os
import re
import urllib.parse
import requests

BASE_CDX_URL = "http://web.archive.org/cdx/search/cdx"
DOMAIN = "spirainternational.com/*"

def query_cdx():
    print("Querying Wayback Machine CDX API for all captures...")
    params = {
        "url": DOMAIN,
        "output": "json",
        "fl": "original,timestamp,statuscode,mimetype",
        "collapse": "urlkey"
    }
    resp = requests.get(BASE_CDX_URL, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    headers = data[0]
    rows = data[1:]
    print(f"Total raw records retrieved: {len(rows)}")
    return rows

def categorize_records(rows):
    study_plans = []
    boms = []
    tech_reports = []
    manuals = []
    other_pdfs = []
    model_pages = []
    plates_and_images = []

    # Filter only HTTP 200 captures
    for row in rows:
        orig_url, timestamp, status, mime = row
        if status != "200":
            continue

        wayback_url = f"https://web.archive.org/web/{timestamp}id_/{orig_url}"
        parsed_path = urllib.parse.urlparse(orig_url).path
        filename = os.path.basename(parsed_path)
        clean_name = urllib.parse.unquote(filename)
        lower_name = clean_name.lower()

        entry = {
            "original_url": orig_url,
            "wayback_url": wayback_url,
            "timestamp": timestamp,
            "filename": clean_name,
            "mime": mime
        }

        # PDFs
        if mime == "application/pdf" or lower_name.endswith(".pdf"):
            if "study" in lower_name:
                study_plans.append(entry)
            elif "bom" in lower_name or "bill of material" in lower_name:
                boms.append(entry)
            elif re.match(r"^br[-_]\d+", lower_name) or "report" in lower_name:
                tech_reports.append(entry)
            elif any(k in lower_name for k in ["manual", "guide", "kayak", "ply-on-frame", "book", "handbook"]):
                manuals.append(entry)
            else:
                other_pdfs.append(entry)
        # HTML Model Pages
        elif mime == "text/html" or lower_name.endswith(".html") or lower_name.endswith(".php"):
            # Exclude obvious non-boat pages (like checkout, cart, affiliate, etc.)
            exclude = ["cart", "order", "login", "register", "privacy", "contact", "about", "terms", "faq"]
            if not any(ex in lower_name for ex in exclude):
                model_pages.append(entry)
        # Drawing plates & images
        elif mime.startswith("image/") or any(lower_name.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif", ".dwg", ".dxf"]):
            if any(k in lower_name for k in ["lines", "profile", "study", "plan", "drawing", "plate", "station", "offset", "cad", "dory", "skiff"]):
                plates_and_images.append(entry)

    return {
        "study_plans": study_plans,
        "bills_of_materials": boms,
        "technical_reports": tech_reports,
        "manuals_and_guides": manuals,
        "other_documents": other_pdfs,
        "model_pages": model_pages,
        "plates_and_drawings": plates_and_images
    }

def main():
    os.makedirs("manifests", exist_ok=True)
    rows = query_cdx()
    catalog = categorize_records(rows)

    summary = {}
    for cat, items in catalog.items():
        summary[cat] = len(items)
        out_file = os.path.join("manifests", f"{cat}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)
        print(f"Saved {len(items):>4} items -> {out_file}")

    with open("manifests/summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n--- Manifest Summary ---")
    for k, v in summary.items():
        print(f"  {k.replace('_', ' ').title()}: {v}")

if __name__ == "__main__":
    main()
