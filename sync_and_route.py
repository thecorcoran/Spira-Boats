#!/usr/bin/env python3
"""
Spira Digital Archive - Automatic Asset Router & Ingester
Matches downloaded or manifested files against model folders, manuals, and technical reports.
"""

import os
import re
import json
import shutil

ROUTING_MAP = {
    # Model name patterns -> (category, model_folder)
    "seneca": ("pacific-power-dories", "15-seneca"),
    "tillamook": ("pacific-power-dories", "17-tillamook"),
    "courtenay": ("pacific-power-dories", "17-courtenay"),
    "albion": ("pacific-power-dories", "19-albion"),
    "albi": ("pacific-power-dories", "19-albion"),
    "anacapa": ("pacific-power-dories", "19-anacapa"),
    "avila": ("pacific-power-dories", "20-avila"),
    "alamitos": ("pacific-power-dories", "21-alamitos"),
    "winchester": ("pacific-power-dories", "23-winchester"),
    "farallon": ("pacific-power-dories", "23-farallon"),
    "caladesi": ("pacific-power-dories", "25-caladesi"),
    "sitka": ("pacific-power-dories", "27-sitka"),
    "kodiak": ("pacific-power-dories", "32-kodiak"),
    
    "oysterman": ("carolina-dories", "16-oysterman"),
    "oyst": ("carolina-dories", "16-oysterman"),
    "carolinian": ("carolina-dories", "19-carolinian"),
    "caro": ("carolina-dories", "19-carolinian"),
    "hatteras": ("carolina-dories", "20-hatteras"),
    "hatt": ("carolina-dories", "20-hatteras"),
    "carolina": ("carolina-dories", "22-carolina-dory"),

    "rogue": ("drift-boats-and-river", "14-rogue-river"),
    "mackenzie": ("drift-boats-and-river", "16-mackenzie"),
    "mack": ("drift-boats-and-river", "16-mackenzie"),
    "clackamas": ("drift-boats-and-river", "17-clackamas"),

    "huntington": ("garveys-skiffs-and-utility", "08-huntington-harbor"),
    "newport": ("garveys-skiffs-and-utility", "10-newport-harbor"),
    "channel": ("garveys-skiffs-and-utility", "12-channel-islands"),
    "mission": ("garveys-skiffs-and-utility", "14-mission-bay"),
    "miss": ("garveys-skiffs-and-utility", "14-mission-bay"),
    "clemente": ("garveys-skiffs-and-utility", "16-san-clemente"),
    "clem": ("garveys-skiffs-and-utility", "16-san-clemente"),
    "backbay": ("garveys-skiffs-and-utility", "16-back-bay"),
    "back": ("garveys-skiffs-and-utility", "16-back-bay"),
    "sandiego": ("garveys-skiffs-and-utility", "18-san-diego"),
    "sanpedro": ("garveys-skiffs-and-utility", "20-san-pedro"),

    "keylargo": ("cruisers-and-trawlers", "20-key-largo"),
    "keyl": ("cruisers-and-trawlers", "20-key-largo"),
    "chinook": ("cruisers-and-trawlers", "21-chinook"),
    "chin": ("cruisers-and-trawlers", "21-chinook"),
    "gloucester": ("cruisers-and-trawlers", "24-gloucester"),
    "glou": ("cruisers-and-trawlers", "24-gloucester"),
    "kachemak": ("cruisers-and-trawlers", "24-kachemak"),
    "kach": ("cruisers-and-trawlers", "24-kachemak"),
    "alaskan": ("cruisers-and-trawlers", "26-alaskan"),
    "alas": ("cruisers-and-trawlers", "26-alaskan"),
}

def route_file(src_path, filename, base_archive_dir="archive"):
    lower = filename.lower()

    # 1. Technical Reports
    if re.match(r"^br[-_]\d+", lower) or "report" in lower:
        dest_dir = os.path.join(base_archive_dir, "technical-reports")
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy2(src_path, os.path.join(dest_dir, filename))
        return f"technical-reports/{filename}"

    # 2. General Manuals & Guides
    if any(k in lower for k in ["ply-on-frame", "framedply", "strikearc", "boatbuilding", "kayak", "handbook", "uscg"]):
        dest_dir = os.path.join(base_archive_dir, "manuals-and-guides")
        os.makedirs(dest_dir, exist_ok=True)
        shutil.copy2(src_path, os.path.join(dest_dir, filename))
        return f"manuals-and-guides/{filename}"

    # 3. Model Matching
    for pattern, (cat, folder) in ROUTING_MAP.items():
        if pattern in lower:
            dest_dir = os.path.join(base_archive_dir, "boats", cat, folder)
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copy2(src_path, os.path.join(dest_dir, filename))
            return f"boats/{cat}/{folder}/{filename}"

    # Fallback to general documents
    dest_dir = os.path.join(base_archive_dir, "general-documents")
    os.makedirs(dest_dir, exist_ok=True)
    shutil.copy2(src_path, os.path.join(dest_dir, filename))
    return f"general-documents/{filename}"

def route_all_downloads(source_dir="raw_downloads", base_archive_dir="archive"):
    if not os.path.exists(source_dir):
        print(f"Source directory {source_dir} not found.")
        return

    routed_count = 0
    for root, _, files in os.walk(source_dir):
        for f in files:
            src = os.path.join(root, f)
            dest = route_file(src, f, base_archive_dir)
            print(f"Routed: {f} -> {dest}")
            routed_count += 1
    print(f"\nTotal files routed into archive: {routed_count}")

if __name__ == "__main__":
    route_all_downloads()
