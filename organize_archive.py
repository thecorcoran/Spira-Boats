#!/usr/bin/env python3
"""
Spira Digital Archive - Hull Classification & Catalog Organizer
Maps designs into established hull categories and sets up organized folders
with specs.md templates and associated study plans, BOMs, and guides.
"""

import os
import json
import shutil
import re

HULL_CATEGORIES = {
    "pacific-power-dories": {
        "title": "Pacific Power Dories",
        "description": "V-bottom and flat-bottom ocean planing dories designed for surf launches and rough coastal conditions.",
        "models": {
            "15-seneca": {"name": "Seneca", "length": "15'", "type": "Pacific Power Dory"},
            "17-tillamook": {"name": "Tillamook", "length": "17'", "type": "Pacific Power Dory"},
            "17-courtenay": {"name": "Courtenay Offshore", "length": "17'", "type": "Offshore Power Dory"},
            "19-albion": {"name": "Albion", "length": "19'", "type": "Pacific Power Dory"},
            "19-anacapa": {"name": "Anacapa Offshore", "length": "19'", "type": "Offshore Power Dory"},
            "20-avila": {"name": "Avila", "length": "20'", "type": "Pacific Power Dory"},
            "21-alamitos": {"name": "Alamitos", "length": "21'", "type": "Pacific Power Dory"},
            "23-winchester": {"name": "Winchester", "length": "23'", "type": "Pacific Power Dory"},
            "23-farallon": {"name": "Farallon Offshore", "length": "23'", "type": "Offshore Power Dory"},
            "25-caladesi": {"name": "Caladesi", "length": "25'", "type": "Pacific Power Dory"},
            "27-sitka": {"name": "Sitka", "length": "27'", "type": "Pacific Power Dory"},
            "32-kodiak": {"name": "Kodiak", "length": "32'", "type": "Pacific Power Dory"}
        }
    },
    "carolina-dories": {
        "title": "Carolina Dories & Skiffs",
        "description": "Traditional Carolina style flat-bottom and semi-V dories built for shallow coastal waters, estuaries, and chop.",
        "models": {
            "16-oysterman": {"name": "Oysterman", "length": "16'", "type": "Carolina Dory"},
            "19-carolinian": {"name": "Carolinian", "length": "19'", "type": "Carolina Dory"},
            "20-hatteras": {"name": "Hatteras", "length": "20'", "type": "Carolina Dory"},
            "22-carolina-dory": {"name": "Carolina Dory", "length": "22'", "type": "Carolina Dory"}
        }
    },
    "drift-boats-and-river": {
        "title": "Drift Boats & River Dories",
        "description": "Rocker-bottom whitewater and river drift boats for rowing, fly fishing, and river navigation.",
        "models": {
            "14-rogue-river": {"name": "Rogue River", "length": "14'", "type": "Drift Boat"},
            "16-mackenzie": {"name": "Mackenzie", "length": "16'", "type": "River Drift Boat"},
            "17-clackamas": {"name": "Clackamas", "length": "17'", "type": "Drift Boat"}
        }
    },
    "garveys-skiffs-and-utility": {
        "title": "Garveys, Prams & Utility Skiffs",
        "description": "Blunt-bow garveys, rowing prams, flats boats, and utility skiffs for protected waters and bay fishing.",
        "models": {
            "08-huntington-harbor": {"name": "Huntington Harbor", "length": "8'", "type": "Pram / Dinghy"},
            "10-newport-harbor": {"name": "Newport Harbor", "length": "10'", "type": "Pram / Dinghy"},
            "12-channel-islands": {"name": "Channel Islands", "length": "12'", "type": "Skiff"},
            "14-mission-bay": {"name": "Mission Bay", "length": "14'", "type": "Garvey Skiff"},
            "16-san-clemente": {"name": "San Clemente", "length": "16'", "type": "Garvey Skiff"},
            "16-back-bay": {"name": "Back Bay", "length": "16'", "type": "Flats Skiff"},
            "18-san-diego": {"name": "San Diego", "length": "18'", "type": "Garvey Skiff"},
            "20-san-pedro": {"name": "San Pedro", "length": "20'", "type": "Garvey Skiff"}
        }
    },
    "cruisers-and-trawlers": {
        "title": "Cruisers, Trawlers & Workboats",
        "description": "Cabin cruisers, pocket trawlers, and heavy-duty workboats designed for extended passages and utility.",
        "models": {
            "20-key-largo": {"name": "Key Largo", "length": "20'", "type": "Pocket Cruiser"},
            "21-chinook": {"name": "Chinook", "length": "21'", "type": "Pocket Trawler"},
            "24-gloucester": {"name": "Gloucester", "length": "24'", "type": "Lobster Boat / Cruiser"},
            "24-kachemak": {"name": "Kachemak", "length": "24'", "type": "Alaskan Cruiser"},
            "26-alaskan": {"name": "Alaskan", "length": "26'", "type": "Cabin Cruiser / Workboat"}
        }
    }
}

SPEC_TEMPLATE = """# {name} ({length}) - {type}

## Design Overview
- **Designer:** Jeff Spira (Spira International)
- **Hull Category:** {category_title}
- **Construction Method:** Ply-on-frame (standard lumber yard timber & exterior/marine plywood)

## Specifications
- **Length Overall (LOA):** {length}
- **Beam:** *[Extracted from Study Plan / Archive Table]*
- **Draft:** *[Extracted from Study Plan]*
- **Dry Hull Weight:** *[Extracted from Study Plan]*
- **Max Recommended Power:** *[Extracted from Study Plan]*
- **Fuel Capacity:** *[Optional Tank Spec]*

## Scantlings & Construction Notes
- **Bottom Planking:** Plywood (typically 1/2" or double 3/8")
- **Side Planking:** Plywood (typically 3/8" or 1/4")
- **Frame Stock:** Douglas Fir, White Oak, or construction-grade Southern Yellow Pine
- **Fastenings:** Stainless steel screws / 3M 5200 adhesive bedding / Epoxy fillets

## Archival Documents in Repository
- `study-plan.pdf`: Study drawing with profile, plan, station layout, and displacement data.
- `construction-guide.pdf`: Step-by-step ply-on-frame framing schedule and notes (where available).
- `bill-of-materials.pdf`: Lumber yard materials takeoff schedule.

---
*Preserved for educational and historical purposes in memory of Jeff Spira.*
"""

def create_archive_structure(base_dir="archive"):
    os.makedirs(base_dir, exist_ok=True)
    os.makedirs(os.path.join(base_dir, "manuals-and-guides"), exist_ok=True)
    os.makedirs(os.path.join(base_dir, "technical-reports"), exist_ok=True)

    for cat_slug, cat_data in HULL_CATEGORIES.items():
        cat_dir = os.path.join(base_dir, "boats", cat_slug)
        os.makedirs(cat_dir, exist_ok=True)
        
        # Write Category README
        cat_readme = os.path.join(cat_dir, "README.md")
        with open(cat_readme, "w", encoding="utf-8") as f:
            f.write(f"# {cat_data['title']}\n\n{cat_data['description']}\n\n## Models in this Lineage\n")
            for model_slug, model_info in cat_data["models"].items():
                f.write(f"- [{model_info['name']} ({model_info['length']})](./{model_slug}/specs.md)\n")

        # Create Model Folders & specs.md
        for model_slug, model_info in cat_data["models"].items():
            model_dir = os.path.join(cat_dir, model_slug)
            os.makedirs(model_dir, exist_ok=True)
            specs_path = os.path.join(model_dir, "specs.md")
            if not os.path.exists(specs_path):
                content = SPEC_TEMPLATE.format(
                    name=model_info["name"],
                    length=model_info["length"],
                    type=model_info["type"],
                    category_title=cat_data["title"]
                )
                with open(specs_path, "w", encoding="utf-8") as f:
                    f.write(content)

    print(f"Archive directory structure initialized under '{base_dir}'.")

if __name__ == "__main__":
    create_archive_structure()
