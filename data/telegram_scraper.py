import asyncio
from telethon import TelegramClient
from telethon.network import ConnectionTcpAbridged
import pandas as pd
import re
from collections import Counter

# ============================================
# PYTHONANYWHERE-FRIENDLY SCRAPER
# Uses HTTP protocol instead of MTProto
# ============================================

API_ID = 39378710  # Your actual ID
API_HASH = '80aefba1418ce690c011975d04db5d85'  # Your actual hash

# Use HTTP connection instead of default MTProto
CONNECTION = ConnectionTcpAbridged

# Ethiopian job channels
CHANNELS = [
    'hahujobs',
    'ethiojobsofficial',
    'elelanjobs',
    'freelance_ethio',
]

# Skills to look for INSIDE descriptions
SKILL_PATTERNS = {
    'python': ['python', 'django', 'flask', 'pandas'],
    'sql': ['sql', 'mysql', 'postgresql', 'database', 'query', 'db'],
    'javascript': ['javascript', 'js', 'react', 'node', 'vue', 'angular'],
    'java': ['java', 'spring', 'j2ee'],
    'html': ['html', 'css', 'web design', 'frontend'],
    'excel': ['excel', 'spreadsheet', 'sheets'],
    'communication': ['communication', 'verbal', 'written', 'presentation'],
    'management': ['management', 'leadership', 'team lead', 'supervisor'],
    'accounting': ['accounting', 'finance', 'quickbooks', 'peachtree', 'tax'],
    'marketing': ['marketing', 'seo', 'social media', 'advertising'],
    'sales': ['sales', 'business development', 'client'],
    'teaching': ['teaching', 'education', 'training', 'instruction'],
    'design': ['design', 'graphic', 'creative', 'photoshop', 'illustrator'],
    'engineering': ['engineering', 'engineer', 'civil', 'mechanical', 'electrical'],
    'architecture': ['architect', 'architecture', 'drafting', 'autocad', 'revit'],
    'customer service': ['customer service', 'support', 'help desk', 'client service'],
}

async def scrape_jobs():
    print("📱 Connecting to Telegram (using HTTP protocol)...")

    # Use ConnectionTcpAbridged for better compatibility
    client = TelegramClient(
        'session_name',
        API_ID,
        API_HASH,
        connection=CONNECTION
    )

    try:
        await client.start()
        print("✅ Connected! Reading job channels...")

        all_jobs = []

        for channel_name in CHANNELS:
            try:
                print(f"📥 Reading from @{channel_name}...")
                channel = await client.get_entity(channel_name)
                messages = await client.get_messages(channel, limit=100)

                for msg in messages:
                    if msg.text and len(msg.text) > 50:
                        job = extract_job_info(msg.text, channel_name, msg)
                        if job:
                            all_jobs.append(job)
                            print(f"  ✅ Found: {job['title'][:40]}...")

            except Exception as e:
                print(f"⚠️ Couldn't read {channel_name}: {e}")

        await client.disconnect()
        return all_jobs

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return []

def extract_job_info(text, channel_name, message):
    """Extract FULL job information from message"""

    # Extract title
    title = extract_title(text)

    # Extract company name
    company = extract_company(text)

    # Extract application link (if any)
    link = extract_link(text)

    # Extract salary (if mentioned)
    salary = extract_salary(text)

    # Extract skills from description
    skills = find_skills_in_text(text)

    # Determine category
    category = guess_category(text, skills)

    # Get the message link
    message_link = f"https://t.me/{channel_name}/{message.id}"

    return {
        'job_id': message.id,
        'title': title,
        'description': text[:1000],
        'required_skills': ', '.join(skills) if skills else 'See description',
        'category': category,
        'company': company,
        'channel': f'@{channel_name}',
        'message_link': message_link,
        'salary': salary,
        'date': str(message.date)[:10],
        'message_id': message.id,
    }

def extract_link(text):
    """Extract Telegram or external link from message"""
    # Look for t.me links
    tg_link = re.search(r'https?://t\.me/[^\s]+', text)
    if tg_link:
        return tg_link.group()
    # Look for other links
    other_link = re.search(r'https?://[^\s]+', text)
    if other_link:
        return other_link.group()
    return None

def extract_salary(text):
    """Extract salary information"""
    # Look for salary patterns
    patterns = [
        r'salary[:\s]*([^\n]+)',
        r'በደሞዝ[:\s]*([^\n]+)',
        r'ቅጥር[:\s]*([^\n]+)',
        r'(\d+,\d+|\d+)\s*(?:birr|ETB|ብር)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1) if '(' in pattern else match.group(0)
    return "Not specified"

def extract_title(text):
    """Extract job title from message"""
    lines = text.split('\n')

    # Look for common title indicators
    for line in lines[:5]:
        line = line.strip()
        if 'Job Title:' in line:
            return line.replace('Job Title:', '').strip()
        if 'Position:' in line:
            return line.replace('Position:', '').strip()
        if 'Job:' in line:
            return line.replace('Job:', '').strip()

    # If no clear title, use first non-empty line
    for line in lines[:3]:
        line = line.strip()
        if line and len(line) < 100 and not line.startswith('http'):
            return line

    return "Job Opening"

def find_skills_in_text(text):
    """Scan the entire text to find skills"""
    text_lower = text.lower()
    found_skills = []

    # Check each skill pattern
    for skill, patterns in SKILL_PATTERNS.items():
        for pattern in patterns:
            if pattern in text_lower:
                found_skills.append(skill)
                break

    # Remove duplicates
    found_skills = list(set(found_skills))

    # For architecture roles
    if 'architect' in text_lower and 'architecture' not in found_skills:
        found_skills.append('architecture')
    if 'design' in text_lower and 'design' not in found_skills:
        found_skills.append('design')

    return found_skills

def extract_company(text):
    """Extract company name"""
    lines = text.split('\n')
    for line in lines[:10]:
        line = line.strip()
        if 'Company:' in line:
            return line.replace('Company:', '').strip()
        if 'PLC' in line or 'SC' in line:
            return line.strip()
        # Check for email domain
        email_match = re.search(r'@(\w+\.\w+)', line)
        if email_match:
            return email_match.group(1)
    return "Not specified"

def guess_category(text, skills):
    """Guess job category based on skills and text"""
    text_lower = text.lower()

    if any(s in skills for s in ['architecture', 'design']):
        return '🏗️ Architecture/Design'
    if 'engineer' in text_lower or 'engineering' in text_lower:
        return '🔧 Engineering'
    if any(s in skills for s in ['python', 'javascript', 'java', 'html']):
        return '💻 Technology'
    if any(s in skills for s in ['accounting', 'finance']):
        return '💰 Finance'
    if any(s in skills for s in ['marketing', 'sales']):
        return '📈 Marketing'

    return '📌 General'

def save_to_csv(jobs, filename='data/jobs.csv'):
    """Save jobs to CSV, avoiding duplicates"""
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

    # Show skill statistics
    all_skills = []
    for skills in combined['required_skills'].dropna():
        all_skills.extend([s.strip() for s in skills.split(',') if s.strip()])
    common_skills = Counter(all_skills).most_common(5)
    print("📊 Top skills in database:")
    for skill, count in common_skills:
        print(f"   - {skill}: {count} jobs")

    return combined

async def main():
    print("=" * 60)
    print("🤖 ETHIOPIAN JOB SCRAPER")
    print("=" * 60)

    jobs = await scrape_jobs()

    if jobs:
        save_to_csv(jobs)
        print(f"\n✅ Scraping complete! Added {len(jobs)} jobs")
    else:
        print("❌ No jobs found")

if __name__ == "__main__":
    asyncio.run(main())