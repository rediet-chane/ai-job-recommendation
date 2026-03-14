import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import os

class JobRecommender:  # Make sure this is exactly "JobRecommender" (capital J, capital R)
    def __init__(self):
        """Initialize the recommender system"""
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.jobs_df = None
        self.job_vectors = None
        
    def load_jobs(self, csv_path='data/jobs.csv'):
        """Load and prepare job dataset"""
        try:
            self.jobs_df = pd.read_csv(csv_path)
            
            # Create text corpus from job descriptions and skills
            self.jobs_df['combined_text'] = (
                self.jobs_df['description'].fillna('') + ' ' + 
                self.jobs_df['required_skills'].fillna('')
            )
            
            # Vectorize job descriptions
            self.job_vectors = self.vectorizer.fit_transform(
                self.jobs_df['combined_text']
            )
            
            print(f"✅ Loaded {len(self.jobs_df)} jobs")
            return True
        except Exception as e:
            print(f"❌ Error loading jobs: {e}")
            return False
    
    def get_recommendations(self, user_skills, top_n=10):
        """
        Get job recommendations based on user skills
        """
        if self.jobs_df is None:
            return []
        
        # Convert skills list to text
        skills_text = ' '.join(user_skills)
        
        # Vectorize user skills
        user_vector = self.vectorizer.transform([skills_text])
        
        # Calculate similarity
        similarities = cosine_similarity(user_vector, self.job_vectors).flatten()
        
        # Get top N indices
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        # Prepare recommendations
        recommendations = []
        for idx in top_indices:
            if similarities[idx] > 0:
                job = self.jobs_df.iloc[idx]
                recommendations.append({
                    'job_id': int(job.get('job_id', idx)),
                    'title': str(job.get('title', 'Unknown')),
                    'category': str(job.get('category', 'General')),
                    'match_score': round(similarities[idx] * 100, 2),
                    'required_skills': str(job.get('required_skills', '')),
                    'description': str(job.get('description', ''))[:200] + '...'
                })
        
        return recommendations

# Test it
if __name__ == "__main__":
    recommender = JobRecommender()
    print("✅ JobRecommender class created successfully!")