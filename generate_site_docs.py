#!/usr/bin/env python3
"""
Generate Documentation & Interactive Static Site for Jeff Spira Boat Plans Preservation Archive.
Produces:
1. MkDocs Markdown documentation pages in `docs/`
2. Standalone, ultra-intuitive, interactive single-page application in `site/index.html`
"""

import os
import re
import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ARCHIVE_DIR = BASE_DIR / "archive"
DOCS_DIR = BASE_DIR / "docs"
SITE_DIR = BASE_DIR / "site"

DOCS_DIR.mkdir(exist_ok=True)
(DOCS_DIR / "boats").mkdir(exist_ok=True)
SITE_DIR.mkdir(exist_ok=True)

CATEGORIES = [
    {
        "id": "pacific-power-dories",
        "title": "Pacific Power Dories",
        "icon": "🌊",
        "doc": "boats/pacific-power-dories.md",
        "desc": "Spira's flagship flat-bottom ocean power dories designed for surf launching, immense payload capacity, shallow draft, and instant planing."
    },
    {
        "id": "carolina-dories",
        "title": "Carolina Dories",
        "icon": "🛶",
        "doc": "boats/carolina-dories.md",
        "desc": "Traditional East Coast high-sheer planing workboats and dories built for chop, coastal fishing, and beach retrieval."
    },
    {
        "id": "drift-boats-and-river",
        "title": "Drift Boats & River",
        "icon": "🎣",
        "doc": "boats/drift-boats.md",
        "desc": "Whitewater drift boats and McKenzie-style river craft engineered with extreme rocker for maneuvering rapids and rocky shallows."
    },
    {
        "id": "garveys-skiffs-and-utility",
        "title": "Garveys & Skiffs",
        "icon": "⛵",
        "doc": "boats/garveys-skiffs.md",
        "desc": "Blunt-bow garveys, flat-bottom skiffs, and fast bay utility craft maximizing interior volume and stability on a budget."
    },
    {
        "id": "cruisers-and-trawlers",
        "title": "Cruisers & Trawlers",
        "icon": "🛥️",
        "doc": "boats/cruisers-trawlers.md",
        "desc": "Pocket passage-makers, trawlers, and coastal cabin cruisers built on rugged ply-on-frame hulls for extended expeditions."
    }
]

def scan_archive():
    boats = []
    boats_base = ARCHIVE_DIR / "boats"
    
    cat_map = {c["id"]: c for c in CATEGORIES}
    
    for cat_dir in sorted(boats_base.iterdir()):
        if not cat_dir.is_dir():
            continue
        cat_id = cat_dir.name
        cat_meta = cat_map.get(cat_id, {
            "id": cat_id,
            "title": cat_id.replace("-", " ").title(),
            "icon": "⛵",
            "desc": ""
        })
        
        for model_dir in sorted(cat_dir.iterdir()):
            if not model_dir.is_dir():
                continue
            
            slug = model_dir.name
            parts = slug.split("-", 1)
            if len(parts) > 1 and parts[0].isdigit():
                length_ft = int(parts[0])
                length_str = f"{length_ft}'"
                raw_name = parts[1].replace("-", " ").title()
            else:
                length_ft = 0
                length_str = ""
                raw_name = slug.replace("-", " ").title()
                
            files = []
            study_plan = None
            metric_study_plan = None
            bom = None
            const_guide = None
            
            for f in sorted(model_dir.iterdir()):
                if f.name == "specs.md" or not f.is_file():
                    continue
                size_kb = f.stat().st_size / 1024
                size_str = f"{size_kb / 1024:.1f} MB" if size_kb > 1024 else f"{size_kb:.0f} KB"
                file_info = {
                    "filename": f.name,
                    "rel_path": f"archive/boats/{cat_id}/{slug}/{f.name}",
                    "size_str": size_str,
                    "size_kb": size_kb
                }
                files.append(file_info)
                
                fn_lower = f.name.lower()
                if "metric" in fn_lower and "study" in fn_lower:
                    metric_study_plan = file_info
                elif "study" in fn_lower and not study_plan:
                    study_plan = file_info
                elif "bom" in fn_lower or "bill" in fn_lower:
                    bom = file_info
                elif "const" in fn_lower:
                    const_guide = file_info
            
            description = f"Rugged {length_str} {cat_meta['title']} design by Jeff Spira using standard ply-on-frame lumber and exterior/marine plywood."
            
            boats.append({
                "id": slug,
                "name": raw_name,
                "full_name": f"{length_str} {raw_name}".strip(),
                "length_ft": length_ft,
                "length_str": length_str,
                "category_id": cat_id,
                "category_title": cat_meta["title"],
                "category_icon": cat_meta.get("icon", "⛵"),
                "description": description,
                "hull_type": "Ply-on-Frame",
                "folder": f"archive/boats/{cat_id}/{slug}",
                "study_plan": study_plan,
                "metric_study_plan": metric_study_plan,
                "bom": bom,
                "const_guide": const_guide,
                "files": files
            })
            
    return boats

def scan_reports():
    reports = []
    tech_dir = ARCHIVE_DIR / "technical-reports"
    meta = {
        "BR-001": {
            "title": "Registering Your Homebuilt Boat",
            "desc": "Legal, Coast Guard, and state registration procedures for amateur-built vessels."
        },
        "BR-002": {
            "title": "Outboard Power for Homebuilt Boats",
            "desc": "Horsepower calculation formulas, transom loading, weight ratings, and fuel efficiency."
        },
        "BR-003": {
            "title": "Homebuilt Boat Seaworthiness",
            "desc": "Hydrodynamic stability, reserve buoyancy in surf, and cockpit self-bailing design."
        },
        "BR-004": {
            "title": "Scarfing Lumber for Boat Building",
            "desc": "Step-by-step techniques for 8:1 scarf beveling of long longitudinal framing stringers."
        },
        "BR-005": {
            "title": "Steam Bending Boat Framing",
            "desc": "Constructing steam boxes and bending hardwood framing without splitting."
        },
        "BR-006": {
            "title": "Scarfing Plywood Panels",
            "desc": "Methods for joining standard 4x8 plywood sheets into continuous seamless hull sides."
        }
    }
    
    if tech_dir.exists():
        for f in sorted(tech_dir.iterdir()):
            if not f.is_file():
                continue
            size_kb = f.stat().st_size / 1024
            size_str = f"{size_kb / 1024:.1f} MB" if size_kb > 1024 else f"{size_kb:.0f} KB"
            code = "Report"
            for k in meta:
                if k in f.name:
                    code = k
                    break
            m = meta.get(code, {
                "title": f.stem.replace("_", " "),
                "desc": "Engineering technical report by Jeff Spira."
            })
            reports.append({
                "code": code,
                "filename": f.name,
                "title": m["title"],
                "desc": m["desc"],
                "rel_path": f"archive/technical-reports/{f.name}",
                "size_str": size_str
            })
    return reports

def scan_manuals():
    manuals = []
    man_dir = ARCHIVE_DIR / "manuals-and-guides"
    if man_dir.exists():
        for f in sorted(man_dir.iterdir()):
            if not f.is_file():
                continue
            size_kb = f.stat().st_size / 1024
            size_str = f"{size_kb / 1024:.1f} MB" if size_kb > 1024 else f"{size_kb:.0f} KB"
            clean_title = f.stem.replace("_", " ").replace("ebook", "").strip().title()
            manuals.append({
                "filename": f.name,
                "title": clean_title,
                "rel_path": f"archive/manuals-and-guides/{f.name}",
                "size_str": size_str
            })
    return manuals

def build_interactive_html(boats, reports, manuals):
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jeff Spira Boat Plans Preservation Archive</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #090e17;
            --surface: #111a2e;
            --surface-hover: #16223b;
            --surface-card: #0f172a;
            --border: #1e2e4a;
            --border-highlight: #38bdf8;
            --primary: #0284c7;
            --primary-glow: rgba(2, 132, 199, 0.25);
            --accent: #38bdf8;
            --text: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            --tag-bg: #1e293b;
            --tag-text: #38bdf8;
            --success: #10b981;
            --success-bg: rgba(16, 185, 129, 0.15);
            --radius-sm: 6px;
            --radius-md: 10px;
            --radius-lg: 16px;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.5;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }}

        /* Header */
        header {{
            background: rgba(9, 14, 23, 0.9);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 100;
            padding: 0.85rem 2rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}

        .brand {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            text-decoration: none;
            color: #fff;
            font-weight: 700;
            font-size: 1.15rem;
        }}

        .brand-icon {{
            font-size: 1.5rem;
            background: linear-gradient(135deg, var(--primary), var(--accent));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .nav-links {{
            display: flex;
            gap: 1rem;
            align-items: center;
        }}

        .nav-link {{
            color: var(--text-muted);
            text-decoration: none;
            font-size: 0.9rem;
            font-weight: 500;
            padding: 0.4rem 0.8rem;
            border-radius: var(--radius-sm);
            transition: all 0.2s;
            cursor: pointer;
        }}

        .nav-link:hover, .nav-link.active {{
            color: #fff;
            background: var(--surface-hover);
        }}

        .btn-github {{
            background: #1f2937;
            color: #fff;
            padding: 0.45rem 1rem;
            border-radius: var(--radius-sm);
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 600;
            border: 1px solid var(--border);
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            transition: all 0.2s;
        }}

        .btn-github:hover {{
            background: #374151;
            border-color: var(--accent);
        }}

        /* Hero */
        .hero {{
            background: linear-gradient(180deg, rgba(2, 132, 199, 0.08) 0%, transparent 100%);
            padding: 3rem 1.5rem 2rem 1.5rem;
            text-align: center;
            border-bottom: 1px solid var(--border);
        }}

        .hero h1 {{
            font-size: 2.25rem;
            font-weight: 800;
            letter-spacing: -0.025em;
            margin-bottom: 0.75rem;
            background: linear-gradient(135deg, #ffffff 40%, var(--accent) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .hero p {{
            color: var(--text-muted);
            font-size: 1.05rem;
            max-width: 820px;
            margin: 0 auto 1.5rem auto;
            line-height: 1.6;
        }}

        /* Stats bar */
        .stats-bar {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
            margin-bottom: 1.5rem;
        }}

        .stat-item {{
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 0.5rem 1.25rem;
            border-radius: var(--radius-md);
            font-size: 0.875rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .stat-num {{
            font-weight: 700;
            color: var(--accent);
            font-family: 'JetBrains Mono', monospace;
        }}

        /* Search & Filter Toolbar */
        .toolbar {{
            max-width: 1280px;
            margin: -1.25rem auto 1.5rem auto;
            padding: 0 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            position: sticky;
            top: 60px;
            z-index: 90;
        }}

        .search-container {{
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: var(--radius-lg);
            padding: 0.6rem 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }}

        .search-icon {{
            color: var(--text-dim);
            font-size: 1.25rem;
        }}

        .search-input {{
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: #fff;
            font-size: 1rem;
            font-family: inherit;
        }}

        .search-input::placeholder {{
            color: var(--text-dim);
        }}

        .filter-tabs {{
            display: flex;
            gap: 0.5rem;
            overflow-x: auto;
            padding: 0.25rem 0;
            scrollbar-width: none;
        }}

        .filter-tabs::-webkit-scrollbar {{
            display: none;
        }}

        .tab-btn {{
            background: var(--surface);
            color: var(--text-muted);
            border: 1px solid var(--border);
            padding: 0.45rem 0.9rem;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }}

        .tab-btn:hover {{
            background: var(--surface-hover);
            color: #fff;
            border-color: var(--accent);
        }}

        .tab-btn.active {{
            background: var(--primary);
            color: #fff;
            border-color: var(--accent);
            box-shadow: 0 0 12px var(--primary-glow);
        }}

        .tab-count {{
            background: rgba(0, 0, 0, 0.25);
            padding: 0.1rem 0.4rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-family: 'JetBrains Mono', monospace;
        }}

        /* Main Container */
        .container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 1rem 1.5rem 4rem 1.5rem;
            flex: 1;
            width: 100%;
        }}

        .section-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: 2rem 0 1.25rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border);
        }}

        .section-header h2 {{
            font-size: 1.4rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        /* Grid */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 1.25rem;
        }}

        /* Boat Card */
        .boat-card {{
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 0.85rem;
            transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
            position: relative;
        }}

        .boat-card:hover {{
            transform: translateY(-3px);
            border-color: var(--border-highlight);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.35);
        }}

        .card-top {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.75rem;
        }}

        .boat-title {{
            font-size: 1.2rem;
            font-weight: 700;
            color: #fff;
            line-height: 1.3;
        }}

        .badge-length {{
            background: var(--primary);
            color: #fff;
            font-size: 0.8rem;
            font-weight: 700;
            padding: 0.2rem 0.5rem;
            border-radius: var(--radius-sm);
            font-family: 'JetBrains Mono', monospace;
            white-space: nowrap;
        }}

        .badge-category {{
            display: inline-block;
            background: var(--tag-bg);
            color: var(--tag-text);
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.2rem 0.5rem;
            border-radius: var(--radius-sm);
            width: fit-content;
        }}

        .boat-desc {{
            color: var(--text-muted);
            font-size: 0.875rem;
            line-height: 1.5;
            flex: 1;
        }}

        .downloads-box {{
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 0.75rem;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}

        .downloads-label {{
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-dim);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .btn-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
        }}

        .btn-dl {{
            background: var(--surface);
            color: #fff;
            border: 1px solid var(--border);
            padding: 0.35rem 0.65rem;
            border-radius: var(--radius-sm);
            font-size: 0.8rem;
            font-weight: 600;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            transition: all 0.15s;
        }}

        .btn-dl:hover {{
            background: var(--primary);
            border-color: var(--accent);
            color: #fff;
        }}

        .btn-dl.primary-dl {{
            background: var(--primary);
            border-color: var(--accent);
        }}

        .btn-dl.primary-dl:hover {{
            background: var(--accent);
            color: #000;
        }}

        .btn-all-files {{
            background: transparent;
            color: var(--text-dim);
            border: 1px dashed var(--border);
            padding: 0.35rem 0.65rem;
            border-radius: var(--radius-sm);
            font-size: 0.8rem;
            cursor: pointer;
            width: 100%;
            text-align: center;
            transition: all 0.2s;
        }}

        .btn-all-files:hover {{
            color: #fff;
            border-color: var(--accent);
            background: var(--surface-hover);
        }}

        /* Reports & Manuals styling */
        .doc-card {{
            background: var(--surface-card);
            border: 1px solid var(--border);
            border-radius: var(--radius-md);
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            gap: 0.75rem;
            transition: all 0.2s;
        }}

        .doc-card:hover {{
            border-color: var(--border-highlight);
            transform: translateY(-2px);
        }}

        .doc-code {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 700;
            color: var(--accent);
            font-size: 0.85rem;
        }}

        .doc-title {{
            font-size: 1.05rem;
            font-weight: 700;
            color: #fff;
        }}

        .doc-desc {{
            color: var(--text-muted);
            font-size: 0.85rem;
            line-height: 1.4;
        }}

        /* Modal */
        .modal-backdrop {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(8px);
            z-index: 200;
            align-items: center;
            justify-content: center;
            padding: 1.5rem;
        }}

        .modal-backdrop.active {{
            display: flex;
        }}

        .modal-box {{
            background: var(--surface);
            border: 1px solid var(--border-highlight);
            border-radius: var(--radius-lg);
            max-width: 600px;
            width: 100%;
            max-height: 85vh;
            overflow-y: auto;
            padding: 1.75rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }}

        .modal-header {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.75rem;
        }}

        .modal-close {{
            background: transparent;
            border: none;
            color: var(--text-dim);
            font-size: 1.5rem;
            cursor: pointer;
            padding: 0 0.5rem;
            line-height: 1;
        }}

        .modal-close:hover {{
            color: #fff;
        }}

        .modal-file-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}

        .modal-file-item {{
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 0.6rem 0.8rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 0.875rem;
        }}

        /* Empty state */
        .empty-state {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 4rem 1rem;
            color: var(--text-dim);
        }}

        footer {{
            background: #060910;
            border-top: 1px solid var(--border);
            padding: 2.5rem 1.5rem;
            text-align: center;
            color: var(--text-dim);
            font-size: 0.875rem;
            margin-top: auto;
        }}

        footer a {{
            color: var(--accent);
            text-decoration: none;
        }}
    </style>
</head>
<body>
    <header>
        <a href="#" class="brand">
            <span class="brand-icon">⛵</span>
            <span>Spira Boat Plans Archive</span>
        </a>
        <nav class="nav-links">
            <a class="nav-link active" onclick="switchTab('all')">Boat Models</a>
            <a class="nav-link" onclick="switchTab('reports')">Technical Reports</a>
            <a class="nav-link" onclick="switchTab('manuals')">Manuals & Books</a>
            <a href="https://github.com/thecorcoran/Spira-Boats" target="_blank" class="btn-github">
                <span>⭐ GitHub Repo</span>
            </a>
        </nav>
    </header>

    <section class="hero">
        <h1>Jeff Spira Boat Plans Digital Preservation Archive</h1>
        <p>An open, searchable preservation library honoring the naval designs of Jeff Spira. Built to make over 170+ study plans, engineering reports, and construction guides easily accessible to builders worldwide.</p>
        
        <div class="stats-bar">
            <div class="stat-item">
                <span>⛵ Models:</span>
                <span class="stat-num">{len(boats)}</span>
            </div>
            <div class="stat-item">
                <span>📐 Technical Bulletins:</span>
                <span class="stat-num">{len(reports)}</span>
            </div>
            <div class="stat-item">
                <span>📖 Books & Guides:</span>
                <span class="stat-num">{len(manuals)}</span>
            </div>
            <div class="stat-item">
                <span>🔨 Construction:</span>
                <span class="stat-num">Ply-on-Frame</span>
            </div>
        </div>
    </section>

    <div class="toolbar">
        <div class="search-container">
            <span class="search-icon">🔍</span>
            <input type="text" id="searchInput" class="search-input" placeholder="Search by boat name, length, or category (e.g., Tillamook, 19', Albion, Carolina, Rogue)..." oninput="applyFilters()">
        </div>
        
        <div class="filter-tabs">
            <button class="tab-btn active" onclick="switchTab('all')" data-cat="all">
                <span>🌟 All Models</span>
                <span class="tab-count">{len(boats)}</span>
            </button>
            <button class="tab-btn" onclick="switchTab('pacific-power-dories')" data-cat="pacific-power-dories">
                <span>🌊 Pacific Dories</span>
                <span class="tab-count">{len([b for b in boats if b['category_id'] == 'pacific-power-dories'])}</span>
            </button>
            <button class="tab-btn" onclick="switchTab('carolina-dories')" data-cat="carolina-dories">
                <span>🛶 Carolina Dories</span>
                <span class="tab-count">{len([b for b in boats if b['category_id'] == 'carolina-dories'])}</span>
            </button>
            <button class="tab-btn" onclick="switchTab('drift-boats-and-river')" data-cat="drift-boats-and-river">
                <span>🎣 Drift & River</span>
                <span class="tab-count">{len([b for b in boats if b['category_id'] == 'drift-boats-and-river'])}</span>
            </button>
            <button class="tab-btn" onclick="switchTab('garveys-skiffs-and-utility')" data-cat="garveys-skiffs-and-utility">
                <span>⛵ Garveys & Skiffs</span>
                <span class="tab-count">{len([b for b in boats if b['category_id'] == 'garveys-skiffs-and-utility'])}</span>
            </button>
            <button class="tab-btn" onclick="switchTab('cruisers-and-trawlers')" data-cat="cruisers-and-trawlers">
                <span>🛥️ Cruisers & Trawlers</span>
                <span class="tab-count">{len([b for b in boats if b['category_id'] == 'cruisers-and-trawlers'])}</span>
            </button>
            <button class="tab-btn" onclick="switchTab('reports')" data-cat="reports">
                <span>📐 Tech Reports</span>
                <span class="tab-count">{len(reports)}</span>
            </button>
            <button class="tab-btn" onclick="switchTab('manuals')" data-cat="manuals">
                <span>📚 Manuals</span>
                <span class="tab-count">{len(manuals)}</span>
            </button>
        </div>
    </div>

    <main class="container">
        <!-- Boat Catalog Section -->
        <div id="boatsSection">
            <div class="section-header">
                <h2><span>⛵</span> <span id="sectionTitle">All Boat Models</span></h2>
                <span id="resultsCount" style="color: var(--text-dim); font-size: 0.9rem;">Showing {len(boats)} designs</span>
            </div>
            <div class="cards-grid" id="boatsGrid"></div>
        </div>

        <!-- Technical Reports Section -->
        <div id="reportsSection" style="margin-top: 3rem;">
            <div class="section-header">
                <h2><span>📐</span> <span>Engineering Technical Reports (BR-001 – BR-006)</span></h2>
            </div>
            <div class="cards-grid" id="reportsGrid"></div>
        </div>

        <!-- Manuals Section -->
        <div id="manualsSection" style="margin-top: 3rem;">
            <div class="section-header">
                <h2><span>📖</span> <span>Boatbuilding Manuals, Guides & Nautical Literature</span></h2>
            </div>
            <div class="cards-grid" id="manualsGrid"></div>
        </div>
    </main>

    <!-- Modal for viewing all files -->
    <div class="modal-backdrop" id="modalBackdrop" onclick="closeModal(event)">
        <div class="modal-box" onclick="event.stopPropagation()">
            <div class="modal-header">
                <div>
                    <h3 id="modalTitle" style="font-size: 1.25rem; color: #fff;">Boat Name</h3>
                    <p id="modalCategory" style="color: var(--accent); font-size: 0.85rem;">Category</p>
                </div>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div id="modalDesc" style="color: var(--text-muted); font-size: 0.9rem; line-height: 1.5;"></div>
            <div>
                <h4 style="font-size: 0.85rem; text-transform: uppercase; color: var(--text-dim); margin-bottom: 0.5rem;">All Available Plans & Documents</h4>
                <ul class="modal-file-list" id="modalFileList"></ul>
            </div>
        </div>
    </div>

    <footer>
        <p><strong>Jeff Spira Boat Plans Preservation Archive</strong> &bull; Non-Commercial Educational Archive</p>
        <p style="margin-top: 0.5rem;">Hosted and preserved on <a href="https://github.com/thecorcoran/Spira-Boats" target="_blank">GitHub</a> with automated Pages deployment.</p>
    </footer>

    <script>
        const BOATS = {json.dumps(boats)};
        const REPORTS = {json.dumps(reports)};
        const MANUALS = {json.dumps(manuals)};

        let currentCategory = 'all';

        function renderBoats(items) {{
            const grid = document.getElementById('boatsGrid');
            if (!items.length) {{
                grid.innerHTML = '<div class="empty-state"><h3>No boat models matched your search.</h3><p>Try searching for a different name or clear the search filter.</p></div>';
                document.getElementById('resultsCount').innerText = '0 designs';
                return;
            }}
            document.getElementById('resultsCount').innerText = `Showing ${{items.length}} design${{items.length === 1 ? '' : 's'}}`;
            
            grid.innerHTML = items.map(b => {{
                let dlButtons = [];
                if (b.study_plan) {{
                    dlButtons.push(`<a href="../${{b.study_plan.rel_path}}" download class="btn-dl primary-dl" title="Download Study Plan">📥 Study Plan</a>`);
                }}
                if (b.metric_study_plan) {{
                    dlButtons.push(`<a href="../${{b.metric_study_plan.rel_path}}" download class="btn-dl" title="Download Metric Study Plan">📐 Metric Plan</a>`);
                }}
                if (b.bom) {{
                    dlButtons.push(`<a href="../${{b.bom.rel_path}}" download class="btn-dl" title="Download Bill of Materials">📋 BOM</a>`);
                }}
                if (b.const_guide) {{
                    dlButtons.push(`<a href="../${{b.const_guide.rel_path}}" download class="btn-dl" title="Download Construction Guide">🔨 Guide</a>`);
                }}

                return `
                <div class="boat-card">
                    <div class="card-top">
                        <div>
                            <div class="badge-category">${{b.category_title}}</div>
                            <h3 class="boat-title" style="margin-top: 0.35rem;">${{b.full_name}}</h3>
                        </div>
                        ${{b.length_str ? `<span class="badge-length">${{b.length_str}}</span>` : ''}}
                    </div>
                    
                    <p class="boat-desc">${{b.description}}</p>

                    <div class="downloads-box">
                        <div class="downloads-label">Available Plans & Takeoffs (${{b.files.length}} files)</div>
                        <div class="btn-group">
                            ${{dlButtons.length ? dlButtons.join('') : '<span style=\"color: var(--text-dim); font-size: 0.8rem;\">Study plans in main collection</span>'}}
                        </div>
                        <button class="btn-all-files" onclick='openModal("${{b.id}}")'>📂 View All Specs & Files (${{b.files.length}})</button>
                    </div>
                </div>
                `;
            }}).join('');
        }}

        function renderReports() {{
            const grid = document.getElementById('reportsGrid');
            grid.innerHTML = REPORTS.map(r => `
                <div class="doc-card">
                    <div>
                        <div class="doc-code">${{r.code}}</div>
                        <h3 class="doc-title">${{r.title}}</h3>
                        <p class="doc-desc" style="margin-top: 0.35rem;">${{r.desc}}</p>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                        <span style="color: var(--text-dim); font-size: 0.8rem;">${{r.size_str}}</span>
                        <a href="../${{r.rel_path}}" download class="btn-dl primary-dl">📥 Download PDF</a>
                    </div>
                </div>
            `).join('');
        }}

        function renderManuals() {{
            const grid = document.getElementById('manualsGrid');
            grid.innerHTML = MANUALS.map(m => `
                <div class="doc-card">
                    <div>
                        <div class="doc-code">📘 Manual / Book</div>
                        <h3 class="doc-title">${{m.title}}</h3>
                        <p class="doc-desc" style="margin-top: 0.35rem;">${{m.filename}}</p>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 0.5rem;">
                        <span style="color: var(--text-dim); font-size: 0.8rem;">${{m.size_str}}</span>
                        <a href="../${{m.rel_path}}" download class="btn-dl primary-dl">📥 Download PDF</a>
                    </div>
                </div>
            `).join('');
        }}

        function switchTab(catId) {{
            currentCategory = catId;
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.toggle('active', btn.getAttribute('data-cat') === catId);
            }});
            
            const boatsSec = document.getElementById('boatsSection');
            const reportsSec = document.getElementById('reportsSection');
            const manualsSec = document.getElementById('manualsSection');

            if (catId === 'reports') {{
                boatsSec.style.display = 'none';
                reportsSec.style.display = 'block';
                manualsSec.style.display = 'none';
                reportsSec.scrollIntoView({{ behavior: 'smooth' }});
            }} else if (catId === 'manuals') {{
                boatsSec.style.display = 'none';
                reportsSec.style.display = 'none';
                manualsSec.style.display = 'block';
                manualsSec.scrollIntoView({{ behavior: 'smooth' }});
            }} else {{
                boatsSec.style.display = 'block';
                reportsSec.style.display = 'block';
                manualsSec.style.display = 'block';
                applyFilters();
            }}
        }}

        function applyFilters() {{
            const query = document.getElementById('searchInput').value.trim().toLowerCase();
            let filtered = BOATS;

            if (currentCategory !== 'all' && currentCategory !== 'reports' && currentCategory !== 'manuals') {{
                filtered = filtered.filter(b => b.category_id === currentCategory);
            }}

            if (query) {{
                filtered = filtered.filter(b => 
                    b.name.toLowerCase().includes(query) ||
                    b.full_name.toLowerCase().includes(query) ||
                    b.category_title.toLowerCase().includes(query) ||
                    b.description.toLowerCase().includes(query) ||
                    b.length_str.toLowerCase().includes(query)
                );
            }}

            renderBoats(filtered);
        }}

        function openModal(boatId) {{
            const boat = BOATS.find(b => b.id === boatId);
            if (!boat) return;

            document.getElementById('modalTitle').innerText = boat.full_name;
            document.getElementById('modalCategory').innerText = boat.category_title;
            document.getElementById('modalDesc').innerText = boat.description;

            const list = document.getElementById('modalFileList');
            if (!boat.files.length) {{
                list.innerHTML = '<li style="color: var(--text-dim); padding: 1rem 0;">No individual loose files attached. Referenced in core study sheets.</li>';
            }} else {{
                list.innerHTML = boat.files.map(f => `
                    <li class="modal-file-item">
                        <div>
                            <strong>${{f.filename}}</strong>
                            <span style="color: var(--text-dim); font-size: 0.75rem; margin-left: 0.5rem;">(${{f.size_str}})</span>
                        </div>
                        <a href="../${{f.rel_path}}" download class="btn-dl primary-dl">📥 Download</a>
                    </li>
                `).join('');
            }}

            document.getElementById('modalBackdrop').classList.add('active');
        }}

        function closeModal(e) {{
            document.getElementById('modalBackdrop').classList.remove('active');
        }}

        // Initialize
        renderBoats(BOATS);
        renderReports();
        renderManuals();
    </script>
</body>
</html>
"""
    (SITE_DIR / "index.html").write_text(html_content, encoding="utf-8")
    print(f"✓ Standalone interactive site generated at {SITE_DIR / 'index.html'}")

def generate_mkdocs_pages(boats, reports, manuals):
    print("--> Generating MkDocs markdown pages in docs/...")
    
    # 1. Main index
    index_md = f"""# Jeff Spira Boat Plans Preservation Archive

Welcome to the digital preservation archive for the naval designs of **Jeff Spira** (*Spira International*).

Jeff Spira was an aerospace engineer, naval designer, and educator who dedicated decades to democratizing wooden boatbuilding. His accessible **ply-on-frame** construction method enabled thousands of amateur builders worldwide to construct rugged, seaworthy craft in garages and backyards using standard lumber yard materials and basic hand tools.

---

## 🧭 Design Collections ({len(boats)} Models Cataloged)

| Category | Models | Description |
| :--- | :--- | :--- |
| [**Pacific Power Dories**](boats/pacific-power-dories.md) | {len([b for b in boats if b['category_id'] == 'pacific-power-dories'])} Designs | Flat-bottom surf dories, heavy load haulers, and offshore planing dories. |
| [**Carolina Dories**](boats/carolina-dories.md) | {len([b for b in boats if b['category_id'] == 'carolina-dories'])} Designs | High-sheer Carolina coast workboats for choppy sounds and bays. |
| [**Drift Boats & River**](boats/drift-boats.md) | {len([b for b in boats if b['category_id'] == 'drift-boats-and-river'])} Designs | Rockered whitewater drift boats and river dories. |
| [**Garveys & Skiffs**](boats/garveys-skiffs.md) | {len([b for b in boats if b['category_id'] == 'garveys-skiffs-and-utility'])} Designs | Plywood garveys, micro-skiffs, and bay utility craft. |
| [**Cruisers & Trawlers**](boats/cruisers-trawlers.md) | {len([b for b in boats if b['category_id'] == 'cruisers-and-trawlers'])} Designs | Rugged cabin cruisers, trawlers, and offshore camp-cruisers. |

---

## 📚 Technical Manuals & Guides

- 📖 [**Core Manuals & Building Guides**](manuals.md) - Free textbooks including *Ply-on-Frame Boatbuilding*, *Stitch-and-Glue Construction*, and *Homebuilt Sea Kayak*.
- 📐 [**Engineering Technical Reports (BR-001 - BR-006)**](technical-reports.md) - Official Spira engineering bulletins on scarfing, steam bending, outboard powering, and hull seaworthiness.
- 💡 [**Design Philosophy & Scantlings**](philosophy.md) - Why Spira designed flat-bottom reserve buoyancy hulls and simplified framing schedules.

---

## ⚖️ Preservation & Non-Commercial Notice
This archive is maintained as an educational, non-commercial memorial to Jeff Spira's contributions to the amateur wooden boatbuilding community. All study plans, reports, and manuals are preserved for historical, educational, and public research use.
"""
    (DOCS_DIR / "index.md").write_text(index_md, encoding="utf-8")

    # 2. Category Pages
    for cat in CATEGORIES:
        cat_id = cat["id"]
        cat_file = DOCS_DIR / cat["doc"]
        cat_boats = [b for b in boats if b["category_id"] == cat_id]
        
        md = f"# {cat['title']}\n\n"
        md += f"{cat['desc']}\n\n---\n\n"
        md += f"## Models ({len(cat_boats)} Designs)\n\n"
        
        for b in cat_boats:
            md += f"### {b['full_name']}\n\n"
            md += f"{b['description']}\n\n"
            md += f"- **Hull Type:** {b['hull_type']}\n"
            if b['length_str']:
                md += f"- **Length Overall:** {b['length_str']}\n"
            
            if b['files']:
                md += "\n**Archived Documents & Study Plans:**\n\n"
                for f in b['files']:
                    md += f"- 📄 [`{f['filename']}`](../{f['rel_path']}) ({f['size_str']})\n"
            md += "\n---\n\n"
            
        cat_file.write_text(md, encoding="utf-8")

    # 3. Technical Reports
    tech_md = """# Technical Reports & Engineering Bulletins

Jeff Spira authored a series of dedicated technical bulletins to guide builders through key woodworking, engineering, and hydrodynamic challenges.

---

## Bulletins List

| Report | Title | Subject & Content |
| :--- | :--- | :--- |
| **BR-001** | Registering Your Homebuilt Boat | Legal, Coast Guard, and state registration procedures for amateur-built vessels. |
| **BR-002** | Outboard Power for Homebuilt Boats | Calculating required horsepower, transom loading, and fuel efficiency. |
| **BR-003** | Homebuilt Boat Seaworthiness | Hydrodynamic principles, reserve buoyancy, center of gravity, and survivability in surf. |
| **BR-004** | Scarfing Lumber for Boat Building | Step-by-step techniques for 8:1 scarf beveling of long longitudinal framing stringers. |
| **BR-005** | Steam Bending Boat Framing | Steam box construction, timber species selection, and bending chine logs. |
| **BR-006** | Scarfing Plywood Panels | Joining standard 4x8 plywood sheets into continuous seamless hull skin panels. |

---

## Archived Technical Bulletins

"""
    for r in reports:
        tech_md += f"- 📄 [**`{r['filename']}`**](../{r['rel_path']}) ({r['size_str']}) — *{r['title']}*\n"
    (DOCS_DIR / "technical-reports.md").write_text(tech_md, encoding="utf-8")

    # 4. Manuals
    man_md = """# Boatbuilding Manuals & Construction Guides

These guides provide comprehensive instructions covering the complete construction lifecycle—from lofting and frame setup through planking, fiberglass taping, fairing, and rigging.

---

## Archived Manuals & Classic Boating Books

"""
    for m in manuals:
        man_md += f"- 📘 [**`{m['filename']}`**](../{m['rel_path']}) ({m['size_str']})\n"
    (DOCS_DIR / "manuals.md").write_text(man_md, encoding="utf-8")

    print("✓ All Markdown pages generated in docs/")

def main():
    print("=== Generating Jeff Spira Preservation Archive Documentation & Static Site ===")
    boats = scan_archive()
    reports = scan_reports()
    manuals = scan_manuals()
    print(f"Discovered: {len(boats)} boats, {len(reports)} technical reports, {len(manuals)} manuals/books.")
    
    build_interactive_html(boats, reports, manuals)
    generate_mkdocs_pages(boats, reports, manuals)
    print("=== Site Generation Completed Successfully ===")

if __name__ == "__main__":
    main()
