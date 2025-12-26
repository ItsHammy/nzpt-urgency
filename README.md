# nzpt-urgency
Is the govt in urgency?
This webtool tracks the current state of the NZ govt. It counts how many days the govt has been in urgency.

## What's here?
backend/
- Scraping and analysis of parliament.nz to determine if the govt is in urgency.

web/
- Files for the webtool available on nzpt.cjs.nz

## How does the tool work?
The tool runs a scrape daily at 4am NZT. It runs in three stages:
- At 4am, the server runs scrape-headless.py, which takes the RSS feed, and reads the last 20 daily progress in the house for any Urgency motions.
- At 4:15am, the server runs billsaffected.py and billcounter.py. billsaffected takes 5 minutes to find and list all the bills affected by the urgency motions. billcounter starts a process that counts all the unique bills this parliament has considered. This process takes about 10 minutes,
- The final stage starts at 4:23am and finds the bill details for the billviewer using billdetails.py