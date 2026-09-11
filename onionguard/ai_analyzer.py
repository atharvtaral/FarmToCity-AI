"""
ai_analyzer.py
--------------
Handles talking to whichever AI provider is available.

Selection logic (simple if / elif / else, as requested):
    1. If GEMINI_API_KEY is set in the environment  -> use Gemini
    2. Else if OPENAI_API_KEY is set in the environment -> use OpenAI
    3. Else -> fall back to DEMO mode (mock data), so the app
       still runs end-to-end even without a key configured.
"""

import os
import json
import base64
from pathlib import Path


class AIProviderError(Exception):
    """Raised when the configured AI provider fails or returns bad data."""
    pass


def get_active_provider():
    """
    Inspect environment variables and decide which provider to use.
    Returns a tuple: (provider_name, api_key) where provider_name is
    one of "gemini", "openai", or None.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if gemini_key:
        return "gemini", gemini_key
    elif openai_key:
        return "openai", openai_key
    else:
        return None, None


def _encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


PROMPT = """
You are OnionGuard AI, an expert agricultural produce quality grading system.
Analyze the onion(s) in the provided image and return ONLY a valid JSON object
(no markdown formatting, no commentary, no code fences) with exactly these fields:

{
  "quality_score": <integer between 300 and 850>,
  "quality_label": "Poor" | "Fair" | "Good" | "Excellent",
  "freshness_percent": <integer 0-100>,
  "estimated_defect_percent": <integer 0-100>,
  "size_grade": "Small" | "Medium" | "Large" | "Mixed",
  "visible_issues": [<short strings such as "sprouting", "bruising", "mold", "discoloration">, empty list if none],
  "notes": "<one short sentence summary>"
}

Base the score mainly on: skin condition, firmness cues, sprouting/rot signs,
uniformity of size, and overall visual freshness.
"""


def analyze_with_gemini(image_path, api_key):
    import google.generativeai as genai

    genai.configure(api_key=api_key)
     
    model = genai.GenerativeModel("gemini-2.0-flash")
    #model = genai.GenerativeModel("gpt-6-astra")

    mime_type = "image/png" if image_path.lower().endswith("png") else "image/jpeg"
    image_part = {
        "mime_type": mime_type,
        "data": _encode_image(image_path),
    }

    response = model.generate_content([PROMPT, image_part])
    return _parse_json_response(response.text)


def analyze_with_openai(image_path, api_key):
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    b64 = _encode_image(image_path)
    ext = "png" if image_path.lower().endswith("png") else "jpeg"

    response = client.chat.completions.create(
        model="gpt-4o",#gpt-6-astra gpt-4o
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/{ext};base64,{b64}"},
                    },
                ],
            }
        ],
        max_tokens=500,
    )
    return _parse_json_response(response.choices[0].message.content)


def _parse_json_response(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise AIProviderError(
            f"Could not parse AI response as JSON: {e}\nRaw response:\n{text}"
        )


def mock_analysis(image_path):
    """Used automatically when no API key is configured, so the
    pipeline (logistics + marketplace) can still be demoed/tested."""
    return {
        "quality_score": 780,
        "quality_label": "Good",
        "freshness_percent": 94,
        "estimated_defect_percent": 6,
        "size_grade": "Medium",
        "visible_issues": [],
        "notes": "[DEMO MODE - no API key found] Sample analysis output.",
    }


def analyze_onion_image(image_path):
    """
    Main entry point used by main.py.

    if GEMINI_API_KEY is available   -> use Gemini
    elif OPENAI_API_KEY is available -> use OpenAI
    else                              -> demo mode
    """
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    provider, api_key = get_active_provider()

    if provider == "gemini":
        print("[OnionGuard] GEMINI_API_KEY found -> using Gemini AI for analysis...")
        result = analyze_with_gemini(image_path, api_key)
    elif provider == "openai":
        print("[OnionGuard] OPENAI_API_KEY found -> using OpenAI for analysis...")
        result = analyze_with_openai(image_path, api_key)
    else:
        print("[OnionGuard] No GEMINI_API_KEY or OPENAI_API_KEY found -> running in DEMO mode.")
        result = mock_analysis(image_path)

    result["_provider_used"] = provider or "demo"
    return result
