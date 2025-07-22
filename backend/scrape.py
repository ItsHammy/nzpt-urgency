"""

    This tool scrapes from the https://www.parliament.nz/en/pb/daily-progress-in-the-house/ RSS feed, then analyzes each file to count if the govt were in an urgency motion.
    The tool will output to `urgency.sqlite3` with the following schema:
    - `id` (INTEGER PRIMARY KEY): Unique identifier for each record.
    - `date` (TEXT): The date of the sitting.
    - `in_urgency` (INTEGER): Whether the government was in urgency (1) or not (0).
"""

# Imports
import os
import sqlite3
import requests

# Constants
DB_PATH = "urgency.sqlite3"
RSS_FEED_URL = "https://www.parliament.nz/en/highvolumegenericlisting/rss/1667"
CURRENT_GOV_START = "2023-12-03"

# Function to initialize the SQLite database
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
    
# Function to scrape the RSS feed and analyze urgency
def scrape_and_analyze():
    """
    This tool does the following:
    1. Reads RSS_FEED_URL to get information from dates from CURRENT_GOV_START onwards.
    2. For each date, reads the <link href="..."> and checks the content for the phrase "A motion to accord urgency to the following business was agreed to"
    3. If the phrase is found, it records the date and sets in_urgency to 1, otherwise sets it to 0.
    """
    response = requests.get(RSS_FEED_URL)
    if response.status_code != 200:
        print("Failed to fetch RSS feed.")
        return
    
    feed_data = response.text
    entries = feed_data.split('<item>')[1:]  # Split into individual items

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    for entry in entries:
        date_start = entry.find('<pubDate>') + len('<pubDate>')
        date_end = entry.find('</pubDate>')
        date_str = entry[date_start:date_end].strip()

        if date_str < CURRENT_GOV_START:
            continue  # Skip dates before the current government start

        link_start = entry.find('<link>') + len('<link>')
        link_end = entry.find('</link>')
        link_href = entry[link_start:link_end].strip()

        # Fetch the content of the link
        content_response = requests.get(link_href)
        if content_response.status_code != 200:
            print(f"Failed to fetch content from {link_href}.")
            continue
        
        content_text = content_response.text
        in_urgency = 1 if "A motion to accord urgency to the following business was agreed to" in content_text else 0

        cursor.execute("INSERT INTO urgency (date, in_urgency) VALUES (?, ?)", (date_str, in_urgency))

    conn.commit()
    conn.close()
    
