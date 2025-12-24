import asyncio
import sqlite3
from datetime import datetime

from playwright.async_api import async_playwright

DB_PATH = "urgency.sqlite3"


def ensure_bills_columns():
    """
    Make sure the `bills` table has `mps` and `desc` columns.
    Safe to run multiple times.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(bills)")
    cols = {row[1] for row in cursor.fetchall()}

    if "mps" not in cols:
        cursor.execute("ALTER TABLE bills ADD COLUMN mps TEXT")
    if "desc" not in cols:
        cursor.execute("ALTER TABLE bills ADD COLUMN desc TEXT")

    conn.commit()
    conn.close()


def get_bills_needing_details():
    """
    Return list of (id, url) for bills where mps or desc is NULL.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, url FROM bills WHERE mps IS NULL OR desc IS NULL")
    rows = cursor.fetchall()
    conn.close()
    return rows


async def scrape_details_for_bill(page, url: str):
    """
    Given a Playwright page and a bill URL, return (mps, desc) or (None, None)
    if they cannot be found.
    """
    await page.goto(url, wait_until="networkidle")

    #Member(s) in charge: first name in the table cell
    mps = await page.evaluate(
        """
        () => {
          const ths = Array.from(document.querySelectorAll('th'));
          const th = ths.find(t => t.textContent.trim().startsWith('Member(s) in charge:'));
          if (!th) return null;
          const td = th.nextElementSibling;
          if (!td) return null;
          const raw = td.textContent.trim();
          if (!raw) return null;

          // If there are multiple MPs, return only the first
          let first = raw.split(',')[0];
          if (first.includes(' and ')) {
            first = first.split(' and ')[0];
          }
          first = first.trim();
          return first || null;
        }
        """
    )

    # Description: text immediately following the generic paragraph
    desc = await page.evaluate(
        """
        () => {
          const genericText =
            'Bills are proposals to make a new law or to change an existing one. ' +
            'Only Parliament can pass a bill. Each bill goes through several stages, ' +
            'giving MPs and the public the chance to have their say.';

          const ps = Array.from(document.querySelectorAll('p'));
          const generic = ps.find(p => p.textContent.trim().startsWith('Bills are proposals to make a new law'));
          if (!generic) return null;

          // Look at subsequent siblings for the specific bill description
          let node = generic.nextSibling;
          while (node) {
            if (node.nodeType === Node.TEXT_NODE) {
              const text = node.textContent.trim();
              if (text && text !== genericText) {
                return text;
              }
            } else if (node.nodeType === Node.ELEMENT_NODE) {
              const text = node.textContent.trim();
              if (text && text !== genericText) {
                return text;
              }
            }
            node = node.nextSibling;
          }

          return null;
        }
        """
    )

    # Normalise whitespace a bit
    if isinstance(desc, str):
        desc = " ".join(desc.split())

    return mps, desc


async def scrape_all_bill_details():
    ensure_bills_columns()
    bills = get_bills_needing_details()

    if not bills:
        print("No bills need details; all rows already have mps/desc.")
        return

    print(f"Found {len(bills)} bills needing details.")

    updates = []  # (mps, desc, id)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        for bill_id, url in bills:
            print(f"Scraping details for bill {bill_id} -> {url}")
            try:
                mps, desc = await scrape_details_for_bill(page, url)
                print(f"  MP in charge: {mps!r}, desc present: {bool(desc)}")
                updates.append((mps, desc, bill_id))
            except Exception as e:
                print(f"  Error scraping {url}: {e}")

        await browser.close()

    # Write to SQLite
    if updates:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.executemany(
            "UPDATE bills SET mps = ?, desc = ? WHERE id = ?",
            updates,
        )
        conn.commit()
        conn.close()
        print(f"Updated {len(updates)} bills with mps/desc.")
    else:
        print("No updates to apply.")


if __name__ == "__main__":
    asyncio.run(scrape_all_bill_details())