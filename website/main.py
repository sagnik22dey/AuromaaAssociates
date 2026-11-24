"""
Auromaa Associates - FastAPI Website
Intellectual Property Law Firm Web Application
"""

import json
import logging
import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from fastapi import FastAPI, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, Response, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
BASE_URL = "https://www.auromaaassociates.com"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
ENQUIRIES_LOG_FILE = DATA_DIR / "enquiries.jsonl"


def save_submission_locally(submission_type: str, data: dict):
    """Safely append enquiry or callback submission to local JSONL storage."""
    record = {
        "type": submission_type,
        "timestamp": datetime.now().isoformat(),
        "data": data,
    }
    try:
        with open(ENQUIRIES_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        logging.error(f"Failed to record submission locally: {e}")


def send_email_notification(subject: str, body: str, reply_to: str | None = None):
    """Send an email notification via SMTP if environment variables are configured."""
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    recipient = os.environ.get("NOTIFICATION_EMAIL", "info@auromaaassociates.com")

    if not smtp_host or not smtp_user or not smtp_password:
        logging.info("SMTP not configured. Notification logged locally.")
        return

    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = f"Auromaa Associates Website <{smtp_user}>"
        msg["To"] = recipient
        if reply_to:
            msg["Reply-To"] = reply_to
        msg.set_content(body)

        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            logging.info(f"Notification email dispatched to {recipient}")
    except Exception as e:
        logging.error(f"Failed to dispatch notification email via SMTP: {e}")

app = FastAPI(
    title="Auromaa Associates",
    description="Intellectual Property Law Firm Website",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

ROUTE_METADATA = {
    "/": {
        "title": "Auromaa Associates | Advocates & IP Attorneys | Indian Intellectual Property Law Firm",
        "description": "Auromaa Associates is a premier Indian IP law firm with 18+ years of excellence in trademarks, patents, copyright, industrial designs, and GI protection.",
        "canonical": f"{BASE_URL}/",
    },
    "/the-firm": {
        "title": "About Us | Auromaa Associates IP Law Firm",
        "description": "Learn about Auromaa Associates, an Indian IP law firm built on competence, confidentiality, commitment, and courtesy with 18+ years of legal excellence.",
        "canonical": f"{BASE_URL}/the-firm",
    },
    "/our-mission": {
        "title": "Our Mission | Auromaa Associates IP Law Firm",
        "description": "Our mission is to help people and businesses in India and overseas protect, manage and enforce their intellectual property with focused expertise.",
        "canonical": f"{BASE_URL}/our-mission",
    },
    "/our-vision": {
        "title": "Our Vision | Auromaa Associates IP Law Firm",
        "description": "To be the IPR firm of choice for people and businesses in India and chosen international markets, delivering accessible and fair legal counsel.",
        "canonical": f"{BASE_URL}/our-vision",
    },
    "/our-values": {
        "title": "Our Values | Auromaa Associates IP Law Firm",
        "description": "Our practice rests on four values: competence, confidentiality, commitment, and courtesy, ensuring dedicated advocacy for your IP assets.",
        "canonical": f"{BASE_URL}/our-values",
    },
    "/our-quality-policy": {
        "title": "Our Quality Policy | Auromaa Associates IP Law Firm",
        "description": "At Auromaa Associates, quality means accurate advice, careful work, transparent fees, and clear communication on every IP matter.",
        "canonical": f"{BASE_URL}/our-quality-policy",
    },
    "/awards": {
        "title": "Awards & Professional Standing | Auromaa Associates",
        "description": "Recognized across India for 18+ years of IP excellence, Bar Council compliance, and international affiliations with AIPPI, APAA, and INTA.",
        "canonical": f"{BASE_URL}/awards",
    },
    "/our-clients": {
        "title": "Our Clients | Auromaa Associates IP Law Firm",
        "description": "Auromaa Associates provides IP counsel to corporate entities, manufacturers, and innovators including Shyam SEL, Skipper, Colekt, and Bioturm.",
        "canonical": f"{BASE_URL}/our-clients",
    },
    "/gallery": {
        "title": "Gallery | Auromaa Associates IP Law Firm",
        "description": "A visual showcase of Auromaa Associates chambers, conference facilities, legal library, and academic engagements across India.",
        "canonical": f"{BASE_URL}/gallery",
    },
    "/our-team": {
        "title": "Our IP Lawyers & Patent Attorneys | Auromaa Associates",
        "description": "Meet our team of Bar Council enrolled IP advocates and registered patent agents, led by partner Sidhartha Das and senior associate Moitri Das.",
        "canonical": f"{BASE_URL}/our-team",
    },
    "/practice-areas": {
        "title": "IPR Services & Practice Areas in India | Auromaa Associates",
        "description": "Full-cycle intellectual property legal services across India: trademarks, patents, copyright, industrial designs, GI, and plant variety rights.",
        "canonical": f"{BASE_URL}/practice-areas",
    },
    "/practice-areas/trademark": {
        "title": "Trademark Registration & Protection Services | Auromaa Associates",
        "description": "Comprehensive trademark registration in India: brand clearance searches, filings, objections, oppositions, renewals, and infringement enforcement.",
        "canonical": f"{BASE_URL}/practice-areas/trademark",
    },
    "/practice-areas/patent": {
        "title": "Patent Filing & Prosecution in India & PCT | Auromaa Associates",
        "description": "Patent filing and prosecution in India and under PCT: patentability searches, specification drafting, FER responses, and controller hearings.",
        "canonical": f"{BASE_URL}/practice-areas/patent",
    },
    "/practice-areas/copyright": {
        "title": "Copyright Registration & Enforcement | Auromaa Associates",
        "description": "Protect literary, artistic, musical, cinematograph film and software works with copyright registration and anti-piracy enforcement in India.",
        "canonical": f"{BASE_URL}/practice-areas/copyright",
    },
    "/practice-areas/industrial-design": {
        "title": "Industrial Design Registration in India | Auromaa Associates",
        "description": "Secure statutory protection for novel product shapes, configurations, patterns, and aesthetics under the Indian Designs Act, 2000.",
        "canonical": f"{BASE_URL}/practice-areas/industrial-design",
    },
    "/practice-areas/geographical-indications": {
        "title": "Geographical Indications (GI) Registration | Auromaa Associates",
        "description": "Legal counsel and registration for regional agricultural, handicraft, and manufactured products under the Indian GI Act.",
        "canonical": f"{BASE_URL}/practice-areas/geographical-indications",
    },
    "/practice-areas/plant-varieties": {
        "title": "Plant Varieties & Farmers' Rights Protection | Auromaa Associates",
        "description": "Protection for breeders, research institutions, and farmers under the Protection of Plant Varieties and Farmers' Rights Act, 2001.",
        "canonical": f"{BASE_URL}/practice-areas/plant-varieties",
    },
    "/practice-areas/semiconductor-ic-layout": {
        "title": "Semiconductor IC Layout Design Registration | Auromaa Associates",
        "description": "Registration and statutory protection for integrated circuit layout designs and microchip topologies in India.",
        "canonical": f"{BASE_URL}/practice-areas/semiconductor-ic-layout",
    },
    "/practice-areas/startup-msme": {
        "title": "Startup & MSME IP Filings in India | Auromaa Associates",
        "description": "Trademark, patent, and design filings for start-ups and MSMEs with fee concessions and strategic statutory protection.",
        "canonical": f"{BASE_URL}/practice-areas/startup-msme",
    },
    "/practice-areas/pharmaceutical-ip": {
        "title": "Pharmaceutical IP & Regulatory Counsel | Auromaa Associates",
        "description": "Patent filing, oppositions, Section 3(d) analysis, and regulatory advice for pharmaceutical and life-sciences companies in India.",
        "canonical": f"{BASE_URL}/practice-areas/pharmaceutical-ip",
    },
    "/practice-areas/insolvency-transactions": {
        "title": "IP in Insolvency & Transactions | Auromaa Associates",
        "description": "IP due diligence, assignments, recordals, and asset defense in corporate mergers, acquisitions, and IBC insolvency proceedings.",
        "canonical": f"{BASE_URL}/practice-areas/insolvency-transactions",
    },
    "/practice-areas/licensing-franchising": {
        "title": "Licensing, Franchising & Technology Transfer | Auromaa Associates",
        "description": "Drafting and negotiating license, franchise, technology transfer, and confidentiality agreements for commercial IP exploitation.",
        "canonical": f"{BASE_URL}/practice-areas/licensing-franchising",
    },
    "/practice-areas/ip-portfolio-audits": {
        "title": "IP Portfolio Audits & Risk Reviews | Auromaa Associates",
        "description": "Systematic audit of registered and unregistered intellectual property assets, flagging protection gaps, renewals, and legal risks.",
        "canonical": f"{BASE_URL}/practice-areas/ip-portfolio-audits",
    },
    "/practice-areas/foreign-associate-desk": {
        "title": "Foreign Associate Desk for Indian IP Filings | Auromaa Associates",
        "description": "Dedicated desk for overseas law firms and foreign IP attorneys filing and prosecuting trademarks, patents, and designs in India.",
        "canonical": f"{BASE_URL}/practice-areas/foreign-associate-desk",
    },
    "/ipr-abstract": {
        "title": "IPR Abstract & Legal Resources | Auromaa Associates",
        "description": "Essential intellectual property law summaries, statutory guides, and procedural overviews curated by Auromaa Associates.",
        "canonical": f"{BASE_URL}/ipr-abstract",
    },
    "/faq": {
        "title": "Frequently Asked Questions on IP Law | Auromaa Associates",
        "description": "Clear answers to common questions regarding trademark registration, patent timelines, copyright protection, and IP enforcement in India.",
        "canonical": f"{BASE_URL}/faq",
    },
    "/news": {
        "title": "IP Law News & Regulatory Updates | Auromaa Associates",
        "description": "Latest news, case laws, High Court decisions, and statutory amendments shaping the Indian intellectual property landscape.",
        "canonical": f"{BASE_URL}/news",
    },
    "/blog": {
        "title": "IP Insights & Legal Commentary | Auromaa Associates",
        "description": "In-depth articles and analytical perspectives on patent strategies, brand protection, and contentious IP proceedings.",
        "canonical": f"{BASE_URL}/blog",
    },
    "/contact": {
        "title": "Contact Auromaa Associates | IP Law Firm in Kolkata, India",
        "description": "Contact our intellectual property team at AA-13 Prafulla Kanan, Kolkata. Call +91 33 40693025 or submit a confidential enquiry.",
        "canonical": f"{BASE_URL}/contact",
    },
    "/disclaimer": {
        "title": "Disclaimer & Bar Council Compliance | Auromaa Associates",
        "description": "Website terms and Bar Council of India Rule 36 compliance disclaimer for Auromaa Associates intellectual property advocates.",
        "canonical": f"{BASE_URL}/disclaimer",
    },
    "/privacy-policy": {
        "title": "Privacy Policy | Auromaa Associates",
        "description": "Privacy policy explaining how Auromaa Associates handles enquiry communications and maintains client confidentiality.",
        "canonical": f"{BASE_URL}/privacy-policy",
    },
    "/terms-of-use": {
        "title": "Terms of Use | Auromaa Associates",
        "description": "Terms of use governing the access and utilization of the Auromaa Associates website and intellectual property resources.",
        "canonical": f"{BASE_URL}/terms-of-use",
    },
    "/careers": {
        "title": "Careers | Auromaa Associates IP Law Firm",
        "description": "Explore career opportunities for intellectual property advocates, patent agents, and trademark attorneys at Auromaa Associates.",
        "canonical": f"{BASE_URL}/careers",
    },
}

SITEMAP_ENTRIES = [
    ("/", "weekly", "1.0"),
    ("/the-firm", "monthly", "0.8"),
    ("/our-mission", "monthly", "0.8"),
    ("/our-vision", "monthly", "0.8"),
    ("/our-values", "monthly", "0.8"),
    ("/our-quality-policy", "monthly", "0.8"),
    ("/awards", "monthly", "0.7"),
    ("/our-clients", "monthly", "0.8"),
    ("/gallery", "monthly", "0.7"),
    ("/our-team", "monthly", "0.8"),
    ("/practice-areas", "monthly", "0.9"),
    ("/practice-areas/trademark", "monthly", "0.8"),
    ("/practice-areas/patent", "monthly", "0.8"),
    ("/practice-areas/copyright", "monthly", "0.8"),
    ("/practice-areas/industrial-design", "monthly", "0.8"),
    ("/practice-areas/geographical-indications", "monthly", "0.8"),
    ("/practice-areas/plant-varieties", "monthly", "0.8"),
    ("/practice-areas/semiconductor-ic-layout", "monthly", "0.8"),
    ("/practice-areas/startup-msme", "monthly", "0.8"),
    ("/practice-areas/pharmaceutical-ip", "monthly", "0.8"),
    ("/practice-areas/insolvency-transactions", "monthly", "0.8"),
    ("/practice-areas/licensing-franchising", "monthly", "0.8"),
    ("/practice-areas/ip-portfolio-audits", "monthly", "0.8"),
    ("/practice-areas/foreign-associate-desk", "monthly", "0.8"),
    ("/ipr-abstract", "monthly", "0.7"),
    ("/faq", "monthly", "0.6"),
    ("/news", "weekly", "0.7"),
    ("/blog", "weekly", "0.7"),
    ("/contact", "monthly", "0.8"),
    ("/disclaimer", "yearly", "0.3"),
    ("/privacy-policy", "yearly", "0.3"),
    ("/terms-of-use", "yearly", "0.3"),
    ("/careers", "monthly", "0.6"),
]


def render_page(
    request: Request,
    template_name: str,
    route_key: str,
    active_page: str = "",
    extra_context: dict | None = None,
):
    """Render a Jinja2 template with route SEO metadata and default context values."""
    meta = ROUTE_METADATA.get(route_key, {
        "title": "Auromaa Associates | Advocates & IP Attorneys",
        "description": "Auromaa Associates is a full-service Intellectual Property law firm based in India.",
        "canonical": f"{BASE_URL}{request.url.path}",
    })

    disclaimer_cookie = request.cookies.get("auromaa_disclaimer_agreed")
    disclaimer_agreed = disclaimer_cookie == "true"

    context = {
        "request": request,
        "year": datetime.now().year,
        "active_page": active_page,
        "page_title": meta["title"],
        "meta_description": meta["description"],
        "canonical_url": meta["canonical"],
        "og_type": "website",
        "og_image": f"{BASE_URL}/static/images/logo.png",
        "disclaimer_agreed": disclaimer_agreed,
    }

    if extra_context:
        context.update(extra_context)

    template_path = BASE_DIR / "templates" / template_name
    target_template = template_name if template_path.exists() else "pages/placeholder.html"
    return templates.TemplateResponse(request=request, name=target_template, context=context)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Render the homepage."""
    return render_page(request, "pages/index.html", "/", "home")


@app.get("/the-firm", response_class=HTMLResponse)
async def the_firm(request: Request):
    """Render the firm overview page."""
    return render_page(request, "pages/the_firm.html", "/the-firm", "the-firm")


@app.get("/our-team", response_class=HTMLResponse)
async def our_team(request: Request):
    """Render our team profile page."""
    return render_page(request, "pages/our_team.html", "/our-team", "our-team")


@app.get("/our-mission", response_class=HTMLResponse)
async def our_mission(request: Request):
    """Render our mission statement page."""
    return render_page(request, "pages/our_mission.html", "/our-mission", "our-mission")


@app.get("/our-vision", response_class=HTMLResponse)
async def our_vision(request: Request):
    """Render our vision statement page."""
    return render_page(request, "pages/our_vision.html", "/our-vision", "our-vision")


@app.get("/our-values", response_class=HTMLResponse)
async def our_values(request: Request):
    """Render our core values page."""
    return render_page(request, "pages/our_values.html", "/our-values", "our-values")


@app.get("/our-quality-policy", response_class=HTMLResponse)
async def our_quality_policy(request: Request):
    """Render our quality policy page."""
    return render_page(request, "pages/our_quality_policy.html", "/our-quality-policy", "our-quality-policy")


@app.get("/awards", response_class=HTMLResponse)
async def awards(request: Request):
    """Render awards and professional standing page."""
    return render_page(request, "pages/awards.html", "/awards", "awards")


@app.get("/our-clients", response_class=HTMLResponse)
async def our_clients(request: Request):
    """Render client portfolio showcase page."""
    return render_page(request, "pages/our_clients.html", "/our-clients", "our-clients")


@app.get("/testimonials")
async def testimonials():
    """Redirect legacy testimonials URL to our-clients."""
    return RedirectResponse(url="/our-clients", status_code=301)


@app.get("/gallery", response_class=HTMLResponse)
async def gallery(request: Request):
    """Render firm gallery and chambers showcase page."""
    return render_page(request, "pages/gallery.html", "/gallery", "gallery")


@app.get("/advisors-instructors")
async def advisors_instructors():
    """Redirect to the team page partners section."""
    return RedirectResponse(url="/our-team#partners", status_code=302)


@app.get("/partners")
async def partners():
    """Redirect to the partners section of our team page."""
    return RedirectResponse(url="/our-team#partners", status_code=302)


@app.get("/our-associate-partner")
async def our_associate_partner():
    """Redirect to the associate partner section of our team page."""
    return RedirectResponse(url="/our-team#associate-partner", status_code=302)


@app.get("/experts")
async def experts():
    """Redirect to the experts section of our team page."""
    return RedirectResponse(url="/our-team#experts", status_code=302)


@app.get("/attorneys-support-staff")
async def attorneys_support_staff():
    """Redirect to the support staff section of our team page."""
    return RedirectResponse(url="/our-team#support-staff", status_code=302)


@app.get("/practice-areas", response_class=HTMLResponse)
async def practice_areas(request: Request):
    """Render practice areas index page."""
    return render_page(request, "pages/practice_areas.html", "/practice-areas", "practice-areas")


@app.get("/practice-areas/{slug}", response_class=HTMLResponse)
async def practice_area_detail(request: Request, slug: str):
    """Render practice area detail view for specific statutory domains."""
    route_key = f"/practice-areas/{slug}"
    if route_key not in ROUTE_METADATA:
        raise HTTPException(status_code=404, detail="Practice area not found")

    template_candidate = f"pages/practice_{slug.replace('-', '_')}.html"
    return render_page(
        request,
        template_candidate,
        route_key,
        "practice-areas",
    )


@app.get("/ipr-abstract", response_class=HTMLResponse)
async def ipr_abstract(request: Request):
    """Render IPR abstract legal resource page."""
    return render_page(request, "pages/ipr_abstract.html", "/ipr-abstract", "ipr-abstract")


@app.get("/faq", response_class=HTMLResponse)
async def faq(request: Request):
    """Render frequently asked questions page."""
    return render_page(request, "pages/faq.html", "/faq", "faq")


@app.get("/news", response_class=HTMLResponse)
async def news(request: Request):
    """Render news and regulatory updates page."""
    return render_page(request, "pages/news.html", "/news", "news")


@app.get("/blog", response_class=HTMLResponse)
async def blog(request: Request):
    """Render articles and legal insights page."""
    return render_page(request, "pages/blog.html", "/blog", "blog")


@app.get("/contact", response_class=HTMLResponse)
async def contact(request: Request):
    """Render contact and office location page."""
    return render_page(request, "pages/contact.html", "/contact", "contact")


@app.get("/disclaimer", response_class=HTMLResponse)
async def disclaimer(request: Request):
    """Render Bar Council compliance disclaimer page."""
    return render_page(request, "pages/disclaimer.html", "/disclaimer", "disclaimer")


@app.get("/privacy-policy", response_class=HTMLResponse)
async def privacy_policy(request: Request):
    """Render privacy policy page."""
    return render_page(request, "pages/privacy_policy.html", "/privacy-policy", "privacy-policy")


@app.get("/terms-of-use", response_class=HTMLResponse)
async def terms_of_use(request: Request):
    """Render terms of use page."""
    return render_page(request, "pages/terms_of_use.html", "/terms-of-use", "terms-of-use")


@app.get("/careers", response_class=HTMLResponse)
async def careers(request: Request):
    """Render careers and legal opportunities page."""
    return render_page(request, "pages/careers.html", "/careers", "careers")


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt(request: Request):
    """Serve robots.txt with crawling guidelines and sitemap directive."""
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        f"Sitemap: {BASE_URL}/sitemap.xml\n"
    )
    return PlainTextResponse(content, media_type="text/plain; charset=utf-8")


@app.get("/sitemap.xml", response_class=Response)
async def sitemap_xml(request: Request):
    """Generate XML sitemap listing canonical urls."""
    xml_items = "\n".join([
        f"  <url>\n    <loc>{BASE_URL}{path}</loc>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>"
        for path, freq, prio in SITEMAP_ENTRIES
    ])
    xml_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'{xml_items}\n'
        '</urlset>'
    )
    return Response(content=xml_content, media_type="application/xml")


@app.post("/api/accept-disclaimer")
async def accept_disclaimer():
    """Set persistent cookie for Bar Council disclaimer acceptance."""
    response = JSONResponse({"success": True, "message": "Disclaimer accepted."})
    response.set_cookie(
        key="auromaa_disclaimer_agreed",
        value="true",
        max_age=31536000,
        path="/",
        samesite="lax",
        httponly=False,
    )
    return response


@app.post("/api/enquiry")
async def submit_enquiry(
    request: Request,
    background_tasks: BackgroundTasks,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    organisation: str = Form(""),
    area_of_interest: str = Form(...),
    description: str = Form(...),
    consent: bool = Form(False),
):
    """Handle prospective client IP enquiry form submissions."""
    if not consent:
        return JSONResponse(
            {"success": False, "message": "Please accept the disclaimer and privacy policy."},
            status_code=400,
        )

    enquiry_data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "organisation": organisation,
        "area_of_interest": area_of_interest,
        "description": description,
        "client_ip": request.client.host if request.client else "unknown",
    }

    save_submission_locally("enquiry", enquiry_data)

    subject = f"[Auromaa Associates] New IP Enquiry: {area_of_interest} - {full_name}"
    body = (
        f"New Intellectual Property Enquiry received from website:\n\n"
        f"Name: {full_name}\n"
        f"Email: {email}\n"
        f"Phone: {phone}\n"
        f"Organisation: {organisation or 'N/A'}\n"
        f"Area of Interest: {area_of_interest}\n\n"
        f"Description:\n{description}\n\n"
        f"Consent: Confirmed adherence to Disclaimer and Privacy Policy."
    )

    background_tasks.add_task(send_email_notification, subject, body, email)

    return JSONResponse({
        "success": True,
        "message": "Thank you. We have received your enquiry and will get back to you within one working day.",
    })


@app.post("/api/callback")
async def request_callback(
    request: Request,
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    phone: str = Form(...),
    area_of_interest: str = Form(...),
    consent: bool = Form(False),
):
    """Handle callback request submissions."""
    if not consent:
        return JSONResponse(
            {"success": False, "message": "Please accept the disclaimer and privacy policy."},
            status_code=400,
        )

    callback_data = {
        "name": name,
        "phone": phone,
        "area_of_interest": area_of_interest,
        "client_ip": request.client.host if request.client else "unknown",
    }

    save_submission_locally("callback", callback_data)

    subject = f"[Auromaa Associates] New Callback Request: {area_of_interest} - {name}"
    body = (
        f"New Callback Request received from website:\n\n"
        f"Name: {name}\n"
        f"Phone: {phone}\n"
        f"Area of Interest: {area_of_interest}\n\n"
        f"Consent: Confirmed adherence to Disclaimer and Privacy Policy."
    )

    background_tasks.add_task(send_email_notification, subject, body)

    return JSONResponse({
        "success": True,
        "message": "Thank you. We have received your request and will call you back shortly.",
    })
