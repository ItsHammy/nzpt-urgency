# billcounter.py
import asyncio
import sqlite3
from datetime import datetime, date
from urllib.parse import urlparse

from playwright.async_api import async_playwright

BASE_URL = "https://www3.parliament.nz"
LIST_URL = f"{BASE_URL}/en/pb/daily-progress-in-the-house"
CURRENT_GOV_START = date(2023, 12, 3)

# Reuse the shared DB to persist the set of bill_ids already counted.
# This is what lets the scan window shrink (via get_since_date()) without
# losing the running total: old bill_ids stay in the table forever, we
# only ever add newly-discovered ones, and the count is COUNT(*) over
# the whole table rather than a fresh in-memory scan each run.
DB_PATH = "/var/www/nzpt/urgency/urgency.sqlite3"


def ensure_bill_ids_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS introduced_bill_ids (
            bill_id TEXT PRIMARY KEY
        )
    """)
    conn.commit()
    conn.close()


def load_known_bill_ids() -> set[str]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT bill_id FROM introduced_bill_ids")
    ids = {row[0] for row in cursor.fetchall()}
    conn.close()
    return ids


def save_new_bill_ids(bill_ids: set[str]):
    if not bill_ids:
        return
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executemany(
        "INSERT OR IGNORE INTO introduced_bill_ids (bill_id) VALUES (?)",
        [(b,) for b in bill_ids],
    )
    conn.commit()
    conn.close()

BILLCOUNTER_PATH = "/var/www/nzpt/urgency/billcounter.txt"
MAX_LIST_PAGES = 40  # enough to cover back to CURRENT_GOV_START

# Written by new-gen-automation.py after a successful run. See scrapewebpage.py
# for the matching helper — kept in sync so both scripts use the same cutoff.
LAST_RUN_PATH = "/var/www/nzpt/urgency/last.txt"


def get_since_date() -> date:
    try:
        with open(LAST_RUN_PATH, "r", encoding="utf-8") as f:
            text = f.read().strip()
        parsed = datetime.strptime(text, "%Y-%m-%d").date()
        if parsed > CURRENT_GOV_START:
            return parsed
    except Exception:
        pass
    return CURRENT_GOV_START


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


async def collect_listing_items(page, since_date: date):
    """
    Crawl the listing pages and return a list of (date, full_url)
    for all sitting days on/after since_date.
    """
    items: list[tuple[date, str]] = []

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

        reached_older_than_start = False

        for r in rows:
            href = r.get("href")
            date_text = r.get("dateText")
            if not href or not date_text:
                continue

            sitting_date = parse_listing_date(date_text)
            if not sitting_date:
                continue

            if sitting_date < since_date:
                reached_older_than_start = True
                continue

            full_url = BASE_URL + href
            items.append((sitting_date, full_url))

        if reached_older_than_start:
            print(f"Reached dates older than {since_date}; stopping pagination.")
            break

    # Dedup by URL
    seen_urls = set()
    unique_items = []
    for d, u in items:
        if u in seen_urls:
            continue
        seen_urls.add(u)
        unique_items.append((d, u))

    print(f"Collected {len(unique_items)} listing items on/after {since_date}")
    return unique_items


def normalise_bill_id(href: str) -> str | None:
    """
    Given a bills.parliament.nz URL, return a stable bill identifier
    based on the last path segment (GUID-like part).
    """
    try:
        parsed = urlparse(href)
    except Exception:
        return None

    if "bills.parliament.nz" not in parsed.netloc:
        return None

    parts = [p for p in parsed.path.split("/") if p]
    if not parts:
        return None

    guid = parts[-1].strip().lower()
    return guid or None


async def introduced_bill_hrefs_on_page(page):
    """
    On the current daily-progress page, return a list of bill hrefs
    from the 'Introduction of bills' section only.
    """
    hrefs = await page.evaluate(
        """
        () => {
          const results = [];

          const h3s = Array.from(document.querySelectorAll('h3'));
          const introH3s = h3s.filter(h3 =>
            h3.textContent.trim().toLowerCase().includes('introduction of bills')
          );
          if (!introH3s.length) {
            return results;
          }

          for (const h3 of introH3s) {
            let node = h3.nextSibling;
            while (node) {
              if (node.nodeType === Node.ELEMENT_NODE &&
                  node.tagName.toLowerCase() === 'h3') {
                // reached the next section
                break;
              }

              if (node.nodeType === Node.ELEMENT_NODE) {
                const el = node;
                const links = el.querySelectorAll('a');
                links.forEach(a => {
                  const text = (a.textContent || '').trim();
                  const href = (a.href || '').trim();
                  if (!href || !text) return;

                  if (href.includes('bills.parliament.nz') &&
                      text.toLowerCase().includes('bill')) {
                    results.push(href);
                  }
                });
              }

              node = node.nextSibling;
            }
          }

          return results;
        }
        """
    )
    return [h for h in hrefs if h]


async def count_unique_bills():
    ensure_bill_ids_table()
    since_date = get_since_date()
    print(f"Scanning since_date = {since_date} (CURRENT_GOV_START = {CURRENT_GOV_START})")

    known_bill_ids = load_known_bill_ids()
    print(f"{len(known_bill_ids)} bill_ids already known from previous runs")

    newly_found: set[str] = set()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        work_items = await collect_listing_items(page, since_date)

        for sitting_date, url in work_items:
            print(f"Scanning {sitting_date} -> {url}")
            try:
                await page.goto(url, wait_until="networkidle")
            except Exception as e:
                print(f"  Failed to load {url}: {e}")
                continue

            hrefs = await introduced_bill_hrefs_on_page(page)
            print(f"  Found {len(hrefs)} introduced bill links on this day")

            for href in hrefs:
                bill_id = normalise_bill_id(href)
                if bill_id:
                    newly_found.add(bill_id)

        await browser.close()

    save_new_bill_ids(newly_found)
    total_bill_ids = known_bill_ids | newly_found
    return len(total_bill_ids)

async def count_unique_bills_sync(): # fix bug where billcounter.txt is not updated correctly as it doesn't read old count. this logic is seperate from main as too much for main :)
    newcount = await count_unique_bills()
    oldcount = open(BILLCOUNTER_PATH, "r", encoding="utf-8").read().strip().split(",")[0]
    count = int(oldcount) + newcount
    return count

async def main():
    count = await count_unique_bills_sync()
    today_str = datetime.now().date().isoformat()
    line = f"{count}, {today_str}\n"

    with open(BILLCOUNTER_PATH, "w", encoding="utf-8") as f:
        f.write(line)

    print(f"Total unique introduced bills since {CURRENT_GOV_START}: {count}")
    print(f"Wrote '{line.strip()}' to {BILLCOUNTER_PATH}")


if __name__ == "__main__":
    asyncio.run(main())