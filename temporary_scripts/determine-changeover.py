"""
find_structure_change.py

Binary-searches the NZ Parliament "Daily Progress in the House" pages
between two known bounds to find the exact date the HTML structure changed.

Known:
  - OLD structure before 31 March 2026
  - NEW structure by 28 May 2026

Old structure:  <h3>Urgency</h3>
New structure:  <h3><span>Urgency</span></h3>

Usage:
    pip install playwright
    playwright install chromium
    python3 find_structure_change.py
"""

import asyncio
import re
from datetime import date, timedelta

from playwright.async_api import async_playwright

BASE_URL = "https://www3.parliament.nz"

# Known bounds (inclusive). Adjust if needed.
LOWER_BOUND = date(2026, 3, 31)   # last known OLD structure
UPPER_BOUND = date(2026, 5, 28)   # first known NEW structure

# Days of the week Parliament typically sits (Mon–Thu).
SITTING_DAYS = {0, 1, 2, 3}  # Mon=0 … Thu=3


def build_url(d: date) -> str:
    weekday = d.strftime("%A").lower()
    day = str(d.day)
    month = d.strftime("%B").lower()
    return (
        f"{BASE_URL}/en/pb/daily-progress-in-the-house/"
        f"daily-progress-for-{weekday}-{day}-{month}-{d.year}"
    )


def sitting_days_in_range(start: date, end: date) -> list[date]:
    """Return Mon–Thu dates between start and end (inclusive)."""
    days = []
    d = start
    while d <= end:
        if d.weekday() in SITTING_DAYS:
            days.append(d)
        d += timedelta(days=1)
    return days


def detect_structure(html: str) -> str | None:
    """
    Returns 'new' if <h3><span>…</span></h3> headings are found,
            'old' if plain <h3>…</h3> headings are found,
            None  if no h3 content headings detected (404 / non-sitting day).
    """
    if re.search(r"<h3>\s*<span>", html, re.IGNORECASE):
        return "new"
    if re.search(
        r"<h3>\s*(?:Urgency|Government business|Introduction|Oral questions)",
        html, re.IGNORECASE
    ):
        return "old"
    return None


async def fetch_structure(browser_page, d: date) -> str | None:
    """Fetch a daily progress page and return its structure tag, or None."""
    url = build_url(d)
    try:
        response = await browser_page.goto(
            url, wait_until="domcontentloaded", timeout=20_000
        )
        if response and response.status == 404:
            return None
        html = await browser_page.content()
        return detect_structure(html)
    except Exception as e:
        print(f"    [error] {url}: {e}")
        return None


async def find_valid_near(browser_page, days: list[date], centre_idx: int) -> tuple[int, str] | None:
    """
    Starting from centre_idx, search outward (alternating left/right) until
    we find a date with a detectable structure. Returns (index, structure) or None.
    """
    n = len(days)
    for offset in range(n):
        for sign in (+1, -1):
            idx = centre_idx + sign * offset
            if 0 <= idx < n:
                structure = await fetch_structure(browser_page, days[idx])
                if structure is not None:
                    return idx, structure
    return None


async def binary_search(browser_page, days: list[date]) -> tuple[date, date] | None:
    """
    Binary search over `days` to find the transition point.
    Returns (last_old_date, first_new_date) or None if not found.
    All state is tracked by integer index to avoid the .index() re-lookup bug.
    """
    lo, hi = 0, len(days) - 1

    # Verify the two bounds have different structures
    lo_result = await find_valid_near(browser_page, days, lo)
    hi_result = await find_valid_near(browser_page, days, hi)

    if not lo_result or not hi_result:
        print("Could not verify bounds — check the date range.")
        return None

    lo, lo_struct = lo_result
    hi, hi_struct = hi_result

    print(f"  Lower bound: {days[lo]} → {lo_struct} structure")
    print(f"  Upper bound: {days[hi]} → {hi_struct} structure")

    if lo_struct == hi_struct:
        print(f"Both bounds have the same structure ({lo_struct}). "
              "Widen the search range.")
        return None

    # Invariant: days[lo] is old, days[hi] is new
    last_old_idx = lo
    first_new_idx = hi

    while lo + 1 < hi:
        mid = (lo + hi) // 2
        result = await find_valid_near(browser_page, days, mid)

        if result is None:
            # No valid page anywhere near mid — shouldn't happen, but bail out
            print("    [warning] Could not find any valid page near midpoint; stopping.")
            break

        mid_idx, mid_struct = result
        print(f"    Checked {days[mid_idx]} → {mid_struct}")

        if mid_struct == "old":
            last_old_idx = mid_idx
            lo = mid_idx          # mid_idx is guaranteed > lo (or loop would have ended)
        else:
            first_new_idx = mid_idx
            hi = mid_idx          # mid_idx is guaranteed < hi

        # Safety: if find_valid_near returned an index outside (lo, hi), clamp
        if lo >= hi:
            break

    return days[last_old_idx], days[first_new_idx]


async def main():
    print("=" * 60)
    print("NZ Parliament Daily Progress — Structure Change Finder")
    print("=" * 60)
    print(f"Searching between {LOWER_BOUND} and {UPPER_BOUND}\n")

    days = sitting_days_in_range(LOWER_BOUND, UPPER_BOUND)
    print(f"Candidate sitting days (Mon–Thu): {len(days)}\n")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        browser_page = await browser.new_page()

        print("Running binary search...")
        result = await binary_search(browser_page, days)

        await browser.close()

    print()
    if result:
        last_old, first_new = result
        print("=" * 60)
        print("RESULT")
        print("=" * 60)
        print(f"  Last OLD structure : {last_old}")
        print(f"                       {build_url(last_old)}")
        print(f"  First NEW structure: {first_new}")
        print(f"                       {build_url(first_new)}")
        print()
        delta = (first_new - last_old).days
        print(f"  The structure changed in the {delta}-day gap between these two dates.")
        if delta <= 4:
            print("  These are consecutive sitting days — the deployment happened")
            print("  between those two sessions.")
    else:
        print("Could not determine the changeover date.")


if __name__ == "__main__":
    asyncio.run(main())