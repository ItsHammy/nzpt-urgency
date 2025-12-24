# lbillsaffected.py
import asyncio
import sqlite3
from datetime import datetime, date
import re

from playwright.async_api import async_playwright

DB_PATH = "urgency.sqlite3"
BASE_URL = "https://www3.parliament.nz"


def init_lbills_table():
    """
    Ensure the `lbills` table exists with columns (bill_name, url, pnum)
    and a UNIQUE index on url. If the table already exists but is missing
    `pnum`, add it.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lbills (
            id INTEGER PRIMARY KEY,
            bill_name TEXT,
            url TEXT,
            pnum INTEGER
        )
    """)

    # Check existing columns
    cursor.execute("PRAGMA table_info(lbills)")
    cols = {row[1] for row in cursor.fetchall()}

    if "pnum" not in cols:
        cursor.execute("ALTER TABLE lbills ADD COLUMN pnum INTEGER")

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_lbills_url ON lbills(url)
    """)

    conn.commit()
    conn.close()


def get_legacy_urgent_dates():
    """
    Read all (date, pnum) from `legacy` where in_urgency = 1.
    Returns a list of (datetime.date, pnum).
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT date, pnum FROM legacy WHERE in_urgency = 1")
    rows = cursor.fetchall()
    conn.close()

    result = []
    for date_str, pnum in rows:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            continue
        result.append((d, pnum))
    return result


def build_daily_progress_url(d: date) -> str:
    weekday = d.strftime("%A").lower()      # 'tuesday'
    day = str(d.day)                        # '9'
    month = d.strftime("%B").lower()        # 'december'
    year = d.year

    slug = f"daily-progress-for-{weekday}-{day}-{month}-{year}"
    return f"{BASE_URL}/en/pb/daily-progress-in-the-house/{slug}"


def extract_bills_from_urgency_section(html_content: str):
    """
    Extract bill names and URLs from the urgency section.
    Returns a list of (bill_name, url) tuples.
    """
    bills = []

    urgency_pattern = (
        r"<h3>\s*Urgency\s*</h3>(.*?)"
        r"<h3>[^<]*Government business.*?</h3>"
    )
    m = re.search(urgency_pattern, html_content, re.DOTALL | re.IGNORECASE)
    if not m:
        return bills

    urgency_section = m.group(1)

    link_pattern = r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
    links = re.findall(link_pattern, urgency_section, re.DOTALL | re.IGNORECASE)

    for url, raw_text in links:
        url = url.strip()

        text_no_tags = re.sub(r"<.*?>", "", raw_text, flags=re.DOTALL)
        bill_name = " ".join(text_no_tags.split()).strip()

        if not bill_name or not url:
            continue

        bills.append((bill_name, url))

    return bills


async def scrape_lbills_for_legacy():
    legacy_dates = get_legacy_urgent_dates()
    if not legacy_dates:
        print("No urgent sittings recorded in `legacy`; nothing to do.")
        return

    print(f"Found {len(legacy_dates)} legacy urgent dates in DB.")
    legacy_dates.sort(key=lambda tup: tup[0])

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        all_bills: list[tuple[str, str, int]] = []

        for d, pnum in legacy_dates:
            url = build_daily_progress_url(d)
            print(f"Scraping bills for {d} (P{pnum}) -> {url}")
            try:
                await page.goto(url, wait_until="networkidle")
                content = await page.content()
            except Exception as e:
                print(f"  Failed to load {url}: {e}")
                continue

            bills = extract_bills_from_urgency_section(content)
            print(f"  Found {len(bills)} bills in urgency section")
            for bill_name, bill_url in bills:
                all_bills.append((bill_name, bill_url, pnum))

        await browser.close()

    if all_bills:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT OR IGNORE INTO lbills (bill_name, url, pnum) VALUES (?, ?, ?)",
            all_bills,
        )
        conn.commit()
        conn.close()
        print(f"Tried to insert {len(all_bills)} legacy bills (duplicates ignored).")
    else:
        print("No legacy bills extracted; nothing to insert.")


async def main():
    init_lbills_table()
    await scrape_lbills_for_legacy()


if __name__ == "__main__":
    asyncio.run(main())