#!/usr/bin/env python3
"""
Generate Documentation & Static Site for Spira Boat Plans Preservation Archive.
Produces MkDocs-compatible Markdown docs in `docs/` and a standalone static HTML website in `site/`.
"""

import os
import re
import json
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
        "doc": "boats/pacific-power-dories.md",
        "desc": "Spira's flagship flat-bottom ocean power dories designed for surf launching, immense payload capacity, and shallow water capability."
    },
    {
        "id": "carolina-dories",
        "title": "Carolina Dories",
        "doc": "boats/carolina-dories.md",
        "desc": "Traditional East Coast high-sheer planing workboats and dories built for chop, coastal fishing, and beach retrieval."
    },
    {
        "id": "drift-boats-and-river",
        "title": "Drift Boats & River Dories",
        "doc": "boats/drift-boats.md",
        "desc": "Whitewater drift boats and McKenzie-style river craft engineered with extreme rocker for maneuvering rapids and rocky shallows."
    },
    {
        "id": "garveys-skiffs-and-utility",
        "title": "Garveys, Skiffs & Utility Boats",
        "doc": "boats/garveys-skiffs.md",
        "desc": "Blunt-bow garveys, flat-bottom skiffs, and fast bay utility craft maximizing interior volume and stability on a budget."
    },
    {
        "id": "cruisers-and-trawlers",
        "title": "Cruisers & Pocket Trawlers",
        "doc": "boats/cruisers-trawlers.md",
        "desc": "Pocket passage-makers and coastal cabin cruisers built on rugged ply-on-frame hulls for extended expeditions."
    }
]

def parse_specs_md(filepath):
    """Extract key fields and body from a specs.md file."""
    if not filepath.exists():
        return {}
    content = filepath.read_text(encoding="utf-8")
    data = {"raw": content}
    for line in content.splitlines():
        if line.startswith("# "):
            data["title"] = line.replace("#", "").strip()
        elif line.startswith("- **Length (LOA)**:"):
            data["loa"] = line.split(":", 1)[1].strip()
        elif line.startswith("- **Beam**:"):
            data["beam"] = line.split(":", 1)[1].strip()
        elif line.startswith("- **Hull Type**:"):
            data["hull"] = line.split(":", 1)[1].strip()
        elif line.startswith("- **Recommended Power**:"):
            data["power"] = line.split(":", 1)[1].strip()
        elif line.startswith("- **Displacement / Payload**:"):
            data["payload"] = line.split(":", 1)[1].strip()
    return data

def build_docs():
    print("--> Generating Markdown documentation in docs/...")
    
    # 1. Index Page
    index_md = f"""# Jeff Spira Boat Plans Preservation Archive

Welcome to the digital preservation archive and open documentation site for the boat designs of **Jeff Spira** (*Spira International*).

Jeff Spira was an aerospace engineer, naval designer, and educator who dedicated decades to democratizing wooden boatbuilding. His accessible **ply-on-frame** construction method enabled thousands of amateur builders worldwide to construct rugged, seaworthy craft in garages and backyards using standard lumber yard materials and basic hand tools.

---

## 🧭 Design Collections

| Hull Category | Designs | Description |
| :--- | :--- | :--- |
| [**Pacific Power Dories**](boats/pacific-power-dories.md) | 15' Seneca to 32' Kodiak | Flat-bottom surf dories, heavy load haulers, and offshore planing dories. |
| [**Carolina Dories**](boats/carolina-dories.md) | 16' Oysterman to 22' Carolina Dory | High-sheer Carolina coast workboats for choppy sounds and bays. |
| [**Drift Boats & River**](boats/drift-boats.md) | 14' Rogue River, 16' Mackenzie | Rockered whitewater drift boats and river dories. |
| [**Garveys & Skiffs**](boats/garveys-skiffs.md) | 8' Huntington to 20' San Pedro | Plywood garveys, micro-skiffs, and bay utility craft. |
| [**Cruisers & Trawlers**](boats/cruisers-trawlers.md) | 20' Key Largo to 26' Alaskan | Rugged cabin cruisers, trawlers, and offshore camp-cruisers. |

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
        cat_dir = ARCHIVE_DIR / "boats" / cat["id"]
        cat_file = DOCS_DIR / cat["doc"]
        
        md = f"# {cat['title']}\n\n"
        md += f"{cat['desc']}\n\n---\n\n"
        md += "## Boat Models in this Category\n\n"
        
        if cat_dir.exists():
            models = sorted([d for d in cat_dir.iterdir() if d.is_dir()])
            for model_dir in models:
                specs_file = model_dir / "specs.md"
                specs = parse_specs_md(specs_file)
                title = specs.get("title", model_dir.name.replace("-", " ").title())
                
                md += f"### {title}\n\n"
                if specs:
                    md += f"- **Length Overall (LOA)**: {specs.get('loa', 'N/A')}\n"
                    md += f"- **Beam**: {specs.get('beam', 'N/A')}\n"
                    md += f"- **Hull Form**: {specs.get('hull', 'Ply-on-Frame')}\n"
                    md += f"- **Recommended Power**: {specs.get('power', 'N/A')}\n"
                    md += f"- **Displacement / Payload**: {specs.get('payload', 'N/A')}\n\n"
                
                # List files
                files = [f for f in sorted(model_dir.iterdir()) if f.name != "specs.md"]
                if files:
                    md += "**Archived Documents & Plans:**\n\n"
                    for f in files:
                        size_kb = f.stat().st_size / 1024
                        md += f"- 📄 `{f.name}` ({size_kb:.1f} KB)\n"
                    md += "\n"
                md += "---\n\n"
                
        cat_file.write_text(md, encoding="utf-8")

    # 3. Technical Reports Page
    tech_dir = ARCHIVE_DIR / "technical-reports"
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

## Archived Technical Documents

"""
    if tech_dir.exists():
        for f in sorted(tech_dir.iterdir()):
            if f.is_file():
                size_kb = f.stat().st_size / 1024
                tech_md += f"- 📄 **`{f.name}`** ({size_kb:.1f} KB)\n"
    (DOCS_DIR / "technical-reports.md").write_text(tech_md, encoding="utf-8")

    # 4. Manuals Page
    man_dir = ARCHIVE_DIR / "manuals-and-guides"
    man_md = """# Boatbuilding Manuals & Construction Guides

These guides provide comprehensive, illustrated instructions covering the complete construction lifecycle—from lofting and frame setup through planking, fiberglass taping, fairing, and rigging.

---

## Core Publications

1. **Illustrated Guide to Building a Spira International Ply-on-Frame Boat**  
   The definitive handbook explaining Spira's signature ply-on-frame methodology, fastener schedules, epoxy fillets, and frame assembly.
   
2. **How to Build an Easy Homebuilt Sea Kayak**  
   A lightweight, accessible stitch-and-and-glue and woodstrip kayak manual for first-time builders.

3. **US Coast Guard Backyard Boatbuilder Safety Manual**  
   Coast Guard standards for floatation foam, electrical wiring, ventilation, and load capacity plates.

---

## Archived Manuals

"""
    if man_dir.exists():
        for f in sorted(man_dir.iterdir()):
            if f.is_file():
                size_kb = f.stat().st_size / 1024
                man_md += f"- 📘 **`{f.name}`** ({size_kb:.1f} KB)\n"
    (DOCS_DIR / "manuals.md").write_text(man_md, encoding="utf-8")

    # 5. Philosophy Page
    phil_md = """# Jeff Spira's Design Philosophy

> *"A boat builder should spend more time using their boat than building it."* — Jeff Spira

### 1. Ply-on-Frame vs. Complex Compound Curves
Spira championed framing boats with dimensional softwood lumber (Douglas Fir, Southern Yellow Pine, White Oak) wrapped in exterior/marine plywood skins. Unlike round-bilge designs that require laborious strip-planking or temporary mold lofting, ply-on-frame uses structural bulkheads as permanent frames, significantly accelerating build time.

### 2. The Pacific Power Dory Principle: Flat Bottoms & Reserve Buoyancy
Traditional naval architecture often defaults to deep-V entries for smooth chop penetration. Spira argued persuasively for flat-bottom and modified-V dory hulls:
- **Instant Planing**: Planes with minimal horsepower (a 19' Albion runs effortlessly on a 25–40 HP outboard).
- **Extreme Shallow Draft**: Floats in 4–6 inches of water, allowing beach launches and navigating tidal flats.
- **Surf Launching Safety**: Flared dory sides provide exponential reserve buoyancy when heeling or encountering breaking breakers.

### 3. Accessible, Budget-Conscious Materials
Spira designed around materials accessible from local retail lumber yards (standard ACX exterior plywood, 2x4 and 2x6 Douglas Fir, 316 stainless/hot-dipped galvanized fasteners, and modern epoxy resins).
"""
    (DOCS_DIR / "philosophy.md").write_text(phil_md, encoding="utf-8")

    print("✓ All Markdown pages generated in docs/")

def build_standalone_html():
    print("--> Generating standalone static website in site/...")
    
    css = """
    :root {
        --primary: #0284c7;
        --primary-dark: #0369a1;
        --bg: #0f172a;
        --card-bg: #1e293b;
        --text: #f1f5f9;
        --text-muted: #94a3b8;
        --border: #334155;
        --accent: #38bdf8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background: var(--bg);
        color: var(--text);
        line-height: 1.6;
    }
    header {
        background: #090d16;
        border-bottom: 1px solid var(--border);
        padding: 1.25rem 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .logo { font-size: 1.35rem; font-weight: 700; color: var(--accent); display: flex; align-items: center; gap: 0.5rem; text-decoration: none; }
    .nav-links { display: flex; gap: 1.5rem; }
    .nav-links a { color: var(--text-muted); text-decoration: none; font-weight: 500; transition: color 0.2s; }
    .nav-links a:hover, .nav-links a.active { color: var(--accent); }
    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
    .hero {
        text-align: center;
        padding: 3rem 1rem;
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        margin-bottom: 2.5rem;
        border: 1px solid var(--border);
    }
    .hero h1 { font-size: 2.5rem; margin-bottom: 0.75rem; color: #fff; }
    .hero p { font-size: 1.15rem; color: var(--text-muted); max-width: 800px; margin: 0 auto; }
    .search-box {
        margin-top: 1.5rem;
        display: flex;
        justify-content: center;
    }
    .search-box input {
        width: 100%;
        max-width: 500px;
        padding: 0.75rem 1.25rem;
        border-radius: 8px;
        border: 1px solid var(--border);
        background: #090d16;
        color: #fff;
        font-size: 1rem;
        outline: none;
    }
    .search-box input:focus { border-color: var(--accent); }
    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
        gap: 1.5rem;
        margin-top: 1.5rem;
    }
    .card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.5rem;
        transition: transform 0.2s, border-color 0.2s;
    }
    .card:hover { transform: translateY(-3px); border-color: var(--accent); }
    .card h3 { color: var(--accent); font-size: 1.25rem; margin-bottom: 0.5rem; }
    .card p { color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1rem; }
    .specs-list { list-style: none; margin-bottom: 1rem; font-size: 0.9rem; }
    .specs-list li { margin-bottom: 0.35rem; color: #cbd5e1; }
    .specs-list strong { color: #fff; }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        background: #0369a1;
        color: #fff;
        font-size: 0.75rem;
        border-radius: 4px;
        margin-bottom: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .btn {
        display: inline-block;
        background: var(--primary);
        color: #fff;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        text-decoration: none;
        font-size: 0.875rem;
        font-weight: 600;
        transition: background 0.2s;
    }
    .btn:hover { background: var(--primary-dark); }
    .section-title { font-size: 1.75rem; margin-bottom: 1rem; border-bottom: 2px solid var(--border); padding-bottom: 0.5rem; }
    footer { text-align: center; padding: 2rem; color: var(--text-muted); font-size: 0.875rem; border-top: 1px solid var(--border); margin-top: 4rem; }
    """
    
    # Collect all boat models
    all_models = []
    for cat in CATEGORIES:
        cat_dir = ARCHIVE_DIR / "boats" / cat["id"]
        if cat_dir.exists():
            for m in sorted(cat_dir.iterdir()):
                if m.is_dir():
                    specs = parse_specs_md(m / "specs.md")
                    files = [f.name for f in m.iterdir() if f.is_file() and f.name != "specs.md"]
                    all_models.append({
                        "category": cat["title"],
                        "category_id": cat["id"],
                        "name": specs.get("title", m.name.replace("-", " ").title()),
                        "folder": m.name,
                        "loa": specs.get("loa", "N/A"),
                        "beam": specs.get("beam", "N/A"),
                        "hull": specs.get("hull", "Ply-on-Frame"),
                        "power": specs.get("power", "N/A"),
                        "payload": specs.get("payload", "N/A"),
                        "files": files
                    })
                    
    models_json = json.dumps(all_models)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jeff Spira Boat Plans Preservation Archive</title>
    <style>{css}</style>
</head>
<body>
    <header>
        <a href="#" class="logo">⛵ Spira Boat Plans Archive</a>
        <nav class="nav-links">
            <a href="#models" class="active">Boat Models</a>
            <a href="#reports">Technical Reports</a>
            <a href="#manuals">Manuals & Guides</a>
            <a href="https://github.com" target="_blank">GitHub</a>
        </nav>
    </header>

    <div class="container">
        <div class="hero">
            <h1>Jeff Spira Boat Plans Archive</h1>
            <p>An open digital preservation library honoring naval designer Jeff Spira. Containing 170+ study plans, construction manuals, engineering technical reports, and bills of materials for home boatbuilders.</p>
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search by model name (e.g. Albion, Tillamook, Seneca, Rogue)..." onkeyup="filterCards()">
            </div>
        </div>

        <h2 id="models" class="section-title">Design Catalog ({len(all_models)} Models)</h2>
        <div class="grid" id="boatGrid"></div>

        <h2 id="reports" class="section-title" style="margin-top: 3rem;">Engineering Technical Reports</h2>
        <div class="grid">
            <div class="card">
                <div class="badge">BR-001</div>
                <h3>Registering Your Homebuilt Boat</h3>
                <p>Official legal and Coast Guard procedures for registering and obtaining Hull Identification Numbers (HIN).</p>
            </div>
            <div class="card">
                <div class="badge">BR-002</div>
                <h3>Outboard Power for Homebuilt Boats</h3>
                <p>Horsepower calculation formulas, transom weight ratings, and fuel consumption considerations.</p>
            </div>
            <div class="card">
                <div class="badge">BR-003</div>
                <h3>Homebuilt Boat Seaworthiness</h3>
                <p>Principles of dynamic stability, reserve buoyancy in surf, and cockpit self-bailing design.</p>
            </div>
            <div class="card">
                <div class="badge">BR-004</div>
                <h3>Scarfing Lumber for Boat Building</h3>
                <p>Detailed guide on scarfing long dimensional timber framing and chine stringers (8:1 bevels).</p>
            </div>
            <div class="card">
                <div class="badge">BR-005</div>
                <h3>Steam Bending Framing</h3>
                <p>Constructing steam boxes and bending hardwood frames without splitting or deformation.</p>
            </div>
            <div class="card">
                <div class="badge">BR-006</div>
                <h3>Scarfing Plywood Panels</h3>
                <p>Step-by-step methods for scarfing 4x8 plywood sheets into continuous full-length boat sides and bottoms.</p>
            </div>
        </div>

        <h2 id="manuals" class="section-title" style="margin-top: 3rem;">Building Manuals & Publications</h2>
        <div class="grid">
            <div class="card">
                <div class="badge">Textbook</div>
                <h3>Illustrated Guide to Ply-on-Frame Boatbuilding</h3>
                <p>Spira's complete illustrated handbook detailing frame construction, lofting, epoxy fillets, and sheathing.</p>
            </div>
            <div class="card">
                <div class="badge">Guide</div>
                <h3>How to Build an Easy Homebuilt Sea Kayak</h3>
                <p>A fast, accessible kayak construction guide for weekend woodworkers and first-time builders.</p>
            </div>
            <div class="card">
                <div class="badge">Standard</div>
                <h3>USCG Backyard Boatbuilder Safety Manual</h3>
                <p>Federal flotation, ventilation, and load capacity safety guidelines.</p>
            </div>
        </div>
    </div>

    <footer>
        <p>Jeff Spira Boat Plans Preservation Project &bull; Educational, Non-Commercial Memorial Archive</p>
    </footer>

    <script>
        const boats = {models_json};
        const grid = document.getElementById('boatGrid');

        function renderBoats(items) {{
            grid.innerHTML = items.map(b => `
                <div class="card">
                    <div class="badge">${{b.category}}</div>
                    <h3>${{b.name}}</h3>
                    <ul class="specs-list">
                        <li><strong>LOA:</strong> ${{b.loa}}</li>
                        <li><strong>Beam:</strong> ${{b.beam}}</li>
                        <li><strong>Hull:</strong> ${{b.hull}}</li>
                        <li><strong>Power:</strong> ${{b.power}}</li>
                        <li><strong>Payload:</strong> ${{b.payload}}</li>
                    </ul>
                    <div style="font-size: 0.8rem; color: #94a3b8; margin-top: 0.5rem;">
                        📁 ${{b.files.length}} plan/document file(s) cataloged
                    </div>
                </div>
            `).join('');
        }}

        function filterCards() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            const filtered = boats.filter(b => 
                b.name.toLowerCase().includes(query) || 
                b.category.toLowerCase().includes(query) ||
                b.hull.toLowerCase().includes(query)
            );
            renderBoats(filtered);
        }}

        renderBoats(boats);
    </script>
</body>
</html>
"""
    (SITE_DIR / "index.html").write_text(html, encoding="utf-8")
    print(f"✓ Standalone interactive site generated at site/index.html with {len(all_models)} models!")

if __name__ == "__main__":
    build_docs()
    build_standalone_html()
