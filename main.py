import os, json, time, datetime as dt
from typing import List, Dict
from utils import relevance_score, now_iso, normalize_url, domain_of
from google_search import google_search
from sheets_client import SheetClient

SHEET_NAME = os.getenv("GSPREAD_SHEET_NAME", "HVAC_ChilledWater_Feed")

def run_once() -> Dict[str, int]:
    import yaml
    with open("queries.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    queries: List[str] = cfg.get("queries", [])
    per_query = int(cfg.get("per_query", 10))

    sheet = SheetClient(sheet_name=SHEET_NAME)
    sheet.ensure_header([
        "run_timestamp", "query", "title", "url", "domain", "snippet", "score"
    ])
    existing_urls = set(normalize_url(u) for u in sheet.read_column_values(col_index=4))

    added = 0
    considered = 0
    batch_rows = []

    for q in queries:
        results = google_search(q, num=per_query)
        for r in results:
            considered += 1
            url = normalize_url(r.get("link", ""))
            if not url or url in existing_urls:
                continue
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            score = relevance_score(title, snippet)

            row = [now_iso(), q, title, url, domain_of(url), snippet, score]
            batch_rows.append(row)
            existing_urls.add(url)
            added += 1

    if batch_rows:
        sheet.append_rows(batch_rows)

    return {"added": added, "considered": considered}

def maybe_notify(summary: Dict[str, int]):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        return
    import requests
    msg = f"HVAC bot: añadidos {summary['added']} nuevos (de {summary['considered']} resultados escaneados)."
    try:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage",
                      json={"chat_id": chat_id, "text": msg, "disable_web_page_preview": True}, timeout=15)
    except Exception as e:
        print("Telegram notify error:", e)

if __name__ == "__main__":
    summary = run_once()
    print("Run summary:", summary)
    maybe_notify(summary)
