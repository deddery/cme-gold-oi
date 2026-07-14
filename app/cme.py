"""Extract Gold Options rows from a manually downloaded CME PG64 Daily Bulletin.

CME's Akamai bot protection blocks automated PDF downloads from this site, so
the PDF must be fetched by a human via a browser (see CME_PG64_URL in
app/config.py) — this module only handles parsing the local file.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path
from typing import Iterable

class ParseError(RuntimeError):
    pass


def pdf_to_text(pdf_path: Path) -> str:
    executable = shutil.which("pdftotext")
    if not executable:
        raise ParseError("pdftotext is required; install Poppler first")
    completed = subprocess.run(
        [executable, "-layout", str(pdf_path), "-"], check=True,
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return completed.stdout


def trade_date(text: str) -> str:
    """Return ISO trade date printed in a CME bulletin."""
    from datetime import datetime
    match = re.search(r"\b(?:Mon|Tue|Wed|Thu|Fri),\s+([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})", text)
    if not match:
        raise ParseError("Could not find bulletin trade date")
    return datetime.strptime(match.group(1), "%b %d, %Y").date().isoformat()


def _number(value: str) -> int:
    return int(value.replace(",", ""))


def parse_gold_rows(text: str) -> list[dict]:
    """Parse COMEX Gold Option rows from CME's text layout.

    A CME product heading (for example ``OG PUT COMEX GOLD OPTIONS``) supplies
    the option side. Each following price row starts with its strike; OI is the
    number immediately before ``UNCH``, a signed OI change, or ``NEW``.
    """
    rows: list[dict] = []
    current_expiry: str | None = None
    current_type: str | None = None
    current_product: str | None = None
    for raw in text.splitlines():
        line = raw.strip()
        heading = re.match(r"^(OG[0-5]?)\s+(CALL|PUT)\s+(?:COMEX\s+)?GOLD OPTIONS\b", line)
        if heading:
            current_product, side = heading.groups()
            current_type = "C" if side == "CALL" else "P"
            current_expiry = None
            continue
        if not current_type:
            continue

        expiry_match = re.match(r"^(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)\d{2}\b", line)
        if expiry_match:
            current_expiry = expiry_match.group(0)
            continue

        row = re.match(r"^(\d{3,5}(?:\.\d+)?)\s+.*?\s+(\d{1,3}(?:,\d{3})*)\s+(?:(?:[+-]\s+)(?:\d{1,3}(?:,\d{3})*|NEW)|NEW|UNCH)\s*$", line)
        if row and current_expiry:
            rows.append({
                "expiry": current_expiry,
                "product": current_product,
                "option_type": current_type,
                "strike": float(row.group(1)),
                "open_interest": _number(row.group(2)),
            })
    if not rows:
        raise ParseError("No explicit Gold CALL/PUT rows found; CME layout may have changed")
    return rows


def validate_rows(rows: Iterable[dict]) -> list[dict]:
    valid = [r for r in rows if r["open_interest"] >= 0 and 1000 <= r["strike"] <= 10000]
    if len(valid) < 10:
        raise ParseError("Too few valid rows; refusing to publish incomplete data")
    return valid
