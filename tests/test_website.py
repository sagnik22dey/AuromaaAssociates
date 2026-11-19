"""
Automated Test Suite for Auromaa Associates Website
Validates HTTP routing, single H1 hierarchy, SEO meta tags, JSON-LD schema,
BCI compliance, facts strip, practice areas, workflow steps, and form endpoints.
"""

import sys
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import pytest
from httpx import AsyncClient, ASGITransport
from bs4 import BeautifulSoup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WEBSITE_DIR = PROJECT_ROOT / "website"
if str(WEBSITE_DIR) not in sys.path:
    sys.path.insert(0, str(WEBSITE_DIR))

from main import app

HTML_ROUTES = [
    "/",
    "/the-firm",
    "/our-mission",
    "/our-vision",
    "/our-values",
    "/our-quality-policy",
    "/awards",
    "/our-clients",
    "/gallery",
    "/our-team",
    "/practice-areas",
    "/practice-areas/trademark",
    "/practice-areas/patent",
    "/practice-areas/copyright",
    "/practice-areas/industrial-design",
    "/practice-areas/geographical-indications",
    "/practice-areas/plant-varieties",
    "/practice-areas/semiconductor-ic-layout",
    "/ipr-abstract",
    "/faq",
    "/news",
    "/blog",
    "/contact",
    "/disclaimer",
    "/privacy-policy",
    "/terms-of-use",
    "/careers",
]


@pytest.fixture
def anyio_backend():
    """Specify backend for anyio runner."""
    return "asyncio"


@pytest.fixture
async def client():
    """Yield async test client bound to FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="https://www.auromaaassociates.com") as ac:
        yield ac


@pytest.mark.anyio
async def test_all_routes_return_200(client: AsyncClient):
    """Verify that every registered route returns HTTP 200."""
    all_routes = HTML_ROUTES + ["/robots.txt", "/sitemap.xml"]
    for route in all_routes:
        response = await client.get(route)
        assert response.status_code == 200, f"Route {route} failed with status {response.status_code}"


@pytest.mark.anyio
async def test_single_h1_rule_across_pages(client: AsyncClient):
    """Verify that every HTML page has exactly one H1 element."""
    for route in HTML_ROUTES:
        response = await client.get(route)
        soup = BeautifulSoup(response.text, "html.parser")
        h1_tags = soup.find_all("h1")
        assert len(h1_tags) == 1, f"Route {route} expected 1 H1 tag, found {len(h1_tags)}"


@pytest.mark.anyio
async def test_heading_progression_across_all_pages(client: AsyncClient):
    """Verify that every page starts with an H1 and consecutive headings never skip levels."""
    for route in HTML_ROUTES:
        response = await client.get(route)
        soup = BeautifulSoup(response.text, "html.parser")
        headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
        assert len(headings) >= 1, f"Route {route} has no headings"
        assert headings[0].name == "h1", f"Route {route} first heading is {headings[0].name}, expected h1"
        levels = [int(h.name[1]) for h in headings]
        for i in range(len(levels) - 1):
            assert levels[i + 1] <= levels[i] + 1, (
                f"Route {route} skipped heading level from H{levels[i]} to H{levels[i+1]}"
            )


@pytest.mark.anyio
async def test_homepage_heading_hierarchy(client: AsyncClient):
    """Verify that Slide 1 has single H1 and Slides 2-4 have H2 tags matching contents.md."""
    response = await client.get("/")
    soup = BeautifulSoup(response.text, "html.parser")

    h1_tag = soup.find("h1")
    assert h1_tag is not None
    assert "Intellectual Property Law Firm in India" in h1_tag.text

    slide_headings = [h.text.strip() for h in soup.find_all(["h1", "h2"]) if "Protect Your Brand" in h.text or "Patent Filing" in h.text or "Enforcing Your" in h.text]
    assert len(slide_headings) == 3

    h2_tags = [h.text.strip() for h in soup.find_all("h2")]
    assert any("Protect Your Brand With Trademark Registration" in t for t in h2_tags)
    assert any("Patent Filing for Inventors and Innovators" in t for t in h2_tags)
    assert any("Enforcing Your Intellectual Property Rights" in t for t in h2_tags)


@pytest.mark.anyio
async def test_no_duplicate_title_or_meta_description(client: AsyncClient):
    """Verify there are no duplicate title or meta description tags on any route."""
    for route in HTML_ROUTES:
        response = await client.get(route)
        soup = BeautifulSoup(response.text, "html.parser")
        titles = soup.find_all("title")
        meta_descs = soup.find_all("meta", attrs={"name": "description"})

        assert len(titles) == 1, f"Route {route} has {len(titles)} title tags"
        assert len(meta_descs) == 1, f"Route {route} has {len(meta_descs)} description tags"
        assert len(titles[0].text.strip()) > 10
        assert len(meta_descs[0].get("content", "").strip()) >= 50


@pytest.mark.anyio
async def test_canonical_and_social_tags(client: AsyncClient):
    """Verify canonical link, OpenGraph tags, and Twitter Cards across all views."""
    for route in HTML_ROUTES:
        response = await client.get(route)
        soup = BeautifulSoup(response.text, "html.parser")

        canonical = soup.find("link", attrs={"rel": "canonical"})
        assert canonical is not None, f"Route {route} missing canonical tag"
        expected_canonical = f"https://www.auromaaassociates.com{route}" if route != "/" else "https://www.auromaaassociates.com/"
        assert canonical.get("href") == expected_canonical

        og_title = soup.find("meta", attrs={"property": "og:title"})
        og_desc = soup.find("meta", attrs={"property": "og:description"})
        og_url = soup.find("meta", attrs={"property": "og:url"})
        og_type = soup.find("meta", attrs={"property": "og:type"})
        assert og_title and og_desc and og_url and og_type, f"Route {route} missing OpenGraph tags"

        tw_card = soup.find("meta", attrs={"name": "twitter:card"})
        tw_title = soup.find("meta", attrs={"name": "twitter:title"})
        tw_desc = soup.find("meta", attrs={"name": "twitter:description"})
        assert tw_card and tw_title and tw_desc, f"Route {route} missing Twitter Card tags"


@pytest.mark.anyio
async def test_json_ld_schema(client: AsyncClient):
    """Verify syntactically valid Schema.org graph for LegalService and Attorney."""
    response = await client.get("/")
    soup = BeautifulSoup(response.text, "html.parser")

    schema_script = soup.find("script", attrs={"type": "application/ld+json"})
    assert schema_script is not None, "Missing JSON-LD structured data script"

    data = json.loads(schema_script.string)
    assert data.get("@context") == "https://schema.org"
    graph = data.get("@graph", [])
    assert len(graph) >= 3

    legal_service = next((item for item in graph if "LegalService" in item.get("@type", [])), None)
    assert legal_service is not None, "LegalService not found in schema graph"
    assert "Attorney" in legal_service.get("@type", [])
    assert legal_service.get("name") == "Auromaa Associates"
    assert legal_service.get("telephone") == "+91-33-40693025"
    assert legal_service.get("email") == "info@auromaaassociates.com"

    address = legal_service.get("address", {})
    assert address.get("addressLocality") == "Kolkata"
    assert address.get("postalCode") == "700101"

    catalog = legal_service.get("hasOfferCatalog", {})
    offers = catalog.get("itemListElement", [])
    assert len(offers) == 7, f"Expected 7 practice area offers, found {len(offers)}"

    founders = legal_service.get("founder", [])
    assert any(f.get("name") == "Sidhartha Das" for f in founders)

    employees = legal_service.get("employee", [])
    assert any(e.get("name") == "Moitri Das" for e in employees)


@pytest.mark.anyio
async def test_json_ld_no_html_entity_corruption(client: AsyncClient):
    """Verify that parsed JSON-LD strings across all routes do not contain &amp; or &#39;."""
    for route in HTML_ROUTES:
        response = await client.get(route)
        soup = BeautifulSoup(response.text, "html.parser")
        schema_script = soup.find("script", attrs={"type": "application/ld+json"})
        assert schema_script is not None, f"Route {route} missing JSON-LD structured data script"
        data = json.loads(schema_script.string)
        raw_json_str = json.dumps(data)
        assert "&amp;" not in raw_json_str, f"Route {route} JSON-LD contains corrupted &amp; entity"
        assert "&#39;" not in raw_json_str, f"Route {route} JSON-LD contains corrupted &#39; entity"


@pytest.mark.anyio
async def test_bci_disclaimer_7_clauses(client: AsyncClient):
    """Verify that all 7 Bar Council of India clauses are present in the disclaimer modal."""
    response = await client.get("/")
    content = response.text

    clauses = [
        "You are accessing this website of your own accord to seek information about Auromaa Associates",
        "The content on this website is for general information only and is not legal advice",
        "Any information you send through this website or by email, before we formally agree to act for you, will not be treated as confidential or privileged",
        "Auromaa Associates is not liable for the consequences of any action taken on the basis of this website",
        "Links to third-party websites are provided for convenience only. The firm does not endorse, and is not responsible for, their content",
        "All content on this website is the intellectual property of Auromaa Associates and may not be reproduced without written permission",
        "Auromaa Associates confirms that the information about the firm, its advocates and its practice areas on this website is true and accurate",
    ]

    for clause in clauses:
        assert clause in content, f"Missing BCI clause: {clause}"


@pytest.mark.anyio
async def test_facts_strip_copy(client: AsyncClient):
    """Verify the 4 stat tiles in the facts strip match contents.md."""
    response = await client.get("/")
    content = response.text

    assert "18 Years in IP Practice" in content
    assert "7 Areas of IP Law" in content
    assert "India and International Filings" in content
    assert "Consultancy, Registration and Litigation" in content


@pytest.mark.anyio
async def test_how_we_work_3_steps(client: AsyncClient):
    """Verify that How We Work has 3 numbered steps from contents.md without marketing filler."""
    response = await client.get("/")
    content = response.text

    assert "Understand your matter." in content
    assert "Plan the protection." in content
    assert "File, follow through and enforce." in content
    assert "Database Due Diligence" not in content
    assert "Statutory Lodgement" not in content


@pytest.mark.anyio
async def test_practice_areas_7_cards(client: AsyncClient):
    """Verify all 7 practice areas and their CTA link texts."""
    response = await client.get("/")
    content = response.text

    cards = [
        ("Trademark Registration & Protection", "Trademark services →"),
        ("Patent Filing & Prosecution", "Patent services →"),
        ("Copyright Registration", "Copyright services →"),
        ("Industrial Design Registration", "Design services →"),
        ("Geographical Indications", "GI services →"),
        ("Plant Varieties & Farmers' Rights", "Plant variety services →"),
        ("Semiconductor IC Layout Designs", "IC layout services →"),
    ]

    for title, link_text in cards:
        assert title in content, f"Missing practice area title: {title}"
        assert link_text in content, f"Missing practice area link text: {link_text}"


@pytest.mark.anyio
async def test_enquiry_and_callback_forms(client: AsyncClient):
    """Verify enquiry and callback form submission handling and consent requirement."""
    valid_enquiry = {
        "full_name": "Test Client",
        "email": "test@example.com",
        "phone": "+919830000000",
        "organisation": "Test Org",
        "area_of_interest": "Trademark",
        "description": "Need trademark clearance and filing.",
        "consent": "true",
    }
    res = await client.post("/api/enquiry", data=valid_enquiry)
    assert res.status_code == 200
    assert res.json().get("success") is True
    assert "received your enquiry" in res.json().get("message")

    invalid_enquiry = valid_enquiry.copy()
    invalid_enquiry["consent"] = "false"
    res = await client.post("/api/enquiry", data=invalid_enquiry)
    assert res.status_code == 400
    assert res.json().get("success") is False

    valid_cb = {
        "name": "Test Client",
        "phone": "+919830000000",
        "area_of_interest": "Patent",
        "consent": "true",
    }
    res = await client.post("/api/callback", data=valid_cb)
    assert res.status_code == 200
    assert res.json().get("success") is True
    assert "call you back shortly" in res.json().get("message")

    invalid_cb = valid_cb.copy()
    invalid_cb["consent"] = "false"
    res = await client.post("/api/callback", data=invalid_cb)
    assert res.status_code == 400
    assert res.json().get("success") is False


@pytest.mark.anyio
async def test_robots_txt(client: AsyncClient):
    """Verify /robots.txt syntax and Sitemap reference."""
    response = await client.get("/robots.txt")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    content = response.text
    assert "User-agent: *" in content
    assert "Allow: /" in content
    assert "Sitemap: https://www.auromaaassociates.com/sitemap.xml" in content


@pytest.mark.anyio
async def test_sitemap_xml(client: AsyncClient):
    """Verify /sitemap.xml valid XML and presence of canonical urls."""
    response = await client.get("/sitemap.xml")
    assert response.status_code == 200
    assert "xml" in response.headers.get("content-type", "")

    root = ET.fromstring(response.text)
    assert "urlset" in root.tag

    namespaces = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    locs = [elem.text for elem in root.findall(".//sm:loc", namespaces)]
    assert len(locs) >= 18
    assert "https://www.auromaaassociates.com/" in locs
    assert "https://www.auromaaassociates.com/practice-areas/trademark" in locs
    assert "https://www.auromaaassociates.com/the-firm" in locs


@pytest.mark.anyio
async def test_disclaimer_cookie_behavior(client: AsyncClient):
    """Verify that disclaimer acceptance sets cookie and suppresses modal on subsequent visits."""
    accept_res = await client.post("/api/accept-disclaimer")
    assert accept_res.status_code == 200
    assert accept_res.json().get("success") is True
    assert "auromaa_disclaimer_agreed" in accept_res.cookies

    first_visit = await client.get("/")
    assert first_visit.status_code == 200
    assert 'id="disclaimer-overlay"' in first_visit.text

    subsequent_visit = await client.get("/", cookies={"auromaa_disclaimer_agreed": "true"})
    assert subsequent_visit.status_code == 200
    soup_home = BeautifulSoup(subsequent_visit.text, "html.parser")
    overlay_home = soup_home.find("div", {"id": "disclaimer-overlay"})
    assert overlay_home is not None
    assert "hidden" in overlay_home.get("class", [])
    assert "display: none;" in overlay_home.get("style", "")


@pytest.mark.anyio
async def test_testimonials_redirect_and_clients(client: AsyncClient):
    """Verify legacy testimonials URL redirects to our-clients and client cards are present."""
    response = await client.get("/testimonials", follow_redirects=False)
    assert response.status_code == 301
    assert response.headers.get("location") == "/our-clients"

    clients_res = await client.get("/our-clients")
    assert clients_res.status_code == 200
    clients_text = BeautifulSoup(clients_res.text, "html.parser").get_text()
    assert "Shyam SEL & Power Limited" in clients_text
    assert "Skipper Limited" in clients_text
    assert "Colekt Stockholm AB" in clients_text
    assert "Samriddhi Rice Mill Pvt Ltd" in clients_text
    assert "Tarsons Products Private Limited" in clients_text
    assert "Bioturm GMBH" in clients_text
    assert "Dencol India Pvt Limited" in clients_text
    assert "Finorchem Private Limited" in clients_text
    assert "Sony Kaushiki Kaisa" in clients_text
    assert "Heinz Italia" in clients_text


    inner_page_visit = await client.get("/the-firm", cookies={"auromaa_disclaimer_agreed": "true"})
    assert inner_page_visit.status_code == 200
    soup_inner = BeautifulSoup(inner_page_visit.text, "html.parser")
    overlay_inner = soup_inner.find("div", {"id": "disclaimer-overlay"})
    assert overlay_inner is not None
    assert "hidden" in overlay_inner.get("class", [])
    assert "display: none;" in overlay_inner.get("style", "")
