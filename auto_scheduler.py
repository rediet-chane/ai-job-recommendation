import schedule
import time
import subprocess
import os
from datetime import datetime

# ============================================
# 🔥 SET IT AND FORGET IT - RUNS FOREVER!
# ============================================
# You only need to create this file ONCE.
# After that, it runs automatically every day at 2 AM.
# Never manually run the scraper again!
# ============================================

# Your exact paths (copy these exactly)
PYTHON_PATH = r"C:\Users\Redie\ai-job-recommendation\venv\Scripts\python.exe"
SCRAPER_PATH = r"C:\Users\Redie\ai-job-recommendation\data\telegram_scraper.py"

def run_scraper():
    """This runs automatically - you never need to touch this!"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] 🤖 Auto-fetching Ethiopian jobs...")
    
    try:
        # This is like typing the command yourself, but automatic!
        result = subprocess.run(
            [PYTHON_PATH, SCRAPER_PATH],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        # Save to log so you can check later
        with open("scraper_log.txt", "a", encoding="utf-8") as log:
            if result.returncode == 0:
                log.write(f"{timestamp} ✅ Success - Jobs updated\n")
                print(f"✅ Jobs updated successfully!")
            else:
                log.write(f"{timestamp} ❌ Error: {result.stderr[:100]}\n")
                print(f"❌ Had an error, check log")
                
    except Exception as e:
        print(f"❌ Error: {e}")

print("=" * 60)
print("🔥 AUTOMATIC JOB SCRAPER - SET IT AND FORGET IT!")
print("=" * 60)
print(f"📅 Started at: {datetime.now()}")
print(f"⏰ Will run EVERY DAY at 2:00 AM automatically")
print(f"📝 Check 'scraper_log.txt' to see what happened")
print("=" * 60)
print("\n✅ THIS WINDOW CAN STAY MINIMIZED FOREVER!")
print("   It will wake up at 2 AM every day by itself.")
print("   Press Ctrl+C if you ever want to stop it.\n")

# Schedule it to run every day at 2 AM
schedule.every().day.at("02:00").do(run_scraper)

# Run forever
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute