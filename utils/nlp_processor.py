import re

class NLPProcessor:
    def __init__(self):
        """Initialize NLP tools with beautiful skill taxonomy"""
        print("🎨 Initializing NLP Processor with colorful skills...")
        
        # Beautiful skill taxonomy with emojis
        self.skill_taxonomy = {
            "💻 Programming": {
                "python": ["python", "py", "django", "flask", "pandas", "numpy"],
                "javascript": ["javascript", "js", "react", "node", "vue", "angular", "jquery"],
                "java": ["java", "spring", "j2ee", "maven", "gradle"],
                "c++": ["c++", "cpp", "cplusplus", "unreal"],
                "c#": ["c#", "csharp", "dotnet", ".net"],
                "php": ["php", "laravel", "wordpress", "drupal"],
                "ruby": ["ruby", "rails", "ruby on rails"],
                "swift": ["swift", "ios", "ipados"],
                "kotlin": ["kotlin", "android"],
                "go": ["go", "golang"],
                "rust": ["rust"],
                "typescript": ["typescript", "ts"]
            },
            "🗄️ Database": {
                "sql": ["sql", "mysql", "postgresql", "database", "query", "oracle", "sqlite"],
                "mongodb": ["mongodb", "mongo", "nosql"],
                "redis": ["redis", "cache"],
                "elasticsearch": ["elasticsearch", "elk"],
                "dynamodb": ["dynamodb", "dynamo"]
            },
            "☁️ Cloud & DevOps": {
                "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
                "azure": ["azure", "microsoft cloud"],
                "gcp": ["gcp", "google cloud", "google cloud platform"],
                "docker": ["docker", "container", "dockerfile"],
                "kubernetes": ["kubernetes", "k8s", "aks", "eks"],
                "jenkins": ["jenkins", "ci/cd", "pipeline"],
                "terraform": ["terraform", "iac", "infrastructure"],
                "ansible": ["ansible"]
            },
            "🤖 Data Science & AI": {
                "machine_learning": ["machine learning", "ml", "ai", "artificial intelligence"],
                "deep_learning": ["deep learning", "neural networks", "tensorflow", "pytorch", "keras"],
                "data_science": ["data science", "predictive modeling"],
                "data_analysis": ["data analysis", "analytics", "statistics"],
                "nlp": ["nlp", "natural language", "text mining", "llm"],
                "computer_vision": ["computer vision", "opencv", "image processing"],
                "big_data": ["big data", "hadoop", "spark", "kafka", "pyspark"]
            },
            "🎨 Design": {
                "ui_design": ["ui", "user interface", "figma", "sketch"],
                "ux_design": ["ux", "user experience", "user research"],
                "graphic_design": ["graphic design", "photoshop", "illustrator", "indesign"],
                "web_design": ["web design", "responsive design", "wireframing"],
                "product_design": ["product design", "design thinking"]
            },
            "📈 Marketing": {
                "seo": ["seo", "search engine optimization", "sem"],
                "content_marketing": ["content marketing", "copywriting", "blogging"],
                "social_media": ["social media", "smm", "facebook ads", "instagram", "tiktok"],
                "email_marketing": ["email marketing", "mailchimp", "newsletter"],
                "digital_marketing": ["digital marketing", "google ads", "analytics"]
            },
            "💼 Soft Skills": {
                "communication": ["communication", "verbal", "written", "presentation", "public speaking"],
                "teamwork": ["teamwork", "collaboration", "team player", "interpersonal"],
                "leadership": ["leadership", "management", "team lead", "mentoring"],
                "problem_solving": ["problem solving", "analytical", "critical thinking"],
                "creativity": ["creativity", "creative", "innovation"],
                "time_management": ["time management", "organization", "prioritization"],
                "adaptability": ["adaptability", "flexibility", "quick learner"]
            },
            "🔧 Tools": {
                "git": ["git", "github", "gitlab", "bitbucket", "version control"],
                "jira": ["jira", "confluence", "atlassian"],
                "trello": ["trello", "kanban"],
                "slack": ["slack", "teams", "discord"],
                "vscode": ["vscode", "visual studio code", "ide"]
            }
        }
    
    def extract_skills(self, text):
        """Extract skills from text with emoji support"""
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
        
        return list(set(found_skills))
    
    def preprocess_job_description(self, description):
        """Process job description and extract skills"""
        skills = self.extract_skills(description)
        
        return {
            'processed_text': description.lower(),
            'extracted_skills': skills
        }
    
    def preprocess_user_skills(self, skills_input):
        """Normalize user skills"""
        if isinstance(skills_input, str):
            raw_skills = [s.strip() for s in skills_input.split(',') if s.strip()]
        elif isinstance(skills_input, list):
            raw_skills = [s.strip() for s in skills_input if s.strip()]
        else:
            raw_skills = []
        
        normalized = []
        for skill in raw_skills:
            skill_lower = skill.lower().strip()
            
            # Check taxonomy
            found = False
            for category, skills in self.skill_taxonomy.items():
                for std_skill, variations in skills.items():
                    if skill_lower in variations or skill_lower == std_skill:
                        normalized.append(std_skill)
                        found = True
                        break
                if found:
                    break
            
            if not found and skill_lower:
                normalized.append(skill_lower)
        
        return list(set(normalized))

# Test the processor
if __name__ == "__main__":
    processor = NLPProcessor()
    test = "Looking for Python developer with SQL, AWS, and machine learning"
    skills = processor.extract_skills(test)
    print(f"📝 Text: {test}")
    print(f"🎯 Extracted Skills: {skills}")