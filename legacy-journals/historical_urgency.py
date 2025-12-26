# historical_urgency.py
#
# Parse Sessional Journals PDFs for Parliaments 48–51 and compute:
#   - sitting days in urgency
#   - distinct bills affected by urgency
#
# Output: append lines like
#   48,11,125
# to results.txt

import os
import re
import pdfplumber


PDF_DIR = "pdf"
RESULTS_PATH = "results.txt"

# Parliament -> list of PDF filenames (relative to PDF_DIR)
PARLIAMENT_PDFS = {
    48: ["48-1.pdf", "48-2.pdf"],   # 48th split across two files
    49: ["49-1.pdf", "49-2.pdf"],   # 49th split across two files
    50: ["50.pdf"],
    51: ["51.pdf"],
}

# Regex for a date line like "Wednesday, 21 December 2011"
DATE_PATTERN = re.compile(
    r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday),\s+\d{1,2}\s+[A-Za-z]+\s+\d{4}",
    re.MULTILINE,
)

# Phrase signalling an urgency motion
URGENCY_PHRASE_PATTERN = re.compile(r"That urgency be accorded", re.IGNORECASE)

# Within an urgency block, approximate bill titles:
# capture sentences/clauses containing "Bill" up to a semicolon, newline, or period.
BILL_TITLE_PATTERN = re.compile(
    r"([A-Z][^\n;:.]*?\bBill\b[^\n;:.]*)",
    re.IGNORECASE,
)


def extract_text_for_parliament(pnum: int) -> str:
    """
    Concatenate text from all PDFs for a parliament into a single string.
    """
    pdf_files = PARLIAMENT_PDFS[pnum]
    chunks = []

    for fname in pdf_files:
        path = os.path.join(PDF_DIR, fname)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing PDF for Parliament {pnum}: {path}")
        print(f"Reading {path} ...")
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                txt = page.extract_text() or ""
                chunks.append(txt)

    return "\n".join(chunks)


def analyze_parliament(pnum: int):
    """
    Return (urgency_days, distinct_bill_count) for a parliament.
    Deduplicates bills by title string within that parliament.
    """
    text = extract_text_for_parliament(pnum)

    # Find all date markers (one per Daily Progress section)
    matches = list(DATE_PATTERN.finditer(text))
    if not matches:
        print(f"Warning: no date headings found for Parliament {pnum}")
        return 0, 0

    urgency_days = 0
    bills_seen = set()

    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        day_text = text[start:end]

        if not URGENCY_PHRASE_PATTERN.search(day_text):
            continue  # no urgency that day

        urgency_days += 1

        # For each urgency block that day, extract bills
        # We take text from each occurrence of the phrase until the next one or end of the day.
        day_urgency_pattern = re.compile(
            r"(That urgency be accorded.*?)(?=That urgency be accorded|$)",
            re.IGNORECASE | re.DOTALL,
        )

        for urg_match in day_urgency_pattern.finditer(day_text):
            block = urg_match.group(1)

            # Find bill-like phrases
            for bill_match in BILL_TITLE_PATTERN.finditer(block):
                raw_title = bill_match.group(1)
                if not raw_title:
                    continue

                # Normalise whitespace and trailing punctuation
                title = " ".join(raw_title.split()).strip(" ;:,.")
                # Require 'bill' in the title to reduce false positives
                if "bill" not in title.lower():
                    continue

                bills_seen.add(title)

    return urgency_days, len(bills_seen)


def main():
    for pnum in [48, 49, 50, 51]:
        print(f"Analyzing Parliament {pnum} ...")
        try:
            urgency_days, bill_count = analyze_parliament(pnum)
        except Exception as e:
            print(f"Error analyzing Parliament {pnum}: {e}")
            continue

        line = f"{pnum},{urgency_days},{bill_count}\n"
        print(f"  Result: {line.strip()}")

        # Append to results.txt
        with open(RESULTS_PATH, "a", encoding="utf-8") as f:
            f.write(line)


if __name__ == "__main__":
    main()