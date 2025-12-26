# billcounter.py
import asyncio
from datetime import datetime, date

from playwright.async_api import async_playwright

BASE_URL = "https://www3.parliament.nz"
LIST_URL = f"{BASE_URL}/en/pb/daily-progress-in-the-house"
CURRENT_GOV_START = date(2023, 12, 3)

BILLCOUNTER_PATH = "billcounter.txt"


MAX_LIST_PAGES = 40


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

    # Deduplicate by URL (in case of any duplicates across pages)
    seen_urls = set()
    unique_items = []
    for d, u in items:
        if u in seen_urls:
            continue
        seen_urls.add(u)
        unique_items.append((d, u))

    print(f"Collected {len(unique_items)} listing items on/after {CURRENT_GOV_START}")
    return unique_items


async def count_unique_bills():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # 1. Collect daily-progress pages
        work_items = await collect_listing_items(page)

        bill_urls: set[str] = set()

        # 2. Visit each sitting page and collect bill URLs
        for sitting_date, url in work_items:
            print(f"Scanning {sitting_date} -> {url}")
            try:
                await page.goto(url, wait_until="networkidle")
            except Exception as e:
                print(f"  Failed to load {url}: {e}")
                continue

            links = await page.evaluate(
                """
                () => Array.from(document.querySelectorAll('a'))
                      .map(a => ({
                          href: a.href,
                          text: a.textContent || ''
                      }))
                """
            )

            for link in links:
                text = (link.get("text") or "").strip()
                href = (link.get("href") or "").strip()
                if not href or not text:
                    continue


                if "bill" in text.lower():
                    bill_urls.add(href)

        await browser.close()

    return len(bill_urls)


async def main():
    count = await count_unique_bills()
    today_str = datetime.now().date().isoformat()

    line = f"{count}, {today_str}\n"


    with open(BILLCOUNTER_PATH, "w", encoding="utf-8") as f:
        f.write(line)

    print(f"Total unique bills considered since {CURRENT_GOV_START}: {count}")
    print(f"Wrote '{line.strip()}' to {BILLCOUNTER_PATH}")


if __name__ == "__main__":
    asyncio.run(main())