import pandas as pd
import json
import os

def create_sample_jobs():
    """Create sample job data"""
    jobs = [
        {
            'job_id': 1,
            'title': 'Python Developer',
            'description': 'Develop backend services using Python and Django. Experience with REST APIs and SQL databases required.',
            'required_skills': 'Python, Django, SQL, REST API, Git',
            'category': 'Software Development',
            'experience_level': 'Entry',
            'source': 'Sample'
        },
        {
            'job_id': 2,
            'title': 'Data Analyst',
            'description': 'Analyze business data using SQL and Python. Create visualizations and reports for stakeholders.',
            'required_skills': 'SQL, Python, Excel, Data Visualization, Statistics',
            'category': 'Data Science',
            'experience_level': 'Entry',
            'source': 'Sample'
        },
        {
            'job_id': 3,
            'title': 'Frontend Developer',
            'description': 'Build responsive web interfaces using HTML, CSS, and JavaScript. Experience with React preferred.',
            'required_skills': 'HTML, CSS, JavaScript, React, Git',
            'category': 'Web Development',
            'experience_level': 'Entry',
            'source': 'Sample'
        },
        {
            'job_id': 4,
            'title': 'Full Stack Developer',
            'description': 'Develop end-to-end web applications. Strong knowledge of both frontend and backend technologies.',
            'required_skills': 'JavaScript, Python, SQL, HTML, CSS, REST API',
            'category': 'Software Development',
            'experience_level': 'Intermediate',
            'source': 'Sample'
        },
        {
            'job_id': 5,
            'title': 'Machine Learning Engineer',
            'description': 'Build and deploy machine learning models. Experience with scikit-learn and deep learning frameworks.',
            'required_skills': 'Python, Machine Learning, SQL, Scikit-learn, TensorFlow',
            'category': 'Data Science',
            'experience_level': 'Intermediate',
            'source': 'Sample'
        },
        {
            'job_id': 6,
            'title': 'DevOps Engineer',
            'description': 'Manage CI/CD pipelines and cloud infrastructure. Experience with Docker and Kubernetes.',
            'required_skills': 'Docker, Kubernetes, AWS, Linux, Python',
            'category': 'DevOps',
            'experience_level': 'Intermediate',
            'source': 'Sample'
        },
        {
            'job_id': 7,
            'title': 'UI/UX Designer',
            'description': 'Design user interfaces and create prototypes. Strong visual design skills.',
            'required_skills': 'Figma, Adobe XD, UI Design, Prototyping, HTML, CSS',
            'category': 'Design',
            'experience_level': 'Entry',
            'source': 'Sample'
        },
        {
            'job_id': 8,
            'title': 'Project Manager',
            'description': 'Lead software development projects. Coordinate teams and manage stakeholder expectations.',
            'required_skills': 'Agile, Scrum, Communication, Leadership, JIRA',
            'category': 'Management',
            'experience_level': 'Senior',
            'source': 'Sample'
        },
        {
            'job_id': 9,
            'title': 'QA Engineer',
            'description': 'Test software applications and ensure quality. Write and execute test cases.',
            'required_skills': 'Testing, Selenium, Python, SQL, Attention to Detail',
            'category': 'Quality Assurance',
            'experience_level': 'Entry',
            'source': 'Sample'
        },
        {
            'job_id': 10,
            'title': 'Business Analyst',
            'description': 'Bridge gap between business needs and technical solutions. Gather and document requirements.',
            'required_skills': 'Requirements Analysis, Communication, SQL, Excel, Documentation',
            'category': 'Business',
            'experience_level': 'Intermediate',
            'source': 'Sample'
        }
    ]
    
    df = pd.DataFrame(jobs)
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV
    df.to_csv('data/jobs.csv', index=False)
    print(f"Created {len(jobs)} sample jobs in data/jobs.csv")
    
    return df

def create_skill_taxonomy():
    """Create skill taxonomy"""
    taxonomy = {
        "programming": {
            "Python": ["py", "python3", "python programming", "django", "flask"],
            "JavaScript": ["js", "javascript", "ecmascript", "node", "react"],
            "Java": ["java", "j2ee", "spring"],
            "SQL": ["sql", "mysql", "postgresql", "database", "rdbms"],
            "HTML": ["html", "html5"],
            "CSS": ["css", "css3", "styling"],
            "C++": ["cpp", "cplusplus"],
            "C#": ["csharp", "c sharp"],
            "PHP": ["php"],
            "Ruby": ["ruby", "rails"],
            "Go": ["golang", "go lang"],
            "Rust": ["rust"],
            "TypeScript": ["ts", "typescript"]
        },
        "data_science": {
            "Machine Learning": ["ml", "machine learning", "ai", "artificial intelligence"],
            "Data Analysis": ["data analysis", "analytics", "data analytics"],
            "Data Visualization": ["visualization", "tableau", "power bi", "matplotlib", "seaborn"],
            "Statistics": ["statistics", "statistical analysis", "probability"],
            "Deep Learning": ["deep learning", "neural networks", "tensorflow", "pytorch"],
            "NLP": ["nlp", "natural language processing", "text mining"]
        },
        "web_development": {
            "React": ["react", "reactjs", "react.js"],
            "Angular": ["angular", "angularjs"],
            "Vue": ["vue", "vuejs"],
            "Node.js": ["node", "nodejs", "node.js"],
            "Django": ["django"],
            "Flask": ["flask"],
            "Express": ["express", "expressjs"],
            "REST API": ["rest", "restful", "api", "apis"],
            "GraphQL": ["graphql"],
            "Responsive Design": ["responsive", "mobile-friendly", "adaptive"]
        },
        "devops": {
            "Docker": ["docker", "containerization"],
            "Kubernetes": ["k8s", "kubernetes"],
            "AWS": ["aws", "amazon web services", "ec2", "s3"],
            "Azure": ["azure", "microsoft azure"],
            "GCP": ["gcp", "google cloud"],
            "CI/CD": ["cicd", "continuous integration", "continuous deployment"],
            "Jenkins": ["jenkins"],
            "Git": ["git", "github", "gitlab"],
            "Linux": ["linux", "unix"],
            "Terraform": ["terraform", "iac"]
        },
        "soft_skills": {
            "Communication": ["communication", "verbal", "written", "presentation"],
            "Teamwork": ["teamwork", "collaboration", "team player", "cooperation"],
            "Problem Solving": ["problem solving", "analytical", "critical thinking"],
            "Leadership": ["leadership", "leading", "mentoring"],
            "Time Management": ["time management", "organization", "prioritization"],
            "Adaptability": ["adaptability", "flexible", "learning"],
            "Creativity": ["creativity", "creative", "innovation"],
            "Attention to Detail": ["attention to detail", "detail-oriented", "precision"]
        },
        "databases": {
            "MySQL": ["mysql"],
            "PostgreSQL": ["postgresql", "postgres"],
            "MongoDB": ["mongodb", "mongo"],
            "Redis": ["redis"],
            "Elasticsearch": ["elasticsearch", "elastic"],
            "Oracle": ["oracle"],
            "SQL Server": ["sql server", "mssql"],
            "SQLite": ["sqlite"]
        },
        "tools": {
            "JIRA": ["jira", "jira software"],
            "Confluence": ["confluence"],
            "Slack": ["slack"],
            "Trello": ["trello"],
            "Figma": ["figma"],
            "Adobe XD": ["adobe xd", "xd"],
            "Photoshop": ["photoshop", "ps"],
            "VS Code": ["vscode", "visual studio code"],
            "IntelliJ": ["intellij", "idea"],
            "Eclipse": ["eclipse"]
        }
    }
    
    with open('data/skills_taxonomy.json', 'w') as f:
        json.dump(taxonomy, f, indent=2)
    
    print("Created data/skills_taxonomy.json")
    return taxonomy

if __name__ == "__main__":
    print("Initializing data...")
    create_sample_jobs()
    create_skill_taxonomy()
    print("\n✅ Data initialization complete!")
    print("\nNext steps:")
    print("1. Run: python app.py")
    print("2. Open browser: http://localhost:5000")
    print("3. Test with both quiz and manual input")