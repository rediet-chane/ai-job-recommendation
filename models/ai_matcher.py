import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
import json

class AIJobMatcher:
    def __init__(self):
        """Initialize with transformer-based AI model"""
        print("🧠 Loading AI embedding model...")
        # Using a lightweight but effective model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.jobs_df = None
        self.job_embeddings = None
        self.job_texts = []
        
    def load_jobs(self, csv_path='data/jobs.csv'):
        """Load jobs and create AI embeddings"""
        self.jobs_df = pd.read_csv(csv_path)
        self.jobs_df = self.jobs_df.fillna('')
        
        # Create rich text for each job
        for _, job in self.jobs_df.iterrows():
            text = f"""
            Title: {job['title']}
            Category: {job['category']}
            Required Skills: {job['required_skills']}
            Description: {job['description']}
            """
            self.job_texts.append(text)
        
        # Create embeddings (this is the AI understanding)
        print("🔮 Creating AI embeddings for jobs...")
        self.job_embeddings = self.model.encode(self.job_texts, show_progress_bar=True)
        
        print(f"✅ Loaded {len(self.jobs_df)} jobs with AI embeddings")
        return True
    
    def extract_skills_ai(self, text):
        """Extract skills using AI and fuzzy matching"""
        from utils.ai_cv_parser import AICVParser
        parser = AICVParser()
        return parser.extract_skills_ai(text)
    
    def get_recommendations(self, user_skills, top_n=10):
        """Get AI-powered job recommendations"""
        if not user_skills or self.jobs_df is None:
            return []
        
        # Create user query
        user_text = f"My skills: {', '.join(user_skills)}"
        
        # Create AI embedding for user
        user_embedding = self.model.encode([user_text])
        
        # Calculate semantic similarity
        similarities = cosine_similarity(user_embedding, self.job_embeddings)[0]
        
        # Get top matches
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        recommendations = []
        for idx in top_indices:
            if similarities[idx] > 0.1:
                job = self.jobs_df.iloc[idx]
                match_percent = round(similarities[idx] * 100, 2)
                
                # Find which skills matched
                job_text = self.job_texts[idx].lower()
                matched = [s for s in user_skills if s.lower() in job_text]
                
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
                    'matched_skills': matched[:5],
                    'ai_explanation': f"AI found {len(matched)} skills matching your profile"
                })
        
        return recommendations
    
    def analyze_skill_gap(self, user_skills, job_id):
        """AI-powered skill gap analysis"""
        if self.jobs_df is None:
            return []
        
        job = self.jobs_df.iloc[job_id]
        job_skills = [s.strip().lower() for s in str(job.get('required_skills', '')).split(',')]
        user_skills_lower = [s.lower() for s in user_skills]
        
        gaps = []
        for skill in job_skills:
            if skill and skill not in user_skills_lower:
                # Check fuzzy similarity
                is_similar = False
                for us in user_skills_lower:
                    if fuzz.ratio(skill, us) > 85:
                        is_similar = True
                        break
                
                if not is_similar:
                    # Determine priority
                    if len(job_skills) <= 3:
                        priority = 'High'
                    elif len(job_skills) <= 6:
                        priority = 'Medium'
                    else:
                        priority = 'Low'
                    
                    gaps.append({
                        'skill': skill.title(),
                        'priority': priority,
                        'learning_url': f"https://www.coursera.org/search?query={skill}"
                    })
        
        return gaps
    
    def generate_quiz_questions(self, skills_detected=None):
        """Generate AI-powered quiz questions"""
        # Base questions
        questions = [
            {
                'id': 1,
                'category': 'Programming',
                'question': 'What does Python use for indentation?',
                'options': ['Braces', 'Spaces/Tabs', 'Keywords', 'Parentheses'],
                'correct': 1,
                'skill': 'python',
                'explanation': 'Python uses indentation (spaces/tabs) to define code blocks!'
            },
            {
                'id': 2,
                'category': 'Database',
                'question': 'Which SQL command retrieves data?',
                'options': ['INSERT', 'UPDATE', 'SELECT', 'DELETE'],
                'correct': 2,
                'skill': 'sql',
                'explanation': 'SELECT is used to query and retrieve data!'
            },
            {
                'id': 3,
                'category': 'Machine Learning',
                'question': 'Which algorithm is best for classification?',
                'options': ['Linear Regression', 'K-Means', 'Random Forest', 'Apriori'],
                'correct': 2,
                'skill': 'machine_learning',
                'explanation': 'Random Forest is excellent for classification tasks!'
            },
            {
                'id': 4,
                'category': 'Soft Skills',
                'question': 'How to handle a conflict with a colleague?',
                'options': ['Ignore', 'Report immediately', 'Private discussion', 'Email chain'],
                'correct': 2,
                'skill': 'communication',
                'explanation': 'Private, supportive communication is key!'
            },
            {
                'id': 5,
                'category': 'Cloud',
                'question': 'What does IaaS stand for?',
                'options': ['Infrastructure as a Service', 'Internet as a Service', 'Integration as a Service', 'Identity as a Service'],
                'correct': 0,
                'skill': 'aws',
                'explanation': 'IaaS provides virtualized computing resources!'
            }
        ]
        
        return questions

# Test
if __name__ == "__main__":
    matcher = AIJobMatcher()
    matcher.load_jobs('../data/jobs.csv')
    recs = matcher.get_recommendations(['python', 'sql'])
    for rec in recs[:3]:
        print(f"{rec['title']} - {rec['match_score']}%")