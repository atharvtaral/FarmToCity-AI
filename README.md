# Farm To City AI

A Python implementation of the OnionGuard pipeline:

1. **Smartphone AI Scan** — analyze a photo of onions
2. **AI Quality Scoring** — Gemini, OpenAI (`gpt-4o`), or custom models (e.g., `gpt-6-astra`) grade quality (300-850 score, freshness %, defects, size grade)
3. **AI Logistics Advisory** — transit spoilage risk, optimal buyer radius, route recommendation
4. **Urban Wholesale Marketplace** — mock buyer match + offer price

## How the AI provider is chosen

The app picks a provider with simple `if / elif / else` logic in
`onionguard/ai_analyzer.py`:

```python
if GEMINI_API_KEY is set:
    use Gemini
elif OPENAI_API_KEY is set:
    use OpenAI (gpt-4o / gpt-6-astra)
else:
    run in DEMO mode (sample data, no API calls)
```
# Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# edit .env and paste in either GEMINI_API_KEY or OPENAI_API_KEY
```

## Run — Streamlit app (camera + upload, recommended)

```bash
streamlit run app.py
```

This opens a browser page where you can:
- **📷 Use Camera** — capture a live photo of the onions directly from your device camera
- **📁 Upload Photo** — upload an existing onion image

Either way, clicking **"Run OnionGuard AI Analysis"** sends the image live to
whichever AI provider is configured and renders the quality score, logistics
advisory, and marketplace match directly on the page.

## Run — CLI (optional)

```bash
python main.py path/to/onion_photo.jpg
```

Example output:

```
============================================================
  ONIONGUARD AI  -  QUALITY & LOGISTICS REPORT
============================================================
Image analyzed : onion_photo.jpg
AI provider    : gemini
------------------------------------------------------------
STEP 1-2: SMARTPHONE AI SCAN
  Quality Score       : 780 / 850  (Good)
  Freshness           : 94%
  Estimated Defects   : 6%
  Size Grade          : Medium
  Visible Issues      : None detected
  Notes               : Firm, uniform onions with minimal blemishes.

STEP 3: AI LOGISTICS ADVISORY
  Transit Spoilage Risk : LOW
  Optimal Buyer Radius  : 45 km
  Route Recommendation  : Extended route to premium urban wholesale buyers viable

STEP 4: URBAN WHOLESALE MARKETPLACE
  Matched Buyer  : FreshHub B2B Market
  Offer Price    : $0.48 / kg
  Status         : MATCH FOUND
============================================================
```

## Project structure

```
onionguard/
├── app.py                      # Streamlit app (camera input + upload, live AI)
├── main.py                     # CLI entry point
├── onionguard/
│   ├── ai_analyzer.py          # Gemini/OpenAI provider selection + vision call
│   ├── logistics.py            # spoilage risk, buyer radius, route logic
│   ├── marketplace.py          # mock buyer matching + pricing
│   └── display.py              # console report formatting
├── requirements.txt
├── .env.example
└── README.md
```

## Notes / next steps for a real deployment

- Swap `marketplace.py`'s mock buyer list for a real marketplace/bidding API.
- Swap the fixed route text in `logistics.py` for a real maps/routing API
  (e.g. Google Maps Directions) if you want an actual optimized route + ETA.
- Add persistent storage (a database) to log every scan for traceability.
- Wrap `main()` in a small Flask/FastAPI app if you want a web/mobile
  front end instead of the CLI.
