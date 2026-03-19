import asyncio
import csv
from telethon import TelegramClient
import pandas as pd
import os

# ============================================
# STEP 3.1: PASTE YOUR KEYS HERE!
# ============================================

# Go to https://my.telegram.org and get these
API_ID = 39378710 # <--- REPLACE with your actual api_id (just numbers)
API_HASH = '80aefba1418ce690c011975d04db5d85' # <--- REPLACE with your actual api_hash (letters and numbers)

# Ethiopian job channels to watch
CHANNELS = [
    'hahujobs',        # Popular Ethiopian job channel
    'ethiojobsofficial', # Another job channel
    'Elelanjobs',      # Another one [citation:9]
    'freelance_ethio', # Freelance jobs
]

# ============================================
# STEP 3.2: THIS FUNCTION READS JOBS FROM TELEGRAM
# ============================================

async def scrape_jobs():
    print("📱 Connecting to Telegram...")
    
    # Create a Telegram client (like opening the Telegram app)
    client = TelegramClient('session_name', API_ID, API_HASH)
    await client.start()
    
    print("✅ Connected! Now reading job channels...")
    
    all_jobs = []
    
    # Go through each channel one by one
    for channel_name in CHANNELS:
        try:
            print(f"📥 Reading from @{channel_name}...")
            
            # Get the channel
            channel = await client.get_entity(channel_name)
            
            # Get the last 20 messages from this channel
            messages = await client.get_messages(channel, limit=20)
            
            for msg in messages:
                if msg.text and len(msg.text) > 50:  # Only keep long messages (likely jobs)
                    # Save the job info
                    job = {
                        'title': extract_title(msg.text),
                        'company': extract_company(msg.text),
                        'description': msg.text[:300],  # First 300 characters
                        'date': str(msg.date)[:10],  # Just the date part
                        'channel': f'@{channel_name}',
                        'message_id': msg.id,
                    }
                    all_jobs.append(job)
                    print(f"  ✅ Found job: {job['title']}")
                    
        except Exception as e:
            print(f"⚠️ Couldn't read {channel_name}: {e}")
    
    await client.disconnect()
    return all_jobs

# ============================================
# STEP 3.3: HELPER FUNCTIONS TO GUESS JOB TITLES
# ============================================

def extract_title(text):
    """Try to guess the job title from the message"""
    lines = text.split('\n')
    for line in lines[:3]:  # Check first 3 lines
        line = line.strip()
        # Look for common job title words
        if any(word in line.lower() for word in ['job', 'vacancy', 'position', 'hiring', 'need']):
            return line[:50]  # First 50 characters
    return "Job Position"  # Default if we can't find

def extract_company(text):
    """Try to guess the company name"""
    lines = text.split('\n')
    for line in lines[:3]:
        if 'company' in line.lower() or '@' in line:
            return line.strip()[:30]
    return "Unknown Company"

# ============================================
# STEP 3.4: SAVE TO CSV FILE
# ============================================

def save_to_csv(jobs, filename='data/jobs_from_telegram.csv'):
    """Save the jobs to a CSV file"""
    if not jobs:
        print("❌ No jobs found")
        return
    
    df = pd.DataFrame(jobs)
    df.to_csv(filename, index=False)
    print(f"✅ Saved {len(jobs)} jobs to {filename}")
    
    # Also show first few jobs
    print("\n📋 First 3 jobs found:")
    print(df.head(3))
    return df

# ============================================
# STEP 3.5: MAIN FUNCTION - RUN EVERYTHING
# ============================================

async def main():
    print("=" * 50)
    print("🤖 ETHIOPIAN JOB SCRAPER")
    print("=" * 50)
    
    jobs = await scrape_jobs()
    
    if jobs:
        save_to_csv(jobs)
        
        # Optional: Also add to your main jobs.csv
        try:
            main_df = pd.read_csv('data/jobs.csv')
            new_df = pd.DataFrame(jobs)
            combined = pd.concat([main_df, new_df], ignore_index=True)
            combined.to_csv('data/jobs.csv', index=False)
            print(f"✅ Also added to main jobs.csv! Total now: {len(combined)} jobs")
        except:
            print("ℹ️ Couldn't add to main jobs.csv (file might not exist yet)")
    else:
        print("❌ No jobs found. Check your channel names or internet connection.")

# Run the program
if __name__ == "__main__":
    asyncio.run(main())