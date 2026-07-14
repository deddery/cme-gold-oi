"""Compute dashboard and Telegram summaries for the CFTC COT gold report."""
from __future__ import annotations


def summarize(cot: dict) -> dict:
    categories = {}
    for name, position in cot["categories"].items():
        categories[name] = {
            "long": position["long"],
            "short": position["short"],
            "net": position["long"] - position["short"],
            "net_change": position["change_long"] - position["change_short"],
        }
    return {
        "report_date": cot["report_date"],
        "open_interest": cot["open_interest"],
        "change_open_interest": cot["change_open_interest"],
        "categories": categories,
    }


def _signed(value: int) -> str:
    return f"{value:+,}"


def telegram_message(summary: dict) -> str:
    managed_money = summary["categories"]["managed_money"]
    producer_merchant = summary["categories"]["producer_merchant"]
    swap_dealers = summary["categories"]["swap_dealers"]
    return (
        f"<b>CFTC COT — COMEX Gold ({summary['report_date']})</b>\n\n"
        f"Managed Money net: <b>{_signed(managed_money['net'])}</b> (Δ {_signed(managed_money['net_change'])})\n"
        f"Producer/Merchant net: {_signed(producer_merchant['net'])} (Δ {_signed(producer_merchant['net_change'])})\n"
        f"Swap Dealers net: {_signed(swap_dealers['net'])} (Δ {_signed(swap_dealers['net_change'])})\n"
        f"Total Open Interest: {summary['open_interest']:,} (Δ {_signed(summary['change_open_interest'])})\n\n"
        "ข้อมูลรายสัปดาห์จาก CFTC (Futures+Options Combined) — Managed Money "
        "มักสะท้อนฝั่งเก็งกำไร ใช้เป็นบริบทประกอบการวิเคราะห์ XAUUSD ไม่ใช่คำแนะนำการลงทุน"
    )
