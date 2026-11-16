"""
Standalone SEO and Acceptance Verification Runner for Auromaa Associates
Executes direct ASGI requests to validate all 18+ routes, heading hierarchies,
metadata, canonicals, Schema.org graph, and sitemap without external test runners.
"""

import asyncio
import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from httpx import AsyncClient, ASGITransport

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEBSITE_DIR = PROJECT_ROOT / "website"
if str(WEBSITE_DIR) not in sys.path:
    sys.path.insert(0, str(WEBSITE_DIR))

from main import app, ROUTE_METADATA


async def run_verification():
    """Execute end-to-end programmatic verification against the ASGI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://www.auromaaassociates.com") as client:
        passed = 0
        failed = 0

        print("=" * 70)
        print("AUROMAA ASSOCIATES - MILESTONE M1 VERIFICATION SUITE")
        print("=" * 70)

        for path in ROUTE_METADATA.keys():
            res = await client.get(path)
            if res.status_code == 200:
                passed += 1
            else:
                print(f"[FAIL] Route {path} returned status {res.status_code}")
                failed += 1

            soup = BeautifulSoup(res.text, "html.parser")
            h1s = soup.find_all("h1")
            if len(h1s) == 1:
                passed += 1
            else:
                print(f"[FAIL] Route {path} has {len(h1s)} H1 tags")
                failed += 1

            titles = soup.find_all("title")
            if len(titles) == 1:
                passed += 1
            else:
                print(f"[FAIL] Route {path} has {len(titles)} title tags")
                failed += 1

            descs = soup.find_all("meta", attrs={"name": "description"})
            if len(descs) == 1:
                passed += 1
            else:
                print(f"[FAIL] Route {path} has {len(descs)} meta description tags")
                failed += 1

            canonical = soup.find("link", attrs={"rel": "canonical"})
            if canonical and canonical.get("href"):
                passed += 1
            else:
                print(f"[FAIL] Route {path} missing canonical URL")
                failed += 1

            headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
            heading_ok = len(headings) >= 1 and headings[0].name == "h1"
            if heading_ok:
                levels = [int(h.name[1]) for h in headings]
                for i in range(len(levels) - 1):
                    if levels[i + 1] > levels[i] + 1:
                        heading_ok = False
                        break
            if heading_ok:
                passed += 1
            else:
                print(f"[FAIL] Route {path} heading progression invalid")
                failed += 1

            schema_tag = soup.find("script", attrs={"type": "application/ld+json"})
            if schema_tag and schema_tag.string:
                parsed_schema = json.loads(schema_tag.string)
                serialized = json.dumps(parsed_schema)
                if "&amp;" not in serialized and "&#39;" not in serialized:
                    passed += 1
                else:
                    print(f"[FAIL] Route {path} JSON-LD contains escaped entities")
                    failed += 1
            else:
                print(f"[FAIL] Route {path} missing JSON-LD script")
                failed += 1

        home_res = await client.get("/")
        soup_home = BeautifulSoup(home_res.text, "html.parser")

        h1_home = soup_home.find("h1")
        if h1_home and "Intellectual Property Law Firm in India" in h1_home.text:
            passed += 1
        else:
            print("[FAIL] Homepage H1 text mismatch")
            failed += 1

        schema_el = soup_home.find("script", attrs={"type": "application/ld+json"})
        if schema_el and schema_el.string:
            schema_data = json.loads(schema_el.string)
            if "@graph" in schema_data:
                passed += 1
            else:
                print("[FAIL] JSON-LD schema missing @graph")
                failed += 1
        else:
            print("[FAIL] Missing JSON-LD script element")
            failed += 1

        robots_res = await client.get("/robots.txt")
        if robots_res.status_code == 200 and "Sitemap:" in robots_res.text:
            passed += 1
        else:
            print("[FAIL] /robots.txt check failed")
            failed += 1

        sitemap_res = await client.get("/sitemap.xml")
        if sitemap_res.status_code == 200:
            root = ET.fromstring(sitemap_res.text)
            if "urlset" in root.tag:
                passed += 1
            else:
                print("[FAIL] /sitemap.xml root is not urlset")
                failed += 1
        else:
            print("[FAIL] /sitemap.xml returned non-200")
            failed += 1

        print("-" * 70)
        print(f"VERIFICATION SUMMARY: {passed} PASSED, {failed} FAILED")
        print("=" * 70)

        if failed > 0:
            sys.exit(1)


if __name__ == "__main__":
    asyncio.run(run_verification())
