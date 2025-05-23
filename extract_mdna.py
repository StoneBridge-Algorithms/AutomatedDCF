# import os
# import re
# from sec_edgar_downloader import Downloader
# from bs4 import BeautifulSoup

# OUTPUT_DIR = "sec_edgar_data"  # Define your output path

# import re

# def mdna_extractor(text: str) -> str:
#     """
#     Extracts the MD&A section from a 10-K filing by identifying Item 7
#     and stopping at Item 7A or Item 8.
#     """

#     # Preserve line breaks and normalize spacing
#     text = text.replace('\xa0', ' ')  # non-breaking space
#     text = text.replace('\r\n', '\n').replace('\r', '\n')

#     # Match flexible Item 7 title, even across line breaks
#     start_pattern = re.compile(
#         r"(?i)item\s*7\.*\s*\n?\s*Management[’']?s\s+Discussion\s+and\s+Analysis.*?Operations",
#         re.DOTALL
#     )

#     # Match either Item 7A or Item 8 as end point
#     end_pattern = re.compile(
#         r"(?i)\n\s*item\s*7a\.*.*?\n|\n\s*item\s*8\.*.*?\n",
#         re.DOTALL
#     )

#     start_match = start_pattern.search(text)
#     if not start_match:
#         raise ValueError("Start of MD&A section (Item 7) not found.")

#     # Search for end only after the start
#     end_match = end_pattern.search(text[start_match.end():])

#     if end_match:
#         end_index = start_match.end() + end_match.start()
#         mdna_text = text[start_match.start():end_index]
#     else:
#         mdna_text = text[start_match.start():]  # fallback: to EOF

#     return mdna_text.strip()




# def extract_mdna_section(ticker_symbol: str) -> str:
#     """
#     Download the latest 10-K for `ticker_symbol` and return the full MD&A section text.
#     """
#     # 1) Download 10-K
#     dl = Downloader("MyCompanyName", "me@domain.com", OUTPUT_DIR)
#     dl.get("10-K", ticker_symbol, limit=1)

#     # 2) Locate downloaded 10-K directory
#     candidates = [
#         os.path.join(OUTPUT_DIR, ticker_symbol, "10-K"),
#         os.path.join(OUTPUT_DIR, "sec-edgar-filings", ticker_symbol, "10-K"),
#     ]
#     for base in candidates:
#         if os.path.isdir(base):
#             break
#     else:
#         raise FileNotFoundError("No 10-K directory found.")

#     # 3) Choose most recent filing
#     subs = sorted(os.listdir(base), reverse=True)
#     if not subs:
#         raise FileNotFoundError("No filings found.")
#     accession_dir = os.path.join(base, subs[0])

#     # 4) Find a .txt or .html/.htm file
#     filing_file = next(
#         (os.path.join(accession_dir, f) for f in os.listdir(accession_dir)
#          if f.lower().endswith(('.txt', '.html', '.htm'))),
#         None
#     )
#     if not filing_file:
#         raise FileNotFoundError("No suitable filing document found.")

#     # 5) Read and clean text
#     with open(filing_file, 'r', encoding='utf-8', errors='ignore') as f:
#         raw = f.read()
#     text = BeautifulSoup(raw, 'html.parser').get_text("\n")

#     # 6) Extract MD&A
#     mdna = mdna_extractor(text)
#     return mdna


# # Example usage:
# # result = extract_mdna_section("AAPL")
# # print(result[:2000])  # Preview first 2000 characters

from sec_api import QueryApi, ExtractorApi
import os

def fetch_mdna_text(ticker: str, api_key: str) -> str:
    """
    Fetch the MD&A (Item 7) text from the latest 10-K for `ticker`.
    """
    query_api     = QueryApi(api_key)
    extractor_api = ExtractorApi(api_key)
    
    # 1) Find the most recent 10-K
    query = {
        "query": {
            "query_string": {
                "query": f"ticker:{ticker} AND formType:\"10-K\""
            }
        },
        "sort": [{ "filedAt": { "order": "desc" }}],
        "from": 0,
        "size": 1
    }
    results = query_api.get_filings(query)
    if not results.get("filings"):
        raise ValueError(f"No 10-K found for ticker {ticker}")
    filing_url = results["filings"][0]["linkToFilingDetails"]
    
    # 2) Extract Item 7 MD&A (plain text)
    mdna_text = extractor_api.get_section(filing_url, "7", "text")
    if not mdna_text.strip():
        raise ValueError("MD&A (Item 7) returned empty")
    return mdna_text