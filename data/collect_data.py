import pandas as pd
import os

def create_sample_data():
    """Create a beautiful sample job dataset"""
    
    print("🎨 Creating sample job data with beautiful colors...")
    
    sample_data = {
        'job_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        'title': [
            '🌟 Software Developer',
            '📊 Data Analyst',
            '🎨 Web Designer',
            '📈 Marketing Specialist',
            '💰 Accountant',
            '🐍 Python Developer',
            '🗄️ Database Administrator',
            '🤖 Machine Learning Engineer',
            '📋 Project Manager',
            '🎯 UX Designer',
            '🔧 DevOps Engineer',
            '🛡️ Cybersecurity Analyst'
        ],
        'description': [
            'Create amazing web applications using Python, Django, and SQL. Build REST APIs and work with cloud platforms.',
            'Transform data into insights using SQL, Python, Excel. Create beautiful visualizations and reports.',
            'Design stunning websites with HTML, CSS, JavaScript, Figma. Create responsive and user-friendly designs.',
            'Manage social media campaigns, SEO, Google Ads, and create engaging content.',
            'Handle financial records, Peachtree, Excel, tax preparation, and financial reporting.',
            'Build powerful backend services with Python, Flask, FastAPI. Work with databases and APIs.',
            'Manage SQL databases, optimize queries, handle backups and database security.',
            'Develop ML models using scikit-learn, TensorFlow. Deploy models to production.',
            'Lead software projects, manage teams, agile methodology, stakeholder communication.',
            'Create beautiful user interfaces, wireframes, prototypes. User research and usability testing.',
            'Manage cloud infrastructure, CI/CD pipelines, Docker, Kubernetes, and AWS.',
            'Protect systems from security threats, monitor networks, and implement security measures.'
        ],
        'required_skills': [
            'Python, Django, SQL, REST API, JavaScript, Git',
            'SQL, Python, Excel, Data Visualization, Statistics, Tableau',
            'HTML, CSS, JavaScript, Figma, Responsive Design, Adobe XD',
            'Social Media, SEO, Google Ads, Content Writing, Analytics',
            'Accounting, Excel, Peachtree, Tax, Financial Reporting, QuickBooks',
            'Python, Flask, FastAPI, PostgreSQL, Git, Docker',
            'SQL, MySQL, PostgreSQL, Database Design, Backup, Performance',
            'Python, Machine Learning, scikit-learn, TensorFlow, SQL',
            'Project Management, Agile, Communication, Leadership, Jira',
            'UX Design, Figma, Wireframing, User Research, Prototyping, Sketch',
            'AWS, Docker, Kubernetes, Jenkins, Linux, Python, Git',
            'Network Security, Risk Assessment, Python, Compliance, Firewalls'
        ],
        'category': [
            '💻 Software Development',
            '📊 Data Science',
            '🎨 Design',
            '📈 Marketing',
            '💰 Finance',
            '💻 Software Development',
            '🗄️ Database',
            '🤖 Data Science',
            '📋 Management',
            '🎨 Design',
            '🔧 DevOps',
            '🛡️ Security'
        ],
        'experience_level': [
            'Entry', 'Entry', 'Entry', 'Mid', 'Entry',
            'Entry', 'Mid', 'Mid', 'Senior', 'Entry', 'Mid', 'Senior'
        ],
        'salary_range': [
            '$60k-$80k', '$55k-$75k', '$50k-$70k', '$45k-$65k', '$50k-$70k',
            '$65k-$85k', '$70k-$90k', '$80k-$110k', '$75k-$95k', '$60k-$80k',
            '$85k-$105k', '$80k-$100k'
        ],
        'remote': ['Yes', 'Hybrid', 'Yes', 'No', 'Hybrid', 'Yes', 'No', 'Hybrid', 'Yes', 'Yes', 'Hybrid', 'No']
    }
    
    df = pd.DataFrame(sample_data)
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Save to CSV
    df.to_csv('data/jobs.csv', index=False)
    print(f"✅ Created sample dataset with {len(df)} jobs in data/jobs.csv")
    print("📊 Jobs include: Software, Data, Design, Marketing, Finance, DevOps, Security")
    print(df.head())
    return df

if __name__ == "__main__":
    create_sample_data()