import spacy
import re
import PyPDF2
import docx
import io

class AICVParser:
    def __init__(self):
        """Initialize with spaCy NLP model"""
        print("🧠 Loading AI NLP model...")
        try:
            self.nlp = spacy.load("en_core_web_lg")
        except:
            self.nlp = spacy.load("en_core_web_sm")
        
        # Skill patterns for NER
        self.skill_patterns = self.load_skill_patterns()
    
    def load_skill_patterns(self):
        """Load skill patterns from taxonomy"""
        return {
            'programming': ['python', 'java', 'javascript', 'sql', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin'],
            'web': ['html', 'css', 'react', 'angular', 'vue', 'node', 'django', 'flask', 'spring'],
            'data': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'tableau', 'power bi', 'excel'],
            'cloud': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform'],
            'soft_skills': ['communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking']
        }
    
    def extract_text_from_pdf(self, file_bytes):
        """Extract text from PDF"""
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except:
            return ""
    
    def extract_text_from_docx(self, file_bytes):
        """Extract text from DOCX"""
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            return "\n".join([p.text for p in doc.paragraphs])
        except:
            return ""
    
    def extract_skills_ai(self, text):
        """AI-powered skill extraction using spaCy NER"""
        doc = self.nlp(text.lower())
        
        skills = []
        
        # Method 1: Pattern matching
        for category, skill_list in self.skill_patterns.items():
            for skill in skill_list:
                if skill in text.lower():
                    skills.append(skill)
        
        # Method 2: Named Entity Recognition (finds technical terms)
        for ent in doc.ents:
            if ent.label_ in ["PRODUCT", "ORG", "WORK_OF_ART"]:
                if len(ent.text) > 2 and ent.text not in skills:
                    skills.append(ent.text.lower())
        
        # Method 3: Part-of-speech tagging (nouns that might be skills)
        for token in doc:
            if token.pos_ == "NOUN" and len(token.text) > 3:
                if token.text not in skills and token.text not in ['experience', 'education', 'work', 'skills']:
                    # Check if it's a known skill pattern
                    for skill_list in self.skill_patterns.values():
                        if token.text in skill_list:
                            skills.append(token.text)
                            break
        
        # Remove duplicates and sort
        return list(set(skills))
    
    def extract_experience(self, text):
        """Extract years of experience"""
        patterns = [
            r'(\d+)\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
            r'experience\s*(?:of)?\s*(\d+)\+?\s*(?:years?|yrs?)',
            r'(\d+)\s*(?:years?|yrs?)\s*(?:of)?\s*experience',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return int(match.group(1))
        
        # Check for phrases
        if 'entry level' in text.lower() or 'junior' in text.lower():
            return 1
        elif 'senior' in text.lower() or 'lead' in text.lower():
            return 5
        elif 'manager' in text.lower() or 'director' in text.lower():
            return 8
        
        return 0
    
    def analyze_cv(self, file_bytes, filename):
        """Complete CV analysis"""
        # Extract text based on file type
        if filename.lower().endswith('.pdf'):
            text = self.extract_text_from_pdf(file_bytes)
        elif filename.lower().endswith('.docx'):
            text = self.extract_text_from_docx(file_bytes)
        else:
            text = file_bytes.decode('utf-8', errors='ignore')
        
        if not text.strip():
            return {'error': 'Could not extract text from file'}
        
        # AI-powered skill extraction
        skills = self.extract_skills_ai(text)
        
        # Extract experience
        experience_years = self.extract_experience(text)
        
        # Generate resume tips
        tips = self.generate_tips(skills, text, experience_years)
        
        return {
            'success': True,
            'skills': skills,
            'experience_years': experience_years,
            'text_sample': text[:500],
            'resume_tips': tips,
            'word_count': len(text.split())
        }
    
    def generate_tips(self, skills, text, years):
        """Generate personalized resume tips"""
        tips = []
        
        # Skills analysis
        if len(skills) < 5:
            tips.append({
                'category': '🎯 Skills to Add',
                'tips': ['Add more technical skills relevant to your field', 'Include soft skills like communication and leadership']
            })
        else:
            tips.append({
                'category': '🎯 Strong Skills',
                'tips': [f'You have {len(skills)} skills! Highlight them prominently']
            })
        
        # Experience analysis
        if years == 0:
            tips.append({
                'category': '💼 Experience',
                'tips': ['Add years of experience clearly', 'Include internships and projects']
            })
        else:
            tips.append({
                'category': '💼 Experience Level',
                'tips': [f'You have {years}+ years of experience - emphasize leadership if applicable']
            })
        
        # Length analysis
        word_count = len(text.split())
        if word_count < 300:
            tips.append({
                'category': '📏 Resume Length',
                'tips': ['Add more details about your projects and achievements', 'Include quantifiable results']
            })
        
        # Action verbs
        verbs = ['developed', 'created', 'managed', 'led', 'implemented', 'designed', 'built', 'launched']
        has_verbs = any(v in text.lower() for v in verbs)
        if not has_verbs:
            tips.append({
                'category': '💪 Action Verbs',
                'tips': ['Use strong action verbs: Developed, Created, Managed, Led', 'Start bullet points with action words']
            })
        
        # Add generic tips
        tips.append({
            'category': '📝 Resume Tips',
            'tips': ['Quantify achievements with numbers', 'Tailor resume for each job', 'Keep formatting consistent']
        })
        
        return tips[:4]

# Test
if __name__ == "__main__":
    parser = AICVParser()
    print("✅ AI CV Parser ready")