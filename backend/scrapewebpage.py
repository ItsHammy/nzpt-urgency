"""
This script will scrape as far back as CURRENT_GOV_START. Only use when there is a significant inconsistency with the database.

"""
import asyncio
import sqlite3
from datetime import datetime, date

from playwright.async_api import async_playwright

DB_PATH = "urgency.sqlite3"
BASE_URL = "https://www3.parliament.nz"
LIST_URL = f"{BASE_URL}/en/pb/daily-progress-in-the-house"
CURRENT_GOV_START = date(2023, 12, 3)
URGENCY_PHRASE = "A motion to accord urgency to the following business was agreed to"

# Safety upper bound; you said the first date you care about is on page 16
MAX_LIST_PAGES = 40


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS urgency (
            id INTEGER PRIMARY KEY,
            date TEXT,
            in_urgency INTEGER
        )
    """)
    # Ensure the unique index exists (harmless if you've already created it)
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_urgency_date ON urgency(date)
    """)
    conn.commit()
    conn.close()


def parse_listing_date(date_text: str):
    """
    Dates on listing pages look like '17 December 2025' (with &nbsp;).
    """
    if not date_text:
        return None
    cleaned = date_text.replace("\xa0", " ").strip()
    try:
        return datetime.strptime(cleaned, "%d %B %Y").date()
    except ValueError:
        return None


async def collect_listing_items(page):
    """
    Crawl the listing pages and return a list of (date, full_url)
    for all sitting days on/after CURRENT_GOV_START.
    Stops once it hits dates older than CURRENT_GOV_START.
    """
    items: list[tuple[date, str]] = []

    for page_num in range(1, MAX_LIST_PAGES + 1):
        # If page 1 is just LIST_URL, leave this logic as-is.
        # If the site uses ?page=1 for the first page, change to always use ?page=page_num.
        if page_num == 1:
            url = LIST_URL
        else:
            url = f"{LIST_URL}?page={page_num}"

        print(f"Listing page {page_num}: {url}")
        await page.goto(url, wait_until="networkidle")

        # Pull href + date text for each row in the desktop table
        rows = await page.evaluate(
            """
            () => {
              const rows = Array.from(
                document.querySelectorAll("table.table--list tbody tr.list__row")
              );
              return rows.map(row => {
                const link = row.querySelector("a.list__cell-heading");
                const cells = row.querySelectorAll("td.list__cell");
                const dateCell = cells.length > 1 ? cells[1] : null;
                return {
                  href: link ? link.getAttribute("href") : null,
                  dateText: dateCell ? dateCell.textContent.trim() : null
                };
              });
            }
            """
        )

        if not rows:
            print("No rows found on this listing page; assuming end of results.")
            break

        reached_older_than_start = False

        for r in rows:
            href = r.get("href")
            date_text = r.get("dateText")
            if not href or not date_text:
                continue

            sitting_date = parse_listing_date(date_text)
            if not sitting_date:
                continue

            # Listing is newest → oldest. Once we see older than CURRENT_GOV_START,
            # we can stop after this page.
            if sitting_date < CURRENT_GOV_START:
                reached_older_than_start = True
                continue

            full_url = BASE_URL + href
            items.append((sitting_date, full_url))

        if reached_older_than_start:
            print("Reached dates older than CURRENT_GOV_START; stopping pagination.")
            break

    # Dedup within this run by URL, in case of oddities in the listing
    seen_urls = set()
    unique_items = []
    for d, u in items:
        if u in seen_urls:
            continue
        seen_urls.add(u)
        unique_items.append((d, u))

    print(f"Collected {len(unique_items)} listing items on/after {CURRENT_GOV_START}")
    return unique_items


async def scrape_from_listing():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 1. Collect all relevant (date, URL) pairs from listing pages
        work_items = await collect_listing_items(page)

        # 2. Visit each daily-progress page and check for urgency
        results: list[tuple[str, int]] = []

        for sitting_date, url in work_items:
            print(f"Checking {sitting_date} -> {url}")
            try:
                await page.goto(url, wait_until="networkidle")
                content = await page.content()
            except Exception as e:
                print(f"Failed to load {url}: {e}")
                continue

            in_urgency = 1 if URGENCY_PHRASE in content else 0
            results.append((sitting_date.isoformat(), in_urgency))

        await browser.close()

    # 3. Insert results into SQLite, skipping duplicates via UNIQUE index
    if results:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # INSERT OR IGNORE will silently skip rows where `date` already exists
        cursor.executemany(
            "INSERT OR IGNORE INTO urgency (date, in_urgency) VALUES (?, ?)",
            results,
        )
        conn.commit()
        conn.close()
        print(f"Tried to insert {len(results)} rows into {DB_PATH} (duplicates ignored).")
    else:
        print("No results to insert.")


async def main():
    init_db()
    await scrape_from_listing()


if __name__ == "__main__":
    asyncio.run(main())