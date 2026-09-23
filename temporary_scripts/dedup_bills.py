# dedupe_bills.py
#
# One-off cleanup for the duplicate rows already sitting in the `bills`
# table (see https://github.com/ItsHammy/nzpt-urgency/issues/11).
#
# Root cause: `billsaffected.py` relied on a UNIQUE INDEX on the raw `url`
# column to dedupe, but parliament.nz serves the same bill under multiple
# URL variants (GUID case differs, and `?Tab=history` / `?lang=en` query
# strings come and go), so several rows ended up representing one bill.
#
# This script groups existing rows by a canonicalised URL (same logic now
# used in billsaffected.py going forward), keeps one "best" row per group
# and deletes the rest, so the Bill Viewer stops showing duplicates.
#
# Run this ONCE against the production DB, ideally after taking a backup:
#   cp urgency.sqlite3 urgency.sqlite3.bak
#   python3 dedupe_bills.py
#
# It defaults to a dry run (prints what it would do). Pass --apply to
# actually write the changes.

import argparse
import sqlite3
from collections import defaultdict
from urllib.parse import urlparse

DB_PATH = "/var/www/nzpt/urgency/urgency.sqlite3"


def canonicalise_bill_url(url: str) -> str:
    url = (url or "").strip()
    try:
        parsed = urlparse(url)
    except Exception:
        return url

    scheme = parsed.scheme or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.lower().rstrip("/")

    return f"{scheme}://{netloc}{path}"


def pick_keeper(rows):
    """
    rows: list of dicts with keys id, bill_name, url, tags, mps, desc
    Returns (keeper, losers) where keeper is the row we keep (merging in
    any non-null fields the losers have that the keeper is missing).
    """
    # Prefer the row that already has the most fields filled in, then the
    # lowest id (earliest inserted) as a tiebreaker.
    def score(row):
        filled = sum(
            1 for k in ("tags", "mps", "desc") if row.get(k) not in (None, "")
        )
        return (-filled, row["id"])

    ordered = sorted(rows, key=score)
    keeper = dict(ordered[0])
    losers = ordered[1:]

    for loser in losers:
        for field in ("tags", "mps", "desc", "bill_name"):
            if keeper.get(field) in (None, "") and loser.get(field) not in (None, ""):
                keeper[field] = loser[field]

    # Always store the canonical URL, not whichever variant happened to be
    # on the keeper row.
    keeper["url"] = canonicalise_bill_url(keeper["url"])

    return keeper, losers


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write changes. Without this flag, only prints a report.",
    )
    parser.add_argument("--db", default=DB_PATH, help=f"Path to sqlite DB (default: {DB_PATH})")
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(bills)")
    cols = {row[1] for row in cursor.fetchall()}
    select_cols = ["id", "bill_name", "url"]
    for optional in ("tags", "mps", "desc"):
        if optional in cols:
            select_cols.append(optional)

    cursor.execute(f"SELECT {', '.join(select_cols)} FROM bills")
    rows = [dict(r) for r in cursor.fetchall()]
    print(f"Loaded {len(rows)} rows from `bills`.")

    groups = defaultdict(list)
    for row in rows:
        key = canonicalise_bill_url(row["url"])
        groups[key].append(row)

    dup_groups = {k: v for k, v in groups.items() if len(v) > 1}
    print(f"Found {len(dup_groups)} bills with duplicate rows "
          f"({sum(len(v) for v in dup_groups.values())} rows total, "
          f"{sum(len(v) - 1 for v in dup_groups.values())} to be removed).")

    if not dup_groups:
        print("Nothing to do.")
        return

    for key, group in dup_groups.items():
        keeper, losers = pick_keeper(group)
        loser_ids = [l["id"] for l in losers]
        print(f"\n{keeper['bill_name']!r}")
        print(f"  keep id={keeper['id']}  url={keeper['url']}")
        print(f"  drop ids={loser_ids}")

        if args.apply:
            set_clauses = ", ".join(f"{c} = ?" for c in select_cols if c != "id")
            values = [keeper[c] for c in select_cols if c != "id"] + [keeper["id"]]
            cursor.execute(f"UPDATE bills SET {set_clauses} WHERE id = ?", values)
            cursor.executemany(
                "DELETE FROM bills WHERE id = ?", [(lid,) for lid in loser_ids]
            )

    if args.apply:
        conn.commit()
        print(f"\nApplied. Removed "
              f"{sum(len(v) - 1 for v in dup_groups.values())} duplicate rows.")
    else:
        print("\nDry run only — nothing written. Re-run with --apply to make changes.")

    conn.close()


if __name__ == "__main__":
    main()