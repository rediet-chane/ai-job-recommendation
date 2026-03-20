import schedule
import time
import subprocess
import os
from datetime import datetime

# ============================================
# 🔥 DEBUG VERSION - SHOWS REAL ERRORS
# ============================================

PYTHON_PATH = r"C:\Users\Redie\ai-job-recommendation\venv\Scripts\python.exe"
SCRAPER_PATH = r"C:\Users\Redie\ai-job-recommendation\data\telegram_scraper.py"

def run_scraper():
    """This runs automatically and shows REAL errors"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n{'='*50}")
    print(f"[{timestamp}] 🤖 Auto-fetching Ethiopian jobs...")
    print(f"{'='*50}")
    
    try:
        # Run the scraper and capture output
        result = subprocess.run(
            [PYTHON_PATH, SCRAPER_PATH],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300
        )
        
        # Show the output in real time
        if result.stdout:
            print("📤 OUTPUT:")
            print(result.stdout)
        
        if result.stderr:
            print("❌ ERROR:")
            print(result.stderr)
        
        # Log it
        with open("scraper_log.txt", "a", encoding="utf-8") as log:
            if result.returncode == 0:
                log.write(f"{timestamp} ✅ Success\n")
                log.write(f"{result.stdout[:500]}\n")
                print(f"✅ SUCCESS at {timestamp}")
            else:
                log.write(f"{timestamp} ❌ Failed (code {result.returncode})\n")
                log.write(f"{result.stderr}\n")
                print(f"❌ FAILED at {timestamp} - Check log for details")
                
    except subprocess.TimeoutExpired:
        print(f"❌ TIMEOUT - Scraper took too long")
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        with open("scraper_log.txt", "a") as log:
            log.write(f"{timestamp} ❌ Exception: {e}\n")

print("=" * 70)
print("🔥 DEBUG MODE - SHOWING REAL ERRORS")
print("=" * 70)
print(f"📅 Started at: {datetime.now()}")
print(f"⏰ Will run EVERY MINUTE for testing")
print("=" * 70)

# Run every minute for testing
schedule.every().day.at("02:00").do(run_scraper)  # Back to 2 AM
# Run once immediately
run_scraper()

try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\n👋 Stopped by user")