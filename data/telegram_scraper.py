import asyncio
import csv
from telethon import TelegramClient
import pandas as pd
import os
import re
from amharic_text_processor import Pipeline
from amharic_text_processor.processors import (
    WhitespaceNormalizer,
    PunctuationNormalizer,
    UnicodeNormalizer,
    CharacterRemapper,
)

# ============================================
# AMHARIC JOB SCRAPER
# ============================================

API_ID = 28759123  # Your actual ID
API_HASH = '9a8b7c6d5e4f3g2h1i'  # Your actual hash

# Ethiopian job channels (many post in Amharic)
CHANNELS = [
    'hahujobs',        # Posts in Amharic & English
    'ethiojobsofficial', 
    'elelanjobs',       # Often posts in Amharic
    'freelance_ethio',
    'mertteka',         # Amharic job posts
    'shegerjobs',       # Amharic job posts
]

# Create Amharic text processing pipeline
amharic_pipeline = Pipeline([
    UnicodeNormalizer(),        # Normalize Unicode characters
    CharacterRemapper(),        # Normalize Ethiopic variants (ሠ->ሰ, ዐ->አ)
    PunctuationNormalizer(),    # Unify punctuation
    WhitespaceNormalizer(),     # Clean up spaces
])

# Amharic keywords for job detection
AMHARIC_JOB_KEYWORDS = [
    'ሥራ', 'ቀጥሮ', 'ቀጣሪ', 'ባንክ', 'ኩባንያ',  # job, hire, company
    'ፈልጎታል', 'ፈልጎ', 'ይፈልጋል',           # looking for
    'ተፈላጊ', 'ቀጥሮታል', 'ቀጣሪ ይፈልጋል',     # wanted, hiring
    'ክፍት ቦታ', 'የሥራ ቦታ',                 # vacancy, job position
]

# Amharic skill keywords
AMHARIC_SKILLS = {
    'ሶፍትዌር': 'software',
    'ፕሮግራሚንግ': 'programming',
    'ኮምፒውተር': 'computer',
    'ዳታ': 'data',
    'አካውንቲንግ': 'accounting',
    'ፋይናንስ': 'finance',
    'ማርኬቲንግ': 'marketing',
    'ሽያጭ': 'sales',
    'ኢንጂነር': 'engineer',
    'ቴክኒሻን': 'technician',
    'አስተዳዳሪ': 'manager',
    'ረዳት': 'assistant',
}

async def scrape_jobs():
    print("📱 Connecting to Telegram...")
    client = TelegramClient('session_name', API_ID, API_HASH)
    await client.start()
    
    print("✅ Connected! Now reading Amharic job channels...")
    all_jobs = []
    
    for channel_name in CHANNELS:
        try:
            print(f"📥 Reading from @{channel_name}...")
            channel = await client.get_entity(channel_name)
            messages = await client.get_messages(channel, limit=30)
            
            for msg in messages:
                if msg.text and len(msg.text) > 50:
                    # Process Amharic text through the pipeline
                    cleaned_text = amharic_pipeline.apply(msg.text)["text"]
                    
                    # Check if it's a job posting (Amharic or English)
                    if is_job_posting(cleaned_text):
                        job = extract_amharic_job_info(cleaned_text, channel_name, msg)
                        all_jobs.append(job)
                        print(f"  ✅ Found job: {job['title'][:50]}...")
                    
        except Exception as e:
            print(f"⚠️ Couldn't read {channel_name}: {e}")
    
    await client.disconnect()
    return all_jobs

def is_job_posting(text):
    """Detect if message is a job posting (supports Amharic & English)"""
    text_lower = text.lower()
    
    # Check for Amharic job keywords
    for keyword in AMHARIC_JOB_KEYWORDS:
        if keyword in text:
            return True
    
    # Check for English job keywords
    english_keywords = ['job', 'vacancy', 'hiring', 'position', 'recruitment']
    for keyword in english_keywords:
        if keyword in text_lower:
            return True
    
    return False

def extract_amharic_job_info(text, channel, message):
    """Extract job information from mixed Amharic/English text"""
    
    # Try to find job title - look for patterns
    title = "የሥራ ቦታ"  # Default: "Job Position" in Amharic
    
    # Look for lines that might contain job titles
    lines = text.split('\n')
    for line in lines[:5]:
        line = line.strip()
        if len(line) > 10 and len(line) < 100:
            # If line contains job keywords, it might be the title
            if any(kw in line for kw in AMHARIC_JOB_KEYWORDS + ['job', 'position']):
                title = line[:100]
                break
    
    # Extract skills (both Amharic and English)
    skills = []
    text_lower = text.lower()
    
    # Check Amharic skills
    for am_skill, en_skill in AMHARIC_SKILLS.items():
        if am_skill in text:
            skills.append(en_skill)
    
    # Check English skills
    english_skills = ['python', 'sql', 'excel', 'word', 'powerpoint', 'communication']
    for skill in english_skills:
        if skill in text_lower:
            skills.append(skill)
    
    # Try to find company name
    company = "ኩባንያ"  # Default: "Company" in Amharic
    company_patterns = [
        r'(?:ኩባንያ|ድርጅት|ተቋም)[:\s]+([^\n]+)',  # Amharic patterns
        r'(?:company|organization)[:\s]+([^\n]+)',  # English patterns
        r'@(\w+)'  # Telegram username
    ]
    for pattern in company_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            company = match.group(1).strip()[:50]
            break
    
    return {
        'title': title,
        'company': company,
        'description': text[:500],
        'required_skills': ', '.join(skills) if skills else 'ተዛማጅ ክህሎቶች',  # "Related skills" in Amharic
        'category': guess_category_amharic(text),
        'experience_level': guess_experience_amharic(text),
        'date': str(message.date)[:10],
        'channel': f'@{channel}',
        'message_id': message.id,
    }

def guess_category_amharic(text):
    """Guess job category from Amharic/English text"""
    categories = {
        '💻 ቴክኖሎጂ': ['ሶፍትዌር', 'ፕሮግራም', 'ኮምፒውተር', 'ዳታ', 'software', 'developer', 'it'],
        '📊 ቢዝነስ': ['አካውንቲንግ', 'ፋይናንስ', 'ማርኬቲንግ', 'ሽያጭ', 'business', 'marketing'],
        '🎨 ዲዛይን': ['ዲዛይን', 'ግራፊክ', 'design', 'graphic'],
        '📚 ትምህርት': ['መምህር', 'ትምህርት', 'teacher', 'education'],
        '🏗️ ኢንጂነሪንግ': ['ኢንጂነር', 'ሲቪል', 'ሜካኒካል', 'engineer', 'civil'],
    }
    
    for cat, keywords in categories.items():
        for keyword in keywords:
            if keyword in text:
                return cat
    
    return '📌 አጠቃላይ'

def guess_experience_amharic(text):
    """Guess experience level from Amharic/English text"""
    if re.search(r'(ጀማሪ|አዲስ|entry|junior|fresh|0|no experience)', text, re.IGNORECASE):
        return 'ጀማሪ'
    elif re.search(r'(መካከለኛ|mid|intermediate|2-5)', text, re.IGNORECASE):
        return 'መካከለኛ'
    elif re.search(r'(ከፍተኛ|ሲኒየር|senior|lead|manager|5\+)', text, re.IGNORECASE):
        return 'ከፍተኛ'
    else:
        return 'ጀማሪ'

def save_to_csv(jobs, filename='data/jobs_from_telegram.csv'):
    """Save jobs to CSV with Amharic support"""
    if not jobs:
        print("❌ No jobs found")
        return
    
    # Make sure to handle Amharic text properly
    df = pd.DataFrame(jobs)
    
    # Save with UTF-8 encoding to preserve Amharic characters
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"✅ Saved {len(jobs)} jobs to {filename}")
    
    # Also append to main jobs file
    try:
        main_df = pd.read_csv('data/jobs.csv', encoding='utf-8')
        combined = pd.concat([main_df, df], ignore_index=True)
        combined.to_csv('data/jobs.csv', index=False, encoding='utf-8-sig')
        print(f"✅ Added to main jobs.csv! Total: {len(combined)} jobs")
    except Exception as e:
        print(f"ℹ️ Couldn't add to main jobs.csv: {e}")
    
    return df

async def main():
    print("=" * 60)
    print("🤖 የኢትዮጵያ ሥራ ሰብሳቢ (Ethiopian Job Scraper)")
    print("=" * 60)
    
    jobs = await scrape_jobs()
    
    if jobs:
        save_to_csv(jobs)
        print(f"\n📊 ጠቅላላ የተገኙ ሥራዎች: {len(jobs)}")
    else:
        print("❌ ምንም ሥራ አልተገኘም")

if __name__ == "__main__":
    asyncio.run(main())