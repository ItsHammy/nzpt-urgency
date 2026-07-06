"""
new-gen-automation.py
This script automates the subscripts, without needing GH actions or cron jobs.
It will be replaced in the future.

This tool does the following:
1. Runs scrapewebpage.py
2. Runs billcounter.py
3. Runs billsaffected.py
4. Runs billdetails.py
5. Runs shareimagegenerator.py
SOON: 6. Sends a nzpt-bot message with the daily urgency status.

All stdout/stderr (including print() calls from the imported subscripts) are
mirrored to DIR/logs/urgency.log as well as the console.
"""

# Import time/date
import asyncio
import os
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
DIR = "/var/www/nzpt/urgency"
LOG_DIR = "logs/"
LOG_PATH = os.path.join(LOG_DIR, "urgency.log")

os.makedirs(LOG_DIR, exist_ok=True)

_log_file = open(LOG_PATH, "a", buffering=1)  # line-buffered so writes appear promptly


class TimestampedTee:
    """
    Mirrors everything written to stdout/stderr to both the console and a
    log file, prefixing each new line with a timestamp. Works transparently
    for print() calls made in this script AND in any imported subscript
    function, since they all share the same sys.stdout/sys.stderr.
    """

    def __init__(self, *streams):
        self.streams = streams
        self._at_line_start = True

    def write(self, data):
        for chunk in data.splitlines(keepends=True):
            if self._at_line_start and chunk.strip("\n") != "":
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                prefix = f"[{timestamp}] "
            else:
                prefix = ""
            for stream in self.streams:
                stream.write(prefix + chunk)
            self._at_line_start = chunk.endswith("\n")

    def flush(self):
        for stream in self.streams:
            stream.flush()


sys.stdout = TimestampedTee(sys.__stdout__, _log_file)
sys.stderr = TimestampedTee(sys.__stderr__, _log_file)

# ---------------------------------------------------------------------------
# Import Scripts (done after stdout/stderr redirection so any import-time
# prints are also captured)
# ---------------------------------------------------------------------------
from scrapewebpage import main as scrapescript
from billcounter import main as billcounter
from billsaffected import main as billsaffected
from billdetails import scrape_all_bill_details as billdetails
from shareimagegenerator import main as shareimagegenerator


# ---------------------------------------------------------------------------
# Run the scripts
# ---------------------------------------------------------------------------
async def run_step(name, coro_or_func, is_coro=True):
    """Run a single step, logging failures without killing the whole loop."""
    print(f"Running {name}...")
    try:
        if is_coro:
            await coro_or_func()
        else:
            coro_or_func()
    except Exception:
        import traceback
        print(f"ERROR: {name} failed:")
        print(traceback.format_exc())
        return False
    return True


async def schedule():
    while True:
        await run_step("scrapewebpage.py", scrapescript)
        await run_step("billcounter.py", billcounter)
        await run_step("billsaffected.py", billsaffected)
        await run_step("billdetails.py", billdetails)
        await run_step("shareimagegenerator.py", shareimagegenerator, is_coro=False)

        try:
            with open(os.path.join(DIR, "lastupdate.txt"), "w") as f:
                f.write(datetime.now().strftime("%d %B %Y").lstrip("0").replace(" 0", " "))
        except Exception:
            import traceback
            print("ERROR: failed to write lastupdate.txt:")
            print(traceback.format_exc())

        print("All scripts ran. Waiting for the next run...")
        # Wait for 24 hours (86400 seconds)
        await asyncio.sleep(86400)


if __name__ == "__main__":
    asyncio.run(schedule())