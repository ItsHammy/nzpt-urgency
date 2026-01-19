"""

    This tool scrapes from the https://www.parliament.nz/en/pb/daily-progress-in-the-house/ RSS feed, then analyzes each file to count if the govt were in an urgency motion.
    The tool will output to `urgency.sqlite3` with the following schema:
    - `id` (INTEGER PRIMARY KEY): Unique identifier for each record.
    - `date` (TEXT): The date of the sitting.
    - `in_urgency` (INTEGER): Whether the government was in urgency (1) or not (0).
    
    NOTE: This tool is the main tool. If there is missing multiple entries, a full scrape can be manually triggered using scrape-webpage.py
    
"""



import asyncio
import sqlite3
import xml.etree.ElementTree as ET
from datetime import datetime, date

from playwright.async_api import async_playwright

DB_PATH = "urgency.sqlite3"
RSS_FEED_URL = "https://www3.parliament.nz/en/highvolumegenericlisting/rss/1667"
CURRENT_GOV_START = date(2023, 12, 3)
URGENCY_PHRASE = "A motion to accord urgency to the following business was agreed to"


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
    conn.commit()
    conn.close()


def parse_date(text: str):
    text = text.strip()
    fmts = [
        "%a, %d %b %Y %H:%M:%S %Z",
        "%a, %d %b %Y %H:%M:%S %z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
    ]
    for fmt in fmts:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    try:
        return datetime.strptime(text.split(" GMT")[0], "%a, %d %b %Y %H:%M:%S").date()
    except ValueError:
        return None


async def scrape_with_playwright():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("Loading RSS feed via headless browser...")
        await page.goto(RSS_FEED_URL, wait_until="networkidle")
        html = await page.content()

        if "<rss" not in html and "<feed" not in html:
            xml_text = await page.evaluate("document.body.innerText")
        else:
            xml_text = html

        if "<rss" not in xml_text and "<feed" not in xml_text:
            print("Still not seeing RSS/Atom XML. Snippet:")
            print(xml_text[:1000])
            await browser.close()
            return

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError as e:
            print("XML parse error:", e)
            print(xml_text[:1000])
            await browser.close()
            return

        entries = [
            el for el in root.iter()
            if el.tag.endswith("item") or el.tag.endswith("entry")
        ]
        print(f"Found {len(entries)} entries in feed")

        if not entries:
            await browser.close()
            return
        work_items = []
        for el in entries:
            pub_el = None
            link_el = None

            for child in el:
                t = child.tag.lower()
                if t.endswith("pubdate") or t.endswith("updated"):
                    pub_el = child
                elif t.endswith("link"):
                    link_el = child

            if pub_el is None or (pub_el.text or "").strip() == "":
                continue

            sitting_date = parse_date(pub_el.text or "")
            if not sitting_date or sitting_date < CURRENT_GOV_START:
                continue

            link_href = None
            if link_el is not None:
                if "href" in link_el.attrib:
                    link_href = link_el.attrib["href"]
                elif link_el.text:
                    link_href = link_el.text.strip()

            if not link_href:
                continue

            work_items.append((sitting_date, link_href))

        print(f"{len(work_items)} entries on/after {CURRENT_GOV_START}")

        results = []
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

    if results:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.executemany(
            "INSERT INTO urgency (date, in_urgency) VALUES (?, ?)",
            results,
            )
            conn.commit()
            conn.close()
            print(f"Inserted {len(results)} rows into {DB_PATH}")
        except Exception as e:
            print(f"No new results found: {e}")
        finally:
            open("lastupdate.txt", "w").write(datetime.now().isoformat())
        print(f"Inserted {len(results)} rows into {DB_PATH}")
    else:
        print("No results to insert.")


async def main():
    init_db()
    await scrape_with_playwright()
    open("lastupdate.txt", "w").write(datetime.now().strftime("%d %B %Y").lstrip("0").replace(" 0", " "))


if __name__ == "__main__":
    asyncio.run(main())