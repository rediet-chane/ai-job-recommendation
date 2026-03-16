import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class JobRecommender:
    def __init__(self):
        """Initialize the recommender system with beautiful settings"""
        print("🎨 Initializing Job Recommender with AI magic...")
        
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        self.jobs_df = None
        self.job_vectors = None
        
    def load_jobs(self, csv_path='data/jobs.csv'):
        """Load and prepare job dataset with colors"""
        try:
            self.jobs_df = pd.read_csv(csv_path)
            
            # Create rich text corpus
            self.jobs_df['rich_text'] = (
                self.jobs_df['title'].fillna('') + ' ' +
                self.jobs_df['description'].fillna('') + ' ' +
                self.jobs_df['required_skills'].fillna('') + ' ' +
                self.jobs_df['category'].fillna('')
            )
            
            # Vectorize with TF-IDF
            self.job_vectors = self.vectorizer.fit_transform(
                self.jobs_df['rich_text']
            )
            
            print(f"✅ Loaded {len(self.jobs_df)} colorful jobs")
            print(f"📊 Job categories: {self.jobs_df['category'].nunique()}")
            return True
            
        except Exception as e:
            print(f"❌ Error loading jobs: {e}")
            return False
    
    def get_recommendations(self, user_skills, top_n=10):
        """Get beautiful job recommendations with match scores"""
        if self.jobs_df is None:
            return []
        
        if not user_skills:
            return []
        
        # Convert skills to search text
        skills_text = ' '.join(user_skills)
        
        # Vectorize user skills
        user_vector = self.vectorizer.transform([skills_text])
        
        # Calculate similarities
        similarities = cosine_similarity(user_vector, self.job_vectors).flatten()
        
        # Get top indices
        top_indices = similarities.argsort()[-top_n:][::-1]
        
        # Prepare recommendations with rich data
        recommendations = []
        for idx in top_indices:
            if similarities[idx] > 0:
                job = self.jobs_df.iloc[idx]
                
                # Get required skills as list
                required_skills = str(job.get('required_skills', ''))
                
                # Calculate matched skills
                user_skills_set = set(s.lower() for s in user_skills)
                job_skills_set = set(s.lower().strip() for s in required_skills.split(',') if s.strip())
                matched_skills = user_skills_set.intersection(job_skills_set)
                
                recommendations.append({
                    'job_id': int(job.get('job_id', idx)),
                    'title': str(job.get('title', 'Unknown')).replace('🌟', '').replace('📊', '').strip(),
                    'full_title': str(job.get('title', 'Unknown')),
                    'category': str(job.get('category', 'General')),
                    'match_score': round(similarities[idx] * 100, 2),
                    'required_skills': required_skills,
                    'matched_skills': list(matched_skills),
                    'description': str(job.get('description', ''))[:200] + '...',
                    'experience_level': str(job.get('experience_level', 'Any')),
                    'salary': str(job.get('salary_range', 'Not specified')),
                    'remote': str(job.get('remote', 'Hybrid'))
                })
        
        return recommendations
    
    def analyze_skill_gap(self, user_skills, job_id):
        """Analyze missing skills with priority"""
        if self.jobs_df is None:
            return {'missing_skills': [], 'matched_skills': []}
        
        job = self.jobs_df[self.jobs_df['job_id'] == job_id].iloc[0]
        
        # Parse required skills
        required = [s.strip().lower() for s in str(job.get('required_skills', '')).split(',') if s.strip()]
        user_lower = [s.lower() for s in user_skills]
        
        # Find matches and gaps
        matched = []
        missing = []
        
        for skill in required:
            if skill in user_lower:
                matched.append(skill)
            else:
                # Calculate priority
                freq = self.jobs_df['required_skills'].str.lower().str.contains(skill).mean()
                if freq > 0.7:
                    priority = '🔴 High'
                elif freq > 0.4:
                    priority = '🟡 Medium'
                else:
                    priority = '🟢 Low'
                
                missing.append({
                    'skill': skill,
                    'priority': priority
                })
        
        return {
            'missing_skills': missing,
            'matched_skills': matched,
            'total_required': len(required),
            'total_matched': len(matched)
        }

# Test the recommender
if __name__ == "__main__":
    recommender = JobRecommender()
    recommender.load_jobs()
    
    test_skills = ['python', 'sql', 'javascript']
    recs = recommender.get_recommendations(test_skills)
    
    print(f"\n🎯 Top recommendations for {test_skills}:")
    for i, rec in enumerate(recs[:3], 1):
        print(f"{i}. {rec['title']} - {rec['match_score']}% match")