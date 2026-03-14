import nltk
import re
import json
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download required NLTK data (if not already downloaded)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('wordnet')

class NLPProcessor:
    def __init__(self):
        """Initialize NLP tools"""
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Simple skill taxonomy
        self.skill_taxonomy = {
            "programming": {
                "python": ["python", "py", "django", "flask", "pandas"],
                "javascript": ["javascript", "js", "react", "node", "vue", "angular"],
                "java": ["java", "spring", "j2ee", "maven"],
                "sql": ["sql", "mysql", "postgresql", "database", "query", "oracle"],
                "html": ["html", "css", "web", "frontend"],
                "css": ["css", "scss", "sass", "styling"],
                "react": ["react", "reactjs", "react.js"],
                "git": ["git", "github", "version control"],
                "c++": ["c++", "cpp", "cplusplus"],
                "c#": ["c#", "csharp"],
                "php": ["php", "laravel"],
                "ruby": ["ruby", "rails"],
                "swift": ["swift", "ios"],
                "kotlin": ["kotlin", "android"],
                "typescript": ["typescript", "ts"],
                "mongodb": ["mongodb", "mongo", "nosql"],
                "aws": ["aws", "amazon web services", "cloud"],
                "docker": ["docker", "container", "kubernetes"],
                "azure": ["azure", "microsoft cloud"],
                "rest": ["rest", "restful", "api"],
                "graphql": ["graphql", "gql"]
            },
            "data_science": {
                "machine_learning": ["machine learning", "ml", "ai", "tensorflow", "pytorch", "keras"],
                "data_analysis": ["data analysis", "analytics", "statistics", "visualization", "tableau"],
                "data_science": ["data science", "predictive modeling", "deep learning"],
                "nlp": ["nlp", "natural language", "text mining"],
                "computer_vision": ["computer vision", "opencv", "image processing"],
                "big_data": ["big data", "hadoop", "spark", "kafka"]
            },
            "soft_skills": {
                "communication": ["communication", "verbal", "written", "presentation", "public speaking"],
                "teamwork": ["teamwork", "collaboration", "team player", "interpersonal"],
                "problem_solving": ["problem solving", "analytical", "critical thinking", "troubleshooting"],
                "leadership": ["leadership", "management", "team lead", "mentoring", "supervision"],
                "time_management": ["time management", "organization", "prioritization", "deadline"],
                "adaptability": ["adaptability", "flexibility", "quick learner"],
                "creativity": ["creativity", "innovation", "design thinking"],
                "conflict_resolution": ["conflict resolution", "negotiation", "mediation"]
            },
            "project_management": {
                "agile": ["agile", "scrum", "kanban", "jira"],
                "project_management": ["project management", "pmp", "prince2", "waterfall"],
                "product_management": ["product management", "product owner", "roadmap"]
            },
            "design": {
                "ui_ux": ["ui", "ux", "user interface", "user experience", "figma", "sketch", "adobe xd"],
                "graphic_design": ["graphic design", "photoshop", "illustrator", "indesign", "canva"],
                "web_design": ["web design", "responsive design", "wireframing", "prototyping"]
            },
            "marketing": {
                "seo": ["seo", "search engine optimization", "sem"],
                "content_marketing": ["content marketing", "copywriting", "blogging"],
                "social_media": ["social media", "smm", "facebook ads", "instagram", "linkedin"],
                "email_marketing": ["email marketing", "mailchimp", "newsletter"],
                "digital_marketing": ["digital marketing", "google ads", "analytics"]
            }
        }
    
    def clean_text(self, text):
        """Basic text cleaning"""
        if not isinstance(text, str):
            return ""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text
    
    def extract_skills(self, text):
        """Extract skills from text using taxonomy"""
        if not isinstance(text, str):
            return []
            
        text_lower = text.lower()
        found_skills = []
        
        for category, skills in self.skill_taxonomy.items():
            for skill, variations in skills.items():
                for variation in variations:
                    if variation in text_lower:
                        found_skills.append(skill)
                        break
        
        return list(set(found_skills))  # Remove duplicates
    
    def standardize_skill_format(self, skill):
        """Format skill name for display"""
        if not isinstance(skill, str):
            return str(skill)
        
        # Replace underscores with spaces and capitalize
        formatted = skill.replace('_', ' ').replace('-', ' ')
        # Capitalize each word
        formatted = ' '.join(word.capitalize() for word in formatted.split())
        
        # Special cases
        special_cases = {
            'Css': 'CSS',
            'Html': 'HTML',
            'Sql': 'SQL',
            'Api': 'API',
            'Ux': 'UX',
            'Ui': 'UI',
            'Js': 'JS',
            'Ts': 'TS',
            'C++': 'C++',
            'C#': 'C#',
            'Aws': 'AWS',
            'Azure': 'Azure',
            'Git': 'Git',
            'Mongodb': 'MongoDB',
            'Mysql': 'MySQL',
            'Postgresql': 'PostgreSQL',
            'Php': 'PHP',
            'Ruby': 'Ruby',
            'Swift': 'Swift',
            'Kotlin': 'Kotlin',
            'Docker': 'Docker',
            'Kubernetes': 'Kubernetes',
            'React': 'React',
            'Angular': 'Angular',
            'Vue': 'Vue.js',
            'Node': 'Node.js',
            'Express': 'Express.js',
            'Django': 'Django',
            'Flask': 'Flask',
            'Spring': 'Spring',
            'Tensorflow': 'TensorFlow',
            'Pytorch': 'PyTorch',
            'Scikit Learn': 'Scikit-Learn',
            'Nlp': 'NLP',
            'Ml': 'ML',
            'Ai': 'AI'
        }
        
        for key, value in special_cases.items():
            if key in formatted:
                return formatted.replace(key, value)
        
        return formatted
    
    def preprocess_user_skills(self, skills_input):
        """
        Process user skills input (can be string or list)
        Returns normalized skill list
        """
        normalized_skills = []
        
        # Handle different input types
        if isinstance(skills_input, str):
            # Split by commas and clean
            raw_skills = [s.strip() for s in skills_input.split(',') if s.strip()]
        elif isinstance(skills_input, list):
            raw_skills = [s.strip() for s in skills_input if s.strip()]
        else:
            raw_skills = []
        
        # Normalize each skill
        for skill in raw_skills:
            skill_lower = skill.lower().strip()
            
            # Check taxonomy for matching
            matched = False
            for category, skills in self.skill_taxonomy.items():
                for std_skill, variations in skills.items():
                    if skill_lower in variations or skill_lower == std_skill:
                        normalized_skills.append(std_skill)
                        matched = True
                        break
                if matched:
                    break
            
            # If not found in taxonomy, keep original
            if not matched and skill_lower:
                normalized_skills.append(skill_lower)
        
        return list(set(normalized_skills))  # Remove duplicates
    
    def preprocess_job_description(self, description):
        """Complete preprocessing pipeline for job descriptions"""
        # Clean text
        cleaned = self.clean_text(description)
        # Extract skills
        skills = self.extract_skills(description)
        
        return {
            'processed_text': cleaned,
            'extracted_skills': skills
        }

# Test the processor
if __name__ == "__main__":
    processor = NLPProcessor()
    test_desc = "Looking for Python developer with SQL and machine learning experience"
    result = processor.preprocess_job_description(test_desc)
    print("Original:", test_desc)
    print("Extracted Skills:", result['extracted_skills'])
    
    # Test skill standardization
    test_skills = ['python', 'sql', 'machine_learning', 'react']
    print("\nStandardized skills:")
    for skill in test_skills:
        print(f"  {skill} -> {processor.standardize_skill_format(skill)}")