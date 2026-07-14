"""Fetch the latest CFTC Commitments of Traders row for COMEX Gold.

Uses the free, public Socrata API (publicreporting.cftc.gov) — no auth, no
anti-bot restrictions, unlike CME's own site. Dataset kh3c-gbw2 is CFTC's
"Disaggregated - Combined" report: futures and options positions combined,
broken down by trader category. It is published weekly (Fridays, ~15:30 ET)
for the prior Tuesday's positions.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

from app.config import CFTC_COT_URL, CFTC_GOLD_CONTRACT_CODE


class CotError(RuntimeError):
    pass


def fetch_latest_row() -> dict:
    params = {
        "$limit": "1",
        "$order": "report_date_as_yyyy_mm_dd DESC",
        "cftc_contract_market_code": CFTC_GOLD_CONTRACT_CODE,
    }
    url = f"{CFTC_COT_URL}?{urllib.parse.urlencode(params)}"
    request = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise CotError(f"CFTC API returned HTTP {response.status}")
        payload = json.loads(response.read().decode("utf-8"))
    if not payload:
        raise CotError("CFTC API returned no rows for the configured gold contract code")
    return payload[0]


def _int(row: dict, key: str) -> int:
    value = row.get(key)
    return int(value) if value not in (None, "") else 0


def normalize(row: dict) -> dict:
    report_date = row.get("report_date_as_yyyy_mm_dd", "")[:10]
    if not report_date:
        raise CotError("CFTC row is missing report_date_as_yyyy_mm_dd")

    def category(long_key: str, short_key: str, change_long_key: str, change_short_key: str) -> dict:
        return {
            "long": _int(row, long_key),
            "short": _int(row, short_key),
            "change_long": _int(row, change_long_key),
            "change_short": _int(row, change_short_key),
        }

    return {
        "report_date": report_date,
        "open_interest": _int(row, "open_interest_all"),
        "change_open_interest": _int(row, "change_in_open_interest_all"),
        "categories": {
            "producer_merchant": category(
                "prod_merc_positions_long", "prod_merc_positions_short",
                "change_in_prod_merc_long", "change_in_prod_merc_short",
            ),
            "swap_dealers": category(
                "swap_positions_long_all", "swap__positions_short_all",
                "change_in_swap_long_all", "change_in_swap_short_all",
            ),
            "managed_money": category(
                "m_money_positions_long_all", "m_money_positions_short_all",
                "change_in_m_money_long_all", "change_in_m_money_short_all",
            ),
            "other_reportables": category(
                "other_rept_positions_long", "other_rept_positions_short",
                "change_in_other_rept_long", "change_in_other_rept_short",
            ),
        },
    }


def validate(cot: dict) -> dict:
    if cot["open_interest"] <= 0:
        raise CotError("CFTC row has non-positive open interest; refusing to publish")
    return cot
