#!/usr/bin/env python3
"""
Spira Digital Archive - Master CLI Pipeline
Provides commands for manifest discovery, bulk asset downloading,
catalog routing, and site generation.
"""

import sys
import argparse
import subprocess
import os

def run_step(cmd_list, desc):
    print(f"\n==========================================")
    print(f"--> {desc}")
    print(f"==========================================")
    res = subprocess.run(cmd_list)
    if res.returncode != 0:
        print(f"Error during: {desc}")
        sys.exit(res.returncode)

def main():
    parser = argparse.ArgumentParser(description="Jeff Spira Archival Pipeline Manager")
    parser.add_argument("action", choices=["manifest", "download-all", "download-quick", "organize", "route", "full-pipeline"],
                        help="Action to perform")
    parser.add_argument("--limit", type=int, default=None, help="Limit per category for quick downloads")
    args = parser.parse_args()

    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_dir)

    if args.action == "manifest":
        run_step(["python3", "fetch_manifest.py"], "1. Generating Asset Manifests from Wayback CDX API")

    elif args.action == "organize":
        run_step(["python3", "organize_archive.py"], "2. Setting up Hull Classification Folder Schema")

    elif args.action == "download-quick":
        limit = args.limit or 5
        run_step(["python3", "organize_archive.py"], "Initializing Schema")
        for manifest, out in [
            ("manifests/technical_reports.json", "raw_downloads/technical_reports"),
            ("manifests/study_plans.json", "raw_downloads/study_plans"),
            ("manifests/bills_of_materials.json", "raw_downloads/bills_of_materials"),
            ("manifests/manuals_and_guides.json", "raw_downloads/manuals_and_guides"),
        ]:
            if os.path.exists(manifest):
                run_step(["python3", "download_assets.py", "--manifest", manifest, "--output", out, "--limit", str(limit)],
                         f"Downloading sample from {manifest}")
        run_step(["python3", "sync_and_route.py"], "Routing downloaded files into model folders")

    elif args.action == "download-all":
        run_step(["python3", "organize_archive.py"], "Initializing Schema")
        for manifest, out in [
            ("manifests/technical_reports.json", "raw_downloads/technical_reports"),
            ("manifests/study_plans.json", "raw_downloads/study_plans"),
            ("manifests/bills_of_materials.json", "raw_downloads/bills_of_materials"),
            ("manifests/manuals_and_guides.json", "raw_downloads/manuals_and_guides"),
            ("manifests/other_documents.json", "raw_downloads/other_documents"),
            ("manifests/plates_and_drawings.json", "raw_downloads/plates_and_drawings")
        ]:
            if os.path.exists(manifest):
                run_step(["python3", "download_assets.py", "--manifest", manifest, "--output", out],
                         f"Downloading all items from {manifest}")
        run_step(["python3", "sync_and_route.py"], "Routing all downloaded files into catalog")

    elif args.action == "route":
        run_step(["python3", "sync_and_route.py"], "Routing raw_downloads into archive folders")

    elif args.action == "full-pipeline":
        run_step(["python3", "fetch_manifest.py"], "Step 1: Manifest Discovery")
        run_step(["python3", "organize_archive.py"], "Step 2: Schema Initialization")
        run_step(["python3", "download_assets.py", "--manifest", "manifests/technical_reports.json", "--output", "raw_downloads/technical_reports"], "Step 3a: Download Technical Reports")
        run_step(["python3", "download_assets.py", "--manifest", "manifests/bills_of_materials.json", "--output", "raw_downloads/bills_of_materials"], "Step 3b: Download Bills of Materials")
        run_step(["python3", "download_assets.py", "--manifest", "manifests/study_plans.json", "--output", "raw_downloads/study_plans"], "Step 3c: Download Study Plans")
        run_step(["python3", "sync_and_route.py"], "Step 4: Route Assets into Catalog")

if __name__ == "__main__":
    main()
