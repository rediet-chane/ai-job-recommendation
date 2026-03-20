import schedule
import time
import subprocess
import os
from datetime import datetime

def run_scraper():
    print(f"[{datetime.now()}] Running job scraper...")
    try:
        result = subprocess.run(
            ["python", "data/telegram_scraper.py"],
            capture_output=True,
            text=True,
            timeout=300
        )
        with open("scraper_log.txt", "a") as log:
            log.write(f"{datetime.now()} - {'SUCCESS' if result.returncode == 0 else 'FAILED'}\n")
    except Exception as e:
        print(f"Error: {e}")

schedule.every().day.at("02:00").do(run_scraper)
print("Scheduler running. Will run daily at 2 AM")
while True:
    schedule.run_pending()
    time.sleep(60)