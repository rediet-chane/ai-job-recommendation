import asyncio
from telethon import TelegramClient
from telethon.tl.types import MessageEntityUrl, MessageEntityTextUrl
import pandas as pd
import re

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
    
    # Extract title
    title = extract_title(text)
    
    # Extract company
    company = extract_company(text)
    
    # Extract skills
    skills = extract_skills(text)
    
    # Get the message link (always available)
    message_link = f"https://t.me/{channel_name}/{message.id}"
    
    # LOOK FOR BUTTON LINKS IN THE MESSAGE
    button_links = []
    
    # Check if message has reply markup (buttons)
    if message.reply_markup:
        try:
            # For inline keyboard buttons
            if hasattr(message.reply_markup, 'rows'):
                for row in message.reply_markup.rows:
                    for button in row.buttons:
                        if hasattr(button, 'url') and button.url:
                            button_links.append({
                                'text': button.text,
                                'url': button.url
                            })
                        elif hasattr(button, 'data'):
                            # This is a callback button, not a URL
                            pass
        except Exception as e:
            print(f"  ⚠️ Could not parse buttons: {e}")
    
    # Also look for URLs in the text (as fallback)
    urls = re.findall(r'https?://[^\s]+', text)
    for url in urls:
        if 't.me' not in url:  # Skip internal Telegram links
            button_links.append({'text': 'External Link', 'url': url})
    
    # Determine which link to use as the primary apply link
    apply_link = None
    for link in button_links:
        if 'apply' in link['text'].lower() or 'apply' in link['url'].lower():
            apply_link = link['url']
            break
    
    # If no apply button found, use the first external link
    if not apply_link and button_links:
        apply_link = button_links[0]['url']
    
    # If still no link, use the message link (user can see full post)
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
        'apply_link': apply_link,  # This is the actual apply button link!
        'button_links': str(button_links),  # Store all buttons for debugging
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
        'engineering': ['engineering', 'engineer'],
        'architecture': ['architecture', 'architect', 'autocad']
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
    if any(s in skills for s in ['accounting', 'finance']):
        return 'Finance'
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
    
    # Show sample of apply links
    sample = combined[combined['apply_link'].notna()].head(3)
    if len(sample) > 0:
        print("\n📎 Sample Apply Links:")
        for _, row in sample.iterrows():
            print(f"   {row['title'][:40]}... → {row['apply_link'][:60]}")
    
    return combined

async def main():
    print("=" * 60)
    print("🤖 TELEGRAM JOB SCRAPER (WITH BUTTON LINKS)")
    print("=" * 60)
    
    jobs = await scrape_jobs()
    
    if jobs:
        save_to_csv(jobs)
        print(f"\n✅ Done! Found {len(jobs)} jobs with apply links")
    else:
        print("❌ No jobs found")

if __name__ == "__main__":
    asyncio.run(main())