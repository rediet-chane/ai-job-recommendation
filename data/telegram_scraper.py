import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl
import pandas as pd
import re
import os

# ============================================
# TELEGRAM SCRAPER WITH BUTTON LINK EXTRACTION
# ============================================

API_ID = 39378710
API_HASH = '80aefba1418ce690c011975d04db5d85'

# Ethiopian job channels
CHANNELS = [
    'hahujobs',
    'ethiojobsofficial',
    'elelanjobs',
    'freelance_ethio',
]

async def scrape_jobs():
    print("📱 Connecting to Telegram...")
    client = TelegramClient('session_name', API_ID, API_HASH)
    await client.start()
    
    print("✅ Connected! Reading job channels...")
    all_jobs = []
    
    for channel_name in CHANNELS:
        try:
            print(f"📥 Reading from @{channel_name}...")
            channel = await client.get_entity(channel_name)
            messages = await client.get_messages(channel, limit=50)
            
            for msg in messages:
                if msg.text and len(msg.text) > 50:
                    job = extract_job_info(msg, channel_name)
                    if job:
                        all_jobs.append(job)
                        print(f"  ✅ Found: {job['title'][:40]}...")
                        
        except Exception as e:
            print(f"⚠️ Couldn't read {channel_name}: {e}")
    
    await client.disconnect()
    return all_jobs

def extract_job_info(message, channel_name):
    """Extract job info including button links"""
    text = message.text
    
    title = extract_title(text)
    company = extract_company(text)
    skills = extract_skills(text)
    message_link = f"https://t.me/{channel_name}/{message.id}"
    
    # Look for button links
    button_links = []
    if message.reply_markup:
        try:
            if hasattr(message.reply_markup, 'rows'):
                for row in message.reply_markup.rows:
                    for button in row.buttons:
                        if hasattr(button, 'url') and button.url:
                            button_links.append(button.url)
        except:
            pass
    
    # Also look for URLs in text
    urls = re.findall(r'https?://[^\s]+', text)
    for url in urls:
        if 't.me' not in url:
            button_links.append(url)
    
    # Determine apply link
    apply_link = None
    if button_links:
        apply_link = button_links[0]
    if not apply_link:
        apply_link = message_link
    
    return {
        'job_id': message.id,
        'title': title,
        'description': text[:1000],
        'required_skills': ', '.join(skills) if skills else 'See description',
        'category': guess_category(text, skills),
        'company': company,
        'channel': f'@{channel_name}',
        'message_link': message_link,
        'apply_link': apply_link,
        'date': str(message.date)[:10],
        'message_id': message.id,
    }

def extract_title(text):
    lines = text.split('\n')
    for line in lines[:5]:
        line = line.strip()
        if 'Job Title:' in line:
            return line.replace('Job Title:', '').strip()
        if 'Position:' in line:
            return line.replace('Position:', '').strip()
        if len(line) > 10 and len(line) < 100:
            return line
    return "Job Position"

def extract_company(text):
    lines = text.split('\n')
    for line in lines[:10]:
        if 'Company:' in line:
            return line.replace('Company:', '').strip()
        if 'PLC' in line or 'SC' in line:
            return line.strip()
    return "Not specified"

def extract_skills(text):
    text_lower = text.lower()
    skills = []
    skill_keywords = {
        'python': ['python', 'django', 'flask'],
        'sql': ['sql', 'mysql', 'database'],
        'javascript': ['javascript', 'react', 'node'],
        'communication': ['communication', 'presentation'],
        'leadership': ['leadership', 'management'],
        'accounting': ['accounting', 'finance'],
        'marketing': ['marketing', 'seo'],
        'design': ['design', 'photoshop', 'figma'],
    }
    for skill, keywords in skill_keywords.items():
        for kw in keywords:
            if kw in text_lower:
                skills.append(skill)
                break
    return list(set(skills))

def guess_category(text, skills):
    text_lower = text.lower()
    if any(s in skills for s in ['architecture', 'design']):
        return 'Architecture/Design'
    if 'engineer' in text_lower:
        return 'Engineering'
    if any(s in skills for s in ['python', 'javascript', 'sql']):
        return 'Technology'
    return 'General'

def save_to_csv(jobs, filename='data/jobs.csv'):
    if not jobs:
        print("❌ No jobs found")
        return
    
    new_df = pd.DataFrame(jobs)
    
    try:
        existing = pd.read_csv(filename)
        combined = pd.concat([existing, new_df], ignore_index=True)
        combined = combined.drop_duplicates(subset=['message_id', 'channel'], keep='last')
    except:
        combined = new_df
    
    combined.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✅ Saved {len(jobs)} new jobs")
    print(f"📊 Total jobs now: {len(combined)}")
    return combined

async def main():
    print("=" * 60)
    print("🤖 TELEGRAM JOB SCRAPER")
    print("=" * 60)
    
    jobs = await scrape_jobs()
    
    if jobs:
        save_to_csv(jobs)
        print(f"\n✅ Done! Found {len(jobs)} jobs")
    else:
        print("❌ No jobs found")

if __name__ == "__main__":
    asyncio.run(main())