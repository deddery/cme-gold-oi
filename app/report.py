"""Compute dashboard and Telegram summaries."""
from __future__ import annotations

from collections import defaultdict


def summarize(rows: list[dict]) -> dict:
    by_type = defaultdict(int)
    strikes: dict[tuple[str, float], int] = defaultdict(int)
    for row in rows:
        by_type[row["option_type"]] += row["open_interest"]
        strikes[(row["option_type"], row["strike"])] += row["open_interest"]
    calls, puts = by_type["C"], by_type["P"]
    top_calls = sorted(({"strike": strike, "open_interest": oi} for (kind, strike), oi in strikes.items() if kind == "C"), key=lambda x: x["open_interest"], reverse=True)[:10]
    top_puts = sorted(({"strike": strike, "open_interest": oi} for (kind, strike), oi in strikes.items() if kind == "P"), key=lambda x: x["open_interest"], reverse=True)[:10]
    return {
        "total_call_oi": calls,
        "total_put_oi": puts,
        "put_call_ratio": round(puts / calls, 3) if calls else None,
        "top_calls": top_calls,
        "top_puts": top_puts,
    }


def telegram_message(trade_date: str, summary: dict) -> str:
    call = summary["top_calls"][0]
    put = summary["top_puts"][0]
    ratio = summary["put_call_ratio"]
    return (
        f"<b>CME Gold Options — {trade_date}</b>\n\n"
        f"Call wall: <b>{call['strike']:,.0f}</b> (OI {call['open_interest']:,})\n"
        f"Put wall: <b>{put['strike']:,.0f}</b> (OI {put['open_interest']:,})\n"
        f"Put/Call OI ratio: <b>{ratio:.3f}</b>\n"
        f"Total Call OI: {summary['total_call_oi']:,}\n"
        f"Total Put OI: {summary['total_put_oi']:,}\n\n"
        "ข้อมูล EOD จาก CME Daily Bulletin — ใช้เป็นบริบท ไม่ใช่คำแนะนำการลงทุน"
    )

