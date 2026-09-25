# Jeff Spira International Boat Design Digital Archive

An open archival, preservation, and classification project dedicated to the boat designs, ply-on-frame manuals, and study plans of **Jeff Spira** (Spira International).

---

## 🎯 Archival Purpose & Memorial Context
Jeff Spira was an aeronautical engineer and boat designer who championed accessible amateur boatbuilding, especially ply-on-frame construction, Pacific power dories, Carolina dories, and river drift boats. Following his passing, many of his original digital web assets, study plans, and guides are at risk of link rot.

This repository provides:
1. **Automated Wayback CDX Ingestion Pipeline**: Tools to query the Internet Archive CDX API for `spirainternational.com`, discover captures, and safely download plans, BOMs, and guides.
2. **Standardized Hull Classification Schema**: An organized folder structure for each design category with markdown spec plates (`specs.md`), drawings, and PDFs.
3. **Publishing & Long-Term Preservation**: Formats ready for static hosting via GitHub Pages, MkDocs, or direct archival upload to the Internet Archive.

---

## 📂 Repository Structure

```
spira-archive/
├── archive_manager.py           # Master CLI runner for pipeline tasks
├── fetch_manifest.py            # Generates categorized Wayback manifests (CDX API)
├── download_assets.py           # Rate-limited, verified file downloader
├── organize_archive.py          # Initializes folder taxonomy and specs.md templates
├── sync_and_route.py            # Auto-sorts downloaded PDFs into model folders
├── manifests/                   # JSON manifests of all discovered captures
│   ├── study_plans.json         # (206 captured study plans)
│   ├── bills_of_materials.json  # (29 BOMs)
│   ├── technical_reports.json   # (21 technical reports: BR-001 to BR-006)
│   ├── manuals_and_guides.json  # (53 manuals & guides)
│   └── summary.json             # High-level capture counts
├── raw_downloads/               # Ingested PDF/image staging directory
└── archive/                     # Structured catalog ready for distribution
    ├── manuals-and-guides/      # Core ply-on-frame guides, kayak manuals
    ├── technical-reports/       # Scarfing, steam bending, seaworthiness reports
    └── boats/
        ├── pacific-power-dories/
        │   ├── 15-seneca/
        │   ├── 17-tillamook/
        │   ├── 19-albion/
        │   ├── 23-winchester/
        │   ├── 27-sitka/
        │   └── 32-kodiak/
        ├── carolina-dories/
        │   ├── 16-oysterman/
        │   ├── 19-carolinian/
        │   └── 20-hatteras/
        ├── drift-boats-and-river/
        │   ├── 14-rogue-river/
        │   └── 16-mackenzie/
        ├── garveys-skiffs-and-utility/
        │   ├── 08-huntington-harbor/
        │   ├── 14-mission-bay/
        │   └── 16-san-clemente/
        └── cruisers-and-trawlers/
            ├── 20-key-largo/
            ├── 21-chinook/
            └── 26-alaskan/
```

---

## 🚀 Quickstart Guide

### 1. Re-generate or Update Manifests
To query the Wayback CDX API and categorize all URLs:
```bash
python3 fetch_manifest.py
```

### 2. Download a Test Sample or Full Set
- **Quick Test (5 items per category):**
  ```bash
  python3 archive_manager.py download-quick --limit 5
  ```
- **Full Ingestion (All discovered study plans, manuals, reports, and BOMs):**
  ```bash
  python3 archive_manager.py download-all
  ```

### 3. Route Downloads into Catalog Folders
```bash
python3 sync_and_route.py
```

---

## 💡 Suggestions & Best Practices for Success

1. **Storage Management (GitHub vs Internet Archive)**:
   - Git repositories have soft limits (1 GB / 2 GB). PDFs can add up quickly.
   - **Recommended Approach**: Store the markdown catalog, specs, and lightweight images in GitHub. Create an Internet Archive Community Item (e.g. `spira-boat-plans-archive`) to store the complete raw PDF bundle, linking direct download buttons inside the `specs.md` plates.
2. **Community Sourcing for Full Construction Sets**:
   - The Wayback machine contains almost all *Study Plans*, *Technical Reports*, and *Bills of Materials*, but full multi-page blueprint offsets were often sold directly.
   - For missing full plans, post a call for contributions to `r/spiraboatplans` and *BoatDesign.net* referencing the missing items from `manifests/summary.json`.
3. **Static Catalog**:
   - Deploying using MkDocs Material or Hugo to GitHub Pages provides a mobile-friendly, searchable online boat catalog for builders worldwide.
