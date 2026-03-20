import time
from datetime import datetime
import subprocess

print(f"[{datetime.now()}] Scheduler started")
while True:
    if datetime.now().hour == 2 and datetime.now().minute == 0:
        print(f"[{datetime.now()}] Running scraper...")
        subprocess.run(["python", "data/telegram_scraper.py"])
        time.sleep(60)
    time.sleep(30)