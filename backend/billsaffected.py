import asyncio
import sqlite3
from datetime import datetime, date
import re

from playwright.async_api import async_playwright

DB_PATH = "urgency.sqlite3"
BASE_URL = "https://www3.parliament.nz"

# Example target:
# https://www3.parliament.nz/en/pb/daily-progress-in-the-house/daily-progress-for-tuesday-9-december-2025


def init_bills_table():
    """
    Ensure the `bills` table exists and `url` is unique.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY,
            bill_name TEXT,
            url TEXT
        )
    """)
    # Enforce URL uniqueness, even if the table already existed
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_bills_url ON bills(url)
    """)
    conn.commit()
    conn.close()


def get_urgent_dates():
    """
    Read all dates from `urgency` where in_urgency = 1.
    Returns a set of datetime.date objects.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT date FROM urgency WHERE in_urgency = 1")
    rows = cursor.fetchall()
    conn.close()

    urgent_dates = set()
    for (date_str,) in rows:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
            urgent_dates.add(d)
        except ValueError:
            continue

    return urgent_dates


def build_daily_progress_url(d: date) -> str:
    """
    Build the daily progress URL from a date, e.g.:

    date(2025, 12, 9) ->
      https://www3.parliament.nz/en/pb/daily-progress-in-the-house/
      daily-progress-for-tuesday-9-december-2025
    """
    weekday = d.strftime("%A").lower()      # 'tuesday'
    day = str(d.day)                        # '9' (no leading zero)
    month = d.strftime("%B").lower()        # 'december'
    year = d.year                           # 2025

    slug = f"daily-progress-for-{weekday}-{day}-{month}-{year}"
    return f"{BASE_URL}/en/pb/daily-progress-in-the-house/{slug}"


def extract_bills_from_urgency_section(html_content: str):
    """
    Extract bill names and URLs from the urgency section.
    Returns a list of (bill_name, url) tuples.

    Looks between:
      <h3>Urgency</h3>
    and the next Government business header:
      <h3>Government business—<em>continued</em></h3>
    (matched loosely to be robust to markup/dash variations).
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

    # Find all <a href="..."> ... </a> links in this section
    link_pattern = r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
    links = re.findall(link_pattern, urgency_section, re.DOTALL | re.IGNORECASE)

    for url, raw_text in links:
        url = url.strip()

        # Strip any inner HTML from the anchor text, keep plain text
        text_no_tags = re.sub(r"<.*?>", "", raw_text, flags=re.DOTALL)
        bill_name = " ".join(text_no_tags.split()).strip()

        if not bill_name or not url:
            continue

        # For bill links you showed, URLs are already absolute.
        # If you ever see relative ones, you could normalize here.
        bills.append((bill_name, url))

    return bills


async def scrape_bills_for_urgent_sittings():
    urgent_dates = get_urgent_dates()
    if not urgent_dates:
        print("No urgent sittings recorded in `urgency`; nothing to do.")
        return

    print(f"Found {len(urgent_dates)} urgent dates in DB.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        all_bills: list[tuple[str, str]] = []

        # 1. For each urgent date, build the URL directly and scrape bills
        for d in sorted(urgent_dates):
            url = build_daily_progress_url(d)
            print(f"Scraping bills for {d} -> {url}")
            try:
                await page.goto(url, wait_until="networkidle")
                content = await page.content()
            except Exception as e:
                print(f"  Failed to load {url}: {e}")
                continue

            bills = extract_bills_from_urgency_section(content)
            print(f"  Found {len(bills)} bills in urgency section")
            all_bills.extend(bills)

        await browser.close()

    # 2. Insert bills into SQLite (skip duplicates via UNIQUE url index)
    if all_bills:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT OR IGNORE INTO bills (bill_name, url) VALUES (?, ?)",
            all_bills,
        )
        conn.commit()
        conn.close()
        print(f"Tried to insert {len(all_bills)} bills (duplicates ignored).")
    else:
        print("No bills extracted; nothing to insert.")


async def main():
    init_bills_table()
    await scrape_bills_for_urgent_sittings()


if __name__ == "__main__":
    asyncio.run(main())