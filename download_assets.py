#!/usr/bin/env python3
"""
Spira Digital Archive - Robust Downloader with Rate Limiting & Verification
Downloads assets from the Wayback Machine according to generated manifests.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.parse
import hashlib

def download_file(url, target_path, delay_sec=0.2, max_retries=3):
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    if os.path.exists(target_path) and os.path.getsize(target_path) > 500:
        # Check if already downloaded and not an empty or tiny error page
        return True, "already exists"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': '*/*'
    }

    req = urllib.request.Request(url, headers=headers)
    for attempt in range(max_retries):
        try:
            time.sleep(delay_sec)
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                
                # Check for Wayback "not found" or error page masquerading as 200
                if len(data) < 200 and b"<html>" in data.lower():
                    return False, "returned html error instead of binary"
                
                # Check PDF header if expected
                if target_path.lower().endswith(".pdf"):
                    if not data.startswith(b"%PDF"):
                        return False, "corrupted/invalid PDF header"

                with open(target_path, "wb") as f:
                    f.write(data)
                return True, f"ok ({len(data):,} bytes)"
        except Exception as e:
            if attempt == max_retries - 1:
                return False, f"failed after {max_retries} attempts: {e}"
            time.sleep(1.0 * (attempt + 1))

    return False, "unknown failure"

def run_download_manifest(manifest_path, output_dir, limit=None):
    with open(manifest_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    # De-duplicate by filename
    seen = {}
    for item in items:
        fn = item["filename"]
        # prefer later timestamps if multiple captures exist
        if fn not in seen or item["timestamp"] > seen[fn]["timestamp"]:
            seen[fn] = item

    unique_items = list(seen.values())
    if limit:
        unique_items = unique_items[:limit]

    print(f"\nProcessing {len(unique_items)} items from {manifest_path} into {output_dir}...")
    success_count = 0
    fail_count = 0

    for i, item in enumerate(unique_items, 1):
        target = os.path.join(output_dir, item["filename"])
        ok, msg = download_file(item["wayback_url"], target)
        status = "✓" if ok else "✗"
        print(f"[{i}/{len(unique_items)}] {status} {item['filename']} -> {msg}")
        if ok:
            success_count += 1
        else:
            fail_count += 1

    print(f"\nCompleted: {success_count} succeeded, {fail_count} failed.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Download archived assets")
    parser.add_argument("--manifest", required=True, help="Path to manifest JSON file")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit of items to download")
    args = parser.parse_args()

    run_download_manifest(args.manifest, args.output, args.limit)
