"""Scheduled entry point (weekly, Friday): fetch CFTC COT gold data, publish, notify."""
from __future__ import annotations

import json
from datetime import datetime, timezone

from app.cftc import CotError, fetch_latest_row, normalize, validate
from app.config import COT_DOCS_DIR, COT_PARSED_DIR
from app.cot_report import summarize, telegram_message
from app.notify import send_telegram
from app.site import write_cot_dashboard


def main() -> None:
    row = validate(normalize(fetch_latest_row()))
    report_date = row["report_date"]

    existing = COT_PARSED_DIR / f"{report_date}.json"
    if existing.exists():
        print(f"CFTC COT report for {report_date} already published; nothing to do")
        return

    summary = summarize(row)
    payload = {
        "report_date": report_date,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "summary": summary,
    }
    COT_PARSED_DIR.mkdir(parents=True, exist_ok=True)
    existing.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    write_cot_dashboard(COT_DOCS_DIR, payload)
    send_telegram(telegram_message(summary))
    print(f"Published CFTC COT gold report for {report_date}")


if __name__ == "__main__":
    try:
        main()
    except CotError as error:
        raise SystemExit(f"CFTC COT fetch stopped safely: {error}")
