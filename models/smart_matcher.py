import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz
import re

class SmartMatcher:
    def __init__(self):
        self.jobs_df = None
        self.skill_map = {
            'py': 'python', 'pyton': 'python', 'pythn': 'python',
            'js': 'javascript', 'javascrip': 'javascript',
            'sql': 'sql', 'sequel': 'sql',
            'excel': 'excel', 'xls': 'excel',
            'html': 'html', 'css': 'css',
            'comm': 'communication', 'comms': 'communication',
            'lead': 'leadership', 'mgmt': 'management',
            'arch': 'architecture', 'architect': 'architecture',
            'design': 'design', 'desgn': 'design',
            'dev': 'development', 'devs': 'development'
        }
    
    def load_jobs(self, csv_path='data/jobs.csv'):
        self.jobs_df = pd.read_csv(csv_path)
        self.jobs_df = self.jobs_df.fillna('')
        # Create search text
        self.jobs_df['search_text'] = (
            self.jobs_df['title'].str.lower() + ' ' +
            self.jobs_df['required_skills'].str.lower() + ' ' +
            self.jobs_df['description'].str.lower()
        )
        print(f"✅ Loaded {len(self.jobs_df)} jobs")
        return True
    
    def clean_skills(self, skills):
        cleaned = []
        for skill in skills:
            s = skill.lower().strip()
            if s in self.skill_map:
                cleaned.append(self.skill_map[s])
            else:
                best_match = None
                best_score = 0
                for key, val in self.skill_map.items():
                    score = fuzz.ratio(s, key)
                    if score > 80 and score > best_score:
                        best_score = score
                        best_match = val
                cleaned.append(best_match if best_match else s)
        return list(set(cleaned))
    
    def get_recommendations(self, user_skills, top_n=10):
        if not user_skills or self.jobs_df is None:
            return []
        
        cleaned_skills = self.clean_skills(user_skills)
        
        results = []
        for idx, job in self.jobs_df.iterrows():
            job_text = job['search_text']
            matched_skills = []
            match_count = 0
            
            # Count matching skills
            for skill in cleaned_skills:
                if skill in job_text:
                    match_count += 1
                    matched_skills.append(skill)
                else:
                    # Check fuzzy match
                    for word in job_text.split()[:100]:
                        if fuzz.ratio(skill, word) > 85:
                            match_count += 0.5
                            matched_skills.append(skill)
                            break
            
            # Calculate realistic percentage
            total_skills = len(cleaned_skills)
            if total_skills > 0:
                percentage = min(100, int((match_count / total_skills) * 100))
            else:
                percentage = 0
            
            # Boost if skills appear in title
            title = job['title'].lower()
            for skill in cleaned_skills:
                if skill in title:
                    percentage = min(100, percentage + 15)
            
            results.append({
                'idx': idx,
                'percentage': percentage,
                'matched': matched_skills,
                'job': job
            })
        
        # Sort by percentage
        results.sort(key=lambda x: x['percentage'], reverse=True)
        
        recommendations = []
        for r in results[:top_n]:
            if r['percentage'] > 0:
                job = r['job']
                channel = str(job.get('channel', '')) if pd.notna(job.get('channel', '')) else ''
                message_link = str(job.get('message_link', '')) if pd.notna(job.get('message_link', '')) else ''
                
                recommendations.append({
                    'job_id': int(r['idx']),
                    'title': str(job['title']),
                    'category': str(job.get('category', 'General')),
                    'match_score': r['percentage'],
                    'required_skills': str(job.get('required_skills', '')),
                    'description': str(job.get('description', ''))[:150],
                    'channel': channel,
                    'message_link': message_link,
                    'matched_skills': r['matched']
                })
        
        return recommendations

if __name__ == "__main__":
    matcher = SmartMatcher()
    matcher.load_jobs('../data/jobs.csv')
    recs = matcher.get_recommendations(['python', 'sql'])
    for rec in recs[:3]:
        print(f"{rec['title']} - {rec['match_score']}% - Link: {rec['message_link']}")