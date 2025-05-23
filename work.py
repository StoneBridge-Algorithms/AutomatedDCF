import os
import sys
import re
import yfinance as yf
from sec_edgar_downloader import Downloader
from bs4 import BeautifulSoup
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from extract_mdna import fetch_mdna_text
from dotenv import load_dotenv
load_dotenv()

# ── CONFIG ─────────────────────────────────────────────────────────────────────
OUTPUT_DIR = "./sec_edgar_filings"
MDNA_MAX_CHARS = 4000
SEC_API_KEY = os.getenv("SEC_API_KEY")

# ── HELPERS ────────────────────────────────────────────────────────────────────

def get_historical_ebit_cagr(ticker_symbol: str, min_years=3) -> float:
    """
    Fetch last 3–5 years of EBIT (Operating Income) and compute CAGR.
    """
    tk = yf.Ticker(ticker_symbol)
    fin = tk.financials
    if fin is None or fin.empty:
        raise RuntimeError("No financials found for " + str(ticker_symbol))

    # Try common EBIT labels
    for label in ("Operating Income", "EBIT", "Ebit"):
        if label in fin.index:
            ebit = fin.loc[label].dropna().sort_index()
            break
    else:
        raise KeyError("EBIT/Operating Income not found in financials")

    if len(ebit) < min_years:
        raise ValueError(f"Need ≥{min_years} years of EBIT data, got {len(ebit)}")

    # Use up to the last 5 data points
    series = ebit.iloc[-5:]
    start, end = float(series.iloc[0]), float(series.iloc[-1])
    n = len(series) - 1
    if start <= 0 or end <= 0 or n == 0:
        return 0.0

    return (end / start) ** (1 / n) - 1

def classify_tone(mdna: str) -> str:
    """
    Classify MD&A tone as optimistic|neutral|pessimistic using VADER.
    """
    analyzer = SentimentIntensityAnalyzer()
    score = analyzer.polarity_scores(mdna)['compound']

    if score >=  0.05:
        return "optimistic"
    elif score <= -0.05:
        return "pessimistic"
    else:
        return "neutral"

# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) != 2:
        print("Usage: python work.py <TICKER>")
        sys.exit(1)

    ticker = sys.argv[1].upper()
    try:
        hist_cagr = get_historical_ebit_cagr(ticker)
        mdna      = fetch_mdna_text(ticker, SEC_API_KEY)
        tone      = classify_tone(mdna)

        # Adjust CAGR by ±2% based on tone
        adj = hist_cagr + (
            0.02 if tone == "optimistic"
            else -0.02 if tone == "pessimistic"
            else 0.0
        )
        print(tone)
        print(f"{adj * 100:.1f}%")

    except Exception as e:
        print("Error:", e)
        sys.exit(1)

if __name__ == "__main__":
    main()
