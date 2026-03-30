import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
import json
import re

class AIMatcher:
    def __init__(self):
        """Initialize the AI matcher with learning capabilities"""
        self.jobs_df = None
        self.vectorizer = None
        self.job_vectors = None
        self.skill_taxonomy = self.load_taxonomy()
        self.learning_resources = self.load_resources()
        
    def load_taxonomy(self):
        """Load skill taxonomy (the AI's knowledge base)"""
        try:
            with open('data/skill_taxonomy.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return self.get_default_taxonomy()
    
    def get_default_taxonomy(self):
        """Fallback taxonomy if file not found"""
        return {
            "programming": {
                "python": ["python", "py", "django", "flask"],
                "javascript": ["javascript", "js", "react"],
                "sql": ["sql", "mysql", "database"]
            }
        }
    
    def load_resources(self):
        """Load learning resources"""
        try:
            with open('data/learning_resources.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def load_jobs(self, csv_path='data/jobs.csv'):
        """Load jobs and create AI embeddings"""
        self.jobs_df = pd.read_csv(csv_path)
        self.jobs_df = self.jobs_df.fillna('')
        
        # Create rich text for each job
        job_texts = []
        for _, job in self.jobs_df.iterrows():
            text = f"""
            Title: {job['title']}
            Category: {job['category']}
            Skills: {job['required_skills']}
            Description: {job['description']}
            """
            job_texts.append(text)
        
        # Create TF-IDF vectors (this is the AI's understanding)
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.job_vectors = self.vectorizer.fit_transform(job_texts)
        
        print(f"✅ AI Matcher loaded {len(self.jobs_df)} jobs")
        return True
    
    def clean_skills(self, skills):
        """AI-powered skill cleaning with synonym detection"""
        cleaned = []
        for skill in skills:
            skill_lower = skill.lower().strip()
            
            # Check taxonomy for synonyms
            found = False
            for category, skills_dict in self.skill_taxonomy.items():
                for std_skill, variations in skills_dict.items():
                    if skill_lower in variations or skill_lower == std_skill:
                        cleaned.append(std_skill)
                        found = True
                        break
                    # Fuzzy match for typos
                    for var in variations:
                        if fuzz.ratio(skill_lower, var) > 85:
                            cleaned.append(std_skill)
                            found = True
                            break
                if found:
                    break
            
            if not found:
                cleaned.append(skill_lower)
        
        return list(set(cleaned))
    
    def get_recommendations(self, user_skills, top_n=10):
        """Get AI-powered job recommendations"""
        if not user_skills or self.jobs_df is None:
            return []
        
        # Clean skills (AI understands typos)
        cleaned_skills = self.clean_skills(user_skills)
        
        # Create user query
        user_query = ' '.join(cleaned_skills)
        
        # Vectorize user skills
        user_vector = self.vectorizer.transform([user_query])
        
        # Calculate similarity scores
        similarities = cosine_similarity(user_vector, self.job_vectors).flatten()
        
        # Get top matches
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        recommendations = []
        for idx in top_indices:
            if similarities[idx] > 0:
                job = self.jobs_df.iloc[idx]
                
                # Calculate match percentage
                match_percent = round(similarities[idx] * 100, 2)
                
                # Find which skills matched
                job_text = f"{job['title']} {job['description']} {job['required_skills']}".lower()
                matched_skills = [s for s in cleaned_skills if s in job_text]
                
                recommendations.append({
                    'job_id': int(idx),
                    'title': str(job['title']),
                    'category': str(job.get('category', 'General')),
                    'match_score': match_percent,
                    'required_skills': str(job.get('required_skills', '')),
                    'description': str(job.get('description', ''))[:200],
                    'channel': str(job.get('channel', '')),
                    'message_link': str(job.get('message_link', '')),
                    'apply_link': str(job.get('apply_link', '')),
                    'matched_skills': matched_skills[:5],
                    'company': str(job.get('company', ''))
                })
        
        return recommendations
    
    def analyze_skill_gap(self, user_skills, job_id):
        """Analyze skill gaps with AI recommendations"""
        if self.jobs_df is None:
            return []
        
        job = self.jobs_df.iloc[job_id]
        required = [s.strip().lower() for s in str(job.get('required_skills', '')).split(',') if s.strip()]
        user_cleaned = self.clean_skills(user_skills)
        
        gaps = []
        for skill in required:
            if skill and skill not in user_cleaned:
                # Check if similar skill exists
                is_similar = False
                for uskill in user_cleaned:
                    if fuzz.ratio(skill, uskill) > 85:
                        is_similar = True
                        break
                if not is_similar:
                    # Determine priority based on importance
                    if len(required) <= 3:
                        priority = 'High'
                    elif len(required) <= 6:
                        priority = 'Medium'
                    else:
                        priority = 'Low'
                    
                    # Get learning resource if available
                    resource = self.get_learning_resource(skill)
                    
                    gaps.append({
                        'skill': skill.title(),
                        'priority': priority,
                        'learning_url': resource['url'] if resource else f"https://www.google.com/search?q=learn+{skill}",
                        'resource_title': resource['title'] if resource else f"Learn {skill.title()}"
                    })
        
        return gaps
    
    def get_learning_resource(self, skill):
        """Get learning resource for a skill"""
        skill_lower = skill.lower()
        for key, resources in self.learning_resources.items():
            if key in skill_lower or skill_lower in key:
                return resources[0] if resources else None
        return None
    
    def extract_skills_from_cv(self, text):
        """AI-powered skill extraction from CV text"""
        text_lower = text.lower()
        found_skills = []
        
        for category, skills_dict in self.skill_taxonomy.items():
            for skill, variations in skills_dict.items():
                for variation in variations:
                    if variation in text_lower:
                        found_skills.append(skill)
                        break
        
        return list(set(found_skills))
    
    def generate_quiz_questions(self, category=None):
        """Generate AI-powered quiz questions"""
        # This can be expanded to fetch from external APIs
        questions = [
            {
                'id': 1,
                'category': 'Programming',
                'question': 'How would you process a large CSV file that doesn\'t fit in memory?',
                'options': [
                    'Load entire file with pandas.read_csv()',
                    'Use chunksize parameter to process in batches',
                    'Convert to Excel first',
                    'Split the file manually'
                ],
                'correct': 1,
                'skill': 'python',
                'explanation': 'Using chunksize allows processing large files in manageable batches!'
            },
            {
                'id': 2,
                'category': 'Database',
                'question': 'Which SQL command is used to retrieve data?',
                'options': ['INSERT', 'UPDATE', 'SELECT', 'DELETE'],
                'correct': 2,
                'skill': 'sql',
                'explanation': 'SELECT is the command to query and retrieve data!'
            },
            {
                'id': 3,
                'category': 'Machine Learning',
                'question': 'Which algorithm is best for classification problems?',
                'options': ['Linear Regression', 'K-Means Clustering', 'Random Forest', 'Apriori'],
                'correct': 2,
                'skill': 'machine_learning',
                'explanation': 'Random Forest is excellent for classification tasks!'
            },
            {
                'id': 4,
                'category': 'Soft Skills',
                'question': 'A teammate misses deadlines. What\'s the best approach?',
                'options': [
                    'Report to manager immediately',
                    'Privately discuss and offer help',
                    'Ignore it',
                    'Do their work for them'
                ],
                'correct': 1,
                'skill': 'communication',
                'explanation': 'Private, supportive communication is key!'
            },
            {
                'id': 5,
                'category': 'Cloud',
                'question': 'What does IaaS stand for?',
                'options': [
                    'Infrastructure as a Service',
                    'Internet as a Service',
                    'Integration as a Service',
                    'Identity as a Service'
                ],
                'correct': 0,
                'skill': 'aws',
                'explanation': 'IaaS provides virtualized computing resources!'
            }
        ]
        
        if category:
            return [q for q in questions if q['category'].lower() == category.lower()]
        return questions