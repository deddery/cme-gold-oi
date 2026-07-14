"""Manual-upload entry point: parse a CME PG64 PDF placed under data/raw/, validate, save, render, notify.

CME's Daily Bulletin blocks automated downloads (Akamai bot protection returns
HTTP 403 "suspected web scraping activity"), so this expects a human to have
downloaded the PDF from CME_PG64_URL via a browser and committed it under
data/raw/ with its original filename. This finds that upload, canonicalizes it
to <trade_date>.pdf, and runs the rest of the pipeline automatically.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

from app.cme import ParseError, parse_gold_rows, pdf_to_text, trade_date, validate_rows
from app.config import DOCS_DIR, PARSED_DIR, RAW_DIR
from app.notify import send_telegram
from app.report import summarize, telegram_message
from app.site import write_dashboard

CANONICAL_NAME = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def find_uploaded_pdf() -> Path | None:
    """Return the newest data/raw/*.pdf that isn't already a canonicalized <date>.pdf."""
    uploads = [p for p in RAW_DIR.glob("*.pdf") if not CANONICAL_NAME.match(p.stem)]
    if not uploads:
        return None
    return max(uploads, key=lambda p: p.stat().st_mtime)


def main() -> None:
    pdf_path = find_uploaded_pdf()
    if pdf_path is None:
        print("No newly uploaded PDF found under data/raw/; nothing to do")
        return

    text = pdf_to_text(pdf_path)
    date = trade_date(text)
    final_pdf = RAW_DIR / f"{date}.pdf"
    pdf_path.replace(final_pdf)

    rows = validate_rows(parse_gold_rows(text))
    summary = summarize(rows)
    payload = {"trade_date": date, "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"), "summary": summary, "rows": rows}
    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    (PARSED_DIR / f"{date}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_dashboard(DOCS_DIR, payload)
    send_telegram(telegram_message(date, summary))
    print(f"Published {len(rows)} rows for {date}")


if __name__ == "__main__":
    try:
        main()
    except ParseError as error:
        raise SystemExit(f"CME parsing stopped safely: {error}")
