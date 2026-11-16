# Auromaa Associates — New Website

A demo FastAPI website for **Auromaa Associates**, an Indian Intellectual Property law firm.

## Stack
- **Backend:** Python 3.11+ / FastAPI
- **Templates:** Jinja2 (HTML)
- **Styling:** Tailwind CSS (via CDN) + Custom CSS
- **Icons:** Google Material Symbols
- **Fonts:** Bitter, Montserrat, Work Sans, Newsreader (Google Fonts)

## Project Structure
```
website/
├── main.py               # FastAPI app & routes
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/
│   │   └── styles.css    # Custom CSS overrides
│   ├── js/
│   │   └── main.js       # Disclaimer popup, slider, callbacks
│   └── images/           # Logo, hero images
└── templates/
    ├── partials/
    │   ├── head.html     # <head> meta, fonts, Tailwind config
    │   ├── topbar.html   # Contact info top bar
    │   ├── nav.html      # Sticky navigation
    │   ├── footer.html   # 3-row footer
    │   ├── disclaimer_modal.html   # Entry disclaimer popup
    │   └── callback_modal.html     # Floating callback form
    └── pages/
        └── index.html    # Homepage
```

## Running Locally
```powershell
# Create & activate venv
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Start dev server
uvicorn main:app --reload --port 8000
```

Then open http://localhost:8000

## Design System — Sovereign Juris
| Token | Value |
|-------|-------|
| Primary Dark / Navy | `#1A202D` |
| Accent Maroon | `#A94C4C` |
| Gold CTA | `#F8D065` |
| Heading Font | Bitter / Newsreader (serif) |
| Body Font | Montserrat |
| Nav Font | Work Sans |
