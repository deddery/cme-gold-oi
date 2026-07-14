from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PARSED_DIR = DATA_DIR / "parsed"
DOCS_DIR = ROOT / "docs"

# CME's Daily Bulletin blocks automated downloads (Akamai bot protection returns
# HTTP 403 "suspected web scraping activity" per CME's Data Terms of Use). Visit
# this URL in a browser and commit the PDF under data/raw/ manually instead.
CME_PG64_URL = "https://www.cmegroup.com/daily_bulletin/current/Section64_Metals_Option_Products.pdf"

# CFTC Commitments of Traders — Disaggregated, Futures and Options Combined.
# Free public Socrata API, no auth, no anti-bot restrictions.
CFTC_COT_URL = "https://publicreporting.cftc.gov/resource/kh3c-gbw2.json"
CFTC_GOLD_CONTRACT_CODE = "088691"  # GOLD - COMMODITY EXCHANGE INC.
COT_PARSED_DIR = DATA_DIR / "parsed" / "cot"
COT_DOCS_DIR = DOCS_DIR / "cot"

