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
"""

# Import time/date
import asyncio

# Import Scipts
from scrapewebpage import main as scrapescript
from billcounter import main as billcounter
from billsaffected import main as billsaffected
from billdetails import scrape_all_bill_details as billdetails
from shareimagegenerator import main as shareimagegenerator

# Run the scripts
async def schedule():
    while True:
        print("Running scrapewebpage.py...")
        await scrapescript()
        print("Running billcounter.py...")
        await billcounter()
        print("Running billsaffected.py...")
        await billsaffected()
        print("Running billdetails.py...")
        await billdetails()
        print("Running shareimagegenerator.py...")
        await shareimagegenerator()
        print("All scripts ran successfully. Waiting for the next run...")
        # Wait for 24 hours (86400 seconds)
        await asyncio.sleep(86400)

if __name__ == "__main__":
    asyncio.run(schedule())