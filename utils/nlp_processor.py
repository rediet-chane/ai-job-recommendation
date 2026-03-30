import re
import json
from fuzzywuzzy import fuzz

class NLPProcessor:
    def __init__(self):
        self.skill_taxonomy = self.load_taxonomy()
    
    def load_taxonomy(self):
        try:
            with open('data/skill_taxonomy.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def extract_skills(self, text):
        """Extract skills from text"""
        text_lower = text.lower()
        skills = []
        
        for category, skills_dict in self.skill_taxonomy.items():
            for skill, variations in skills_dict.items():
                for variation in variations:
                    if variation in text_lower:
                        skills.append(skill)
                        break
        
        return list(set(skills))
    
    def normalize_skill(self, skill):
        """Normalize skill name (handle typos)"""
        skill_lower = skill.lower().strip()
        
        for category, skills_dict in self.skill_taxonomy.items():
            for std_skill, variations in skills_dict.items():
                if skill_lower == std_skill:
                    return std_skill
                for var in variations:
                    if fuzz.ratio(skill_lower, var) > 85:
                        return std_skill
        
        return skill
    
    def clean_text(self, text):
        """Clean text for processing"""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        return ' '.join(text.split())