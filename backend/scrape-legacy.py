"""
One‑off script to backfill urgency data for the 52nd and 53rd Parliaments
into a separate 'legacy' table.

Parliament date ranges (inclusive):

- 52nd: 7 November 2017 – 6 September 2020
- 53rd: 25 November 2020 – 8 September 2023

Data preceeding the 52nd Parliament is not provided in the same format on the website, and will be collected separately.
"""

import asyncio
import sqlite3
from datetime import datetime, date

from playwright.async_api import async_playwright

DB_PATH = "urgency.sqlite3"
BASE_URL = "https://www3.parliament.nz"
LIST_URL = f"{BASE_URL}/en/pb/daily-progress-in-the-house"
URGENCY_PHRASE = "A motion to accord urgency to the following business was agreed to"

# Date ranges for parliaments we care about
PARLIAMENT_RANGES = [
    # (pnum, start_date, end_date)
    (52, date(2017, 11, 7),  date(2020, 9, 6)),
    (53, date(2020, 11, 25), date(2023, 9, 8)),
]

EARLIEST_DATE = min(r[1] for r in PARLIAMENT_RANGES)
MAX_LIST_PAGES = 78


def init_legacy_table():
    """
    Create the 'legacy' table if it does not exist.
    This script is intended as a one‑off; no unique index is needed.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS legacy (
            id INTEGER PRIMARY KEY,
            date TEXT,
            in_urgency INTEGER,
            pnum INTEGER
        )
        """
    )
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


def parliament_for_date(d: date) -> int | None:
    """
    Return the parliament number for a given date according to PARLIAMENT_RANGES,
    or None if the date is outside the 52nd/53rd ranges.
    """
    for pnum, start, end in PARLIAMENT_RANGES:
        if start <= d <= end:
            return pnum
    return None


async def collect_listing_items(page):
    """
    Crawl the listing pages and return a list of (date, full_url, pnum)
    for all sitting days in the 52nd and 53rd parliaments.

    Stops once it hits dates older than EARLIEST_DATE.
    """
    items: list[tuple[date, str, int]] = []

    for page_num in range(1, MAX_LIST_PAGES + 1):
        if page_num == 1:
            url = LIST_URL
        else:
            url = f"{LIST_URL}?page={page_num}"

        print(f"Listing page {page_num}: {url}")
        await page.goto(url, wait_until="networkidle")

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

        reached_before_earliest = False

        for r in rows:
            href = r.get("href")
            date_text = r.get("dateText")
            if not href or not date_text:
                continue

            sitting_date = parse_listing_date(date_text)
            if not sitting_date:
                continue


            if sitting_date < EARLIEST_DATE:
                reached_before_earliest = True
                continue

            pnum = parliament_for_date(sitting_date)
            if pnum is None:

                continue

            full_url = BASE_URL + href
            items.append((sitting_date, full_url, pnum))

        if reached_before_earliest:
            print("Reached dates earlier than earliest target; stopping pagination.")
            break


    seen = set()
    unique_items: list[tuple[date, str, int]] = []
    for d, u, p in items:
        key = (d, u)
        if key in seen:
            continue
        seen.add(key)
        unique_items.append((d, u, p))

    print(f"Collected {len(unique_items)} legacy listing items (52nd & 53rd).")
    return unique_items


async def scrape_legacy():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()


        work_items = await collect_listing_items(page)


        results: list[tuple[str, int, int]] = []

        for sitting_date, url, pnum in work_items:
            print(f"Checking {sitting_date} (P{pnum}) -> {url}")
            try:
                await page.goto(url, wait_until="networkidle")
                content = await page.content()
            except Exception as e:
                print(f"Failed to load {url}: {e}")
                continue

            in_urgency = 1 if URGENCY_PHRASE in content else 0
            results.append((sitting_date.isoformat(), in_urgency, pnum))

        await browser.close()


    if results:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executemany(
            "INSERT INTO legacy (date, in_urgency, pnum) VALUES (?, ?, ?)",
            results,
        )
        conn.commit()
        conn.close()
        print(f"Inserted {len(results)} rows into legacy table.")
    else:
        print("No legacy results to insert.")


async def main():
    init_legacy_table()
    await scrape_legacy()


if __name__ == "__main__":
    asyncio.run(main())