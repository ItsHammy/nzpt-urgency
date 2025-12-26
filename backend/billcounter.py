# billcounter.py
import asyncio
from datetime import datetime, date
from urllib.parse import urlparse

from playwright.async_api import async_playwright

BASE_URL = "https://www3.parliament.nz"
LIST_URL = f"{BASE_URL}/en/pb/daily-progress-in-the-house"
CURRENT_GOV_START = date(2023, 12, 3)

BILLCOUNTER_PATH = "billcounter.txt"
MAX_LIST_PAGES = 40  # enough to cover back to CURRENT_GOV_START


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

            if sitting_date < CURRENT_GOV_START:
                reached_older_than_start = True
                continue

            full_url = BASE_URL + href
            items.append((sitting_date, full_url))

        if reached_older_than_start:
            print("Reached dates older than CURRENT_GOV_START; stopping pagination.")
            break

    # Dedup by URL
    seen_urls = set()
    unique_items = []
    for d, u in items:
        if u in seen_urls:
            continue
        seen_urls.add(u)
        unique_items.append((d, u))

    print(f"Collected {len(unique_items)} listing items on/after {CURRENT_GOV_START}")
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
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        work_items = await collect_listing_items(page)

        bill_ids: set[str] = set()

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
                    bill_ids.add(bill_id)

        await browser.close()

    return len(bill_ids)


async def main():
    count = await count_unique_bills()
    today_str = datetime.now().date().isoformat()
    line = f"{count}, {today_str}\n"

    with open(BILLCOUNTER_PATH, "w", encoding="utf-8") as f:
        f.write(line)

    print(f"Total unique introduced bills since {CURRENT_GOV_START}: {count}")
    print(f"Wrote '{line.strip()}' to {BILLCOUNTER_PATH}")


if __name__ == "__main__":
    asyncio.run(main())