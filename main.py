#!/usr/bin/env python3
"""
OnionGuard AI
=============
AI-powered onion quality scanning, transit-logistics advisory, and
urban wholesale marketplace matching - a Python implementation of
the OnionGuard product flow.

Usage:
    python main.py path/to/onion_image.jpg

Provider selection (set ONE env var, or put it in a .env file):
    GEMINI_API_KEY   -> used first if present  (Google Gemini)
    OPENAI_API_KEY   -> used if GEMINI_API_KEY is not set (OpenAI)

If neither key is set, the script runs in DEMO mode using sample data
so you can still see the full pipeline (scan -> logistics -> marketplace).
"""

import sys
import argparse

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional; env vars can also be exported normally.
    pass

from onionguard.ai_analyzer import analyze_onion_image, AIProviderError
from onionguard.logistics import build_logistics_advisory
from onionguard.marketplace import find_marketplace_match
from onionguard.display import print_report


def main():
    parser = argparse.ArgumentParser(
        description="OnionGuard AI - onion quality scan & logistics advisory"
    )
    parser.add_argument("image", help="Path to an onion image file (jpg/png)")
    args = parser.parse_args()

    try:
        analysis = analyze_onion_image(args.image)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except AIProviderError as e:
        print(f"AI provider error: {e}")
        sys.exit(1)

    logistics = build_logistics_advisory(analysis)
    market = find_marketplace_match(analysis, logistics)

    print_report(args.image, analysis, logistics, market)


if __name__ == "__main__":
    main()
