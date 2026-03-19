import schedule
import time
import subprocess
import os
from datetime import datetime

# Your exact Python path
PYTHON_PATH = r"C:\Users\Redie\ai-job-recommendation\venv\Scripts\python.exe"
SCRIPT_PATH = r"C:\Users\Redie\ai-job-recommendation\data\telegram_scraper.py"

def run_scraper():
    """Run the Telegram scraper and log results"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] 🕒 Running daily job scraper...")
    
    try:
        # Run the scraper
        result = subprocess.run(
            [PYTHON_PATH, SCRIPT_PATH],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        # Log the results
        with open("scraper_log.txt", "a", encoding="utf-8") as log:
            log.write(f"\n--- {timestamp} ---\n")
            if result.returncode == 0:
                log.write(f"✅ SUCCESS\n")
                log.write(f"Output: {result.stdout[:500]}\n")
            else:
                log.write(f"❌ ERROR (code {result.returncode})\n")
                log.write(f"Error: {result.stderr[:500]}\n")
        
        print(f"[{timestamp}] ✅ Scraper finished!")
        
    except subprocess.TimeoutExpired:
        print(f"[{timestamp}] ❌ Scraper timed out after 5 minutes")
    except Exception as e:
        print(f"[{timestamp}] ❌ Error: {e}")

def main():
    print("=" * 60)
    print("🤖 ETHIOPIAN JOB SCRAPER SCHEDULER")
    print(f"📅 Started at: {datetime.now()}")
    print(f"🐍 Python: {PYTHON_PATH}")
    print(f"📜 Script: {SCRIPT_PATH}")
    print("⏰ Scheduled: 2:00 AM daily")
    print("=" * 60)
    
    # Schedule for 2 AM
    schedule.every().day.at("02:00").do(run_scraper)
    
    # Run once immediately for testing (optional)
    # Uncomment next line to test right now:
    # run_scraper()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()