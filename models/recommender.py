import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os
import re
from utils.nlp_processor import NLPProcessor

class JobRecommender:
    def __init__(self):
        """Initialize the recommender system"""
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True  # Keep this True for consistent vectorization
        )
        self.jobs_df = None
        self.job_vectors = None
        self.skill_vectors = None
        self.nlp = NLPProcessor()
        
    def load_jobs(self, csv_path='data/jobs.csv'):
        """Load and prepare job dataset"""
        self.jobs_df = pd.read_csv(csv_path)
        
        # Create text corpus from job descriptions and skills
        self.jobs_df['combined_text'] = (
            self.jobs_df['description'].fillna('') + ' ' + 
            self.jobs_df['required_skills'].fillna('')
        )
        
        # Also store original skills for display
        if 'required_skills' in self.jobs_df.columns:
            self.jobs_df['skills_list'] = self.jobs_df['required_skills'].apply(
                lambda x: [s.strip() for s in str(x).split(',') if s.strip()]
            )
        
        # Vectorize job descriptions
        self.job_vectors = self.vectorizer.fit_transform(
            self.jobs_df['combined_text'].str.lower()  # Lowercase for vectorization
        )
        
        print(f"Loaded {len(self.jobs_df)} jobs")
        return self.jobs_df
    
    def vectorize_user_skills(self, skills_list):
        """Convert user skills to TF-IDF vector (case-insensitive)"""
        # Normalize skills first
        normalized_skills = self.nlp.preprocess_user_skills(skills_list)
        
        # Convert to lowercase for vectorization
        skills_text = ' '.join([s.lower() for s in normalized_skills])
        
        # Vectorize using same vectorizer
        user_vector = self.vectorizer.transform([skills_text])
        return user_vector, normalized_skills
    
    def get_recommendations(self, user_skills, top_n=10):
        """
        Get job recommendations based on user skills
        user_skills: list of skills or comma-separated string
        top_n: number of recommendations to return
        """
        # Normalize skills (case-insensitive)
        if isinstance(user_skills, str):
            user_skills = [s.strip() for s in user_skills.split(',') if s.strip()]
        
        normalized_skills = self.nlp.preprocess_user_skills(user_skills)
        
        if not normalized_skills:
            return []
        
        # Vectorize user skills
        user_vector, _ = self.vectorize_user_skills(normalized_skills)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(user_vector, self.job_vectors).flatten()
        
        # Get top N indices
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        # Prepare recommendations
        recommendations = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only include matches
                job = self.jobs_df.iloc[idx]
                
                # Format skills for display
                required_skills = job.get('required_skills', '')
                if isinstance(required_skills, str):
                    display_skills = [self.nlp.standardize_skill_format(s.strip()) 
                                     for s in required_skills.split(',') if s.strip()]
                else:
                    display_skills = []
                
                recommendations.append({
                    'job_id': int(job.get('job_id', idx)),
                    'title': job.get('title', 'Unknown'),
                    'category': job.get('category', 'General'),
                    'match_score': round(similarities[idx] * 100, 2),
                    'required_skills_display': ', '.join(display_skills[:5]),
                    'all_skills': display_skills,
                    'description': job.get('description', '')[:200] + '...' if job.get('description') else '',
                    'experience_level': job.get('experience_level', 'Not specified')
                })
        
        return recommendations
    
    def analyze_skill_gap(self, user_skills, job_id):
        """Identify missing skills for a specific job (case-insensitive)"""
        # Find job
        job_mask = self.jobs_df['job_id'].astype(str) == str(job_id)
        if not job_mask.any():
            # Try integer comparison
            job_mask = self.jobs_df['job_id'] == int(job_id)
        
        if not job_mask.any():
            return []
        
        job = self.jobs_df[job_mask].iloc[0]
        
        # Normalize user skills
        if isinstance(user_skills, str):
            user_skills = [s.strip() for s in user_skills.split(',') if s.strip()]
        
        normalized_user_skills = [s.lower().strip() for s in self.nlp.preprocess_user_skills(user_skills)]
        
        # Extract required skills (case-insensitive)
        required_skills_raw = str(job.get('required_skills', ''))
        required_skills = []
        
        for skill in required_skills_raw.split(','):
            skill_clean = skill.strip()
            if skill_clean:
                required_skills.append(skill_clean)
        
        # Find gaps
        missing_skills = []
        matched_skills = []
        
        for req_skill in required_skills:
            req_skill_lower = req_skill.lower().strip()
            
            # Check if user has this skill (case-insensitive)
            skill_found = False
            for user_skill in normalized_user_skills:
                if user_skill in req_skill_lower or req_skill_lower in user_skill:
                    skill_found = True
                    matched_skills.append(self.nlp.standardize_skill_format(req_skill))
                    break
            
            if not skill_found:
                # Determine priority based on job requirements
                if len(required_skills) < 5:
                    priority = 'High'
                elif len(required_skills) < 8:
                    priority = 'Medium'
                else:
                    priority = 'Low'
                
                missing_skills.append({
                    'skill': self.nlp.standardize_skill_format(req_skill),
                    'priority': priority
                })
        
        return {
            'missing_skills': missing_skills,
            'matched_skills': matched_skills,
            'total_required': len(required_skills),
            'total_matched': len(matched_skills)
        }
    
    def save_model(self, path='models/job_recommender.pkl'):
        """Save the trained model"""
        joblib.dump({
            'vectorizer': self.vectorizer,
            'jobs_df': self.jobs_df,
            'job_vectors': self.job_vectors
        }, path)
    
    def load_model(self, path='models/job_recommender.pkl'):
        """Load a trained model"""
        if os.path.exists(path):
            data = joblib.load(path)
            self.vectorizer = data['vectorizer']
            self.jobs_df = data['jobs_df']
            self.job_vectors = data['job_vectors']
            return True
        return False

# Test the recommender
if __name__ == "__main__":
    recommender = JobRecommender()
    recommender.load_jobs()
    
    # Test with various skill formats
    test_cases = [
        "python, SQL, JAVAscript",
        ["PYTHON", "Machine Learning", "API"],
        "HTML, CSS, JS"
    ]
    
    for test_skills in test_cases:
        print(f"\nTesting: {test_skills}")
        recs = recommender.get_recommendations(test_skills, top_n=3)
        
        for i, rec in enumerate(recs, 1):
            print(f"{i}. {rec['title']} - {rec['match_score']}% match")
            print(f"   Required: {rec['required_skills_display']}")