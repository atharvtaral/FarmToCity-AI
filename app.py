"""
app.py
------
OnionGuard AI - Streamlit app.

- Take a photo directly with your camera (st.camera_input) OR
  upload an onion photo (st.file_uploader).
- The image is sent live to whichever AI provider is configured
  (Gemini first, then OpenAI, else demo mode) for quality analysis.
- Results flow straight into the logistics advisory and marketplace
  matching steps and are rendered on the page - no manual steps.

Run with:
    streamlit run app.py
"""

import os
import tempfile
from pathlib import Path

import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from onionguard.ai_analyzer import analyze_onion_image, AIProviderError, get_active_provider
from onionguard.logistics import build_logistics_advisory
from onionguard.marketplace import find_marketplace_match


st.set_page_config(page_title="OnionGuard AI", page_icon="🧅", layout="centered")

# ---------------------------------------------------------------- styling --
st.markdown(
    """
    <style>
    .big-score { font-size: 3rem; font-weight: 800; }
    .badge {
        display: inline-block; padding: 4px 14px; border-radius: 999px;
        font-weight: 700; font-size: 0.85rem; margin-top: 4px;
    }
    .badge-low, .badge-good, .badge-excellent { background:#d6f5df; color:#166534; }
    .badge-medium, .badge-fair { background:#fef3c7; color:#92400e; }
    .badge-high, .badge-poor { background:#fee2e2; color:#991b1b; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------------ header --
st.title("🧅 OnionGuard AI")
st.caption("AI-Powered Agritech & Logistics Platform")

provider, _ = get_active_provider()
provider_label = {
    "gemini": "🟢 Connected — using **Gemini AI**",
    "openai": "🟢 Connected — using **OpenAI**",
    None: "🟡 No API key found — running in **DEMO mode** (add GEMINI_API_KEY or OPENAI_API_KEY in .env for live results)",
}[provider]
st.info(provider_label)

st.divider()

# ------------------------------------------------------------ image input --
st.subheader("Step 1 · Smartphone AI Scan")

tab_camera, tab_upload = st.tabs(["📷 Use Camera", "📁 Upload Photo"])

image_bytes = None
image_source_name = "captured_photo.jpg"

with tab_camera:
    camera_file = st.camera_input("Point your camera at the onions and capture")
    if camera_file is not None:
        image_bytes = camera_file.getvalue()
        image_source_name = "camera_capture.jpg"

with tab_upload:
    uploaded_file = st.file_uploader(
        "Upload an onion photo", type=["jpg", "jpeg", "png"]
    )
    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        image_source_name = uploaded_file.name

# ------------------------------------------------------------- run pipeline --
if image_bytes:
    st.image(image_bytes, caption="Image to analyze", use_container_width=True)

    if st.button("🔍 Run OnionGuard AI Analysis", type="primary", use_container_width=True):
        suffix = Path(image_source_name).suffix or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(image_bytes)
            tmp_path = tmp.name

        try:
            with st.spinner("Scanning onions and scoring quality..."):
                analysis = analyze_onion_image(tmp_path)

            with st.spinner("Generating logistics advisory..."):
                logistics = build_logistics_advisory(analysis)

            with st.spinner("Matching to urban wholesale buyers..."):
                market = find_marketplace_match(analysis, logistics)

        except FileNotFoundError as e:
            st.error(f"Image error: {e}")
            st.stop()
        except AIProviderError as e:
            st.error(f"AI provider error: {e}")
            st.stop()
        finally:
            os.unlink(tmp_path)

        st.divider()

        # ---------------------------------------------------- Step 2 result --
        st.subheader("Step 2 · AI Quality Score")
        score = analysis.get("quality_score", 0)
        label = analysis.get("quality_label", "Unknown")
        badge_class = f"badge-{label.lower()}"

        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown(f'<div class="big-score">{score}<span style="font-size:1.2rem;color:#666;"> / 850</span></div>', unsafe_allow_html=True)
            st.markdown(f'<span class="badge {badge_class}">{label}</span>', unsafe_allow_html=True)
        with col2:
            st.metric("Freshness", f"{analysis.get('freshness_percent', 0)}%")
            st.metric("Estimated Defects", f"{analysis.get('estimated_defect_percent', 0)}%")

        st.write(f"**Size grade:** {analysis.get('size_grade', 'N/A')}")
        issues = analysis.get("visible_issues") or []
        st.write(f"**Visible issues:** {', '.join(issues) if issues else 'None detected'}")
        st.caption(analysis.get("notes", ""))

        # ---------------------------------------------------- Step 3 result --
        st.divider()
        st.subheader("Step 3 · AI Logistics Advisory")

        risk = logistics["transit_spoilage_risk"]
        risk_badge = f"badge-{risk.lower()}"
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"**Transit Spoilage Risk**<br><span class='badge {risk_badge}'>{risk}</span>", unsafe_allow_html=True)
        with c2:
            st.metric("Optimal Buyer Radius", f"{logistics['optimal_buyer_radius_km']} km")

        st.write(f"**Route recommendation:** {logistics['route_recommendation']}")
        if logistics["warnings"]:
            for w in logistics["warnings"]:
                st.warning(w)

        # ---------------------------------------------------- Step 4 result --
        st.divider()
        st.subheader("Step 4 · Urban Wholesale Marketplace")

        m1, m2, m3 = st.columns(3)
        m1.metric("Matched Buyer", market["buyer_name"])
        m2.metric("Offer Price", f"${market['offer_price_per_kg']} / kg")
        m3.success(market["match_status"])

else:
    st.caption("Capture a photo or upload one above to run the analysis.")
