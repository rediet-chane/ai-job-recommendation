import re

class NLPProcessor:
    def __init__(self):
        self.skill_keywords = {
            'python': ['python', 'django', 'flask'],
            'sql': ['sql', 'mysql', 'database'],
            'javascript': ['javascript', 'react', 'node'],
            'communication': ['communication', 'presentation'],
            'leadership': ['leadership', 'management'],
            'accounting': ['accounting', 'finance', 'quickbooks'],
            'marketing': ['marketing', 'seo', 'social media'],
            'design': ['design', 'photoshop', 'figma'],
            'engineering': ['engineering', 'engineer', 'civil', 'mechanical'],
            'architecture': ['architecture', 'architect', 'autocad', 'revit']
        }
    
    def extract_skills(self, text):
        """Extract skills from text"""
        text_lower = text.lower()
        found_skills = []
        for skill, keywords in self.skill_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    found_skills.append(skill)
                    break
        return list(set(found_skills))
    
    def clean_text(self, text):
        """Clean text for processing"""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        return ' '.join(text.split())

# Test
if __name__ == "__main__":
    nlp = NLPProcessor()
    print(nlp.extract_skills("I know Python and SQL"))