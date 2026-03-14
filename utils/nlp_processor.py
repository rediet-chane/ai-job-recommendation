import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import json

class NLPProcessor:
    def __init__(self):
        """Initialize NLP tools"""
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Simple skill taxonomy (we'll expand this later)
        self.skill_taxonomy = {
            "programming": {
                "python": ["python", "py", "django", "flask"],
                "javascript": ["javascript", "js", "react", "node"],
                "java": ["java", "spring", "j2ee"],
                "sql": ["sql", "mysql", "postgresql", "database"]
            },
            "data_science": {
                "machine_learning": ["machine learning", "ml", "ai"],
                "data_analysis": ["data analysis", "analytics", "statistics"],
                "visualization": ["visualization", "tableau", "power bi"]
            },
            "soft_skills": {
                "communication": ["communication", "verbal", "written"],
                "teamwork": ["teamwork", "collaboration", "team player"],
                "problem_solving": ["problem solving", "analytical", "critical thinking"]
            }
        }
    
    def clean_text(self, text):
        """Basic text cleaning"""
        if not isinstance(text, str):
            return ""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        text = ' '.join(text.split())
        return text
    
    def extract_skills(self, text):
        """Extract skills from text"""
        text_lower = text.lower()
        found_skills = []
        
        for category, skills in self.skill_taxonomy.items():
            for skill, variations in skills.items():
                for variation in variations:
                    if variation in text_lower:
                        found_skills.append(skill)
                        break
        
        return list(set(found_skills))
    
    def preprocess_job_description(self, description):
        """Process job description"""
        cleaned = self.clean_text(description)
        skills = self.extract_skills(description)
        
        return {
            'processed_text': cleaned,
            'extracted_skills': skills
        }

# Test it
if __name__ == "__main__":
    processor = NLPProcessor()
    test = "Looking for Python developer with SQL and machine learning"
    result = processor.preprocess_job_description(test)
    print("Extracted skills:", result['extracted_skills'])