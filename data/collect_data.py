import pandas as pd
import os

def create_sample_data():
    """Create a sample job dataset"""
    
    sample_data = {
        'job_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'title': [
            'Software Developer',
            'Data Analyst',
            'Web Designer',
            'Marketing Specialist',
            'Accountant',
            'Python Developer',
            'Database Administrator',
            'Machine Learning Engineer',
            'Project Manager',
            'UX Designer'
        ],
        'description': [
            'Develop web applications using Python, Django, and SQL. Experience with REST APIs and cloud platforms.',
            'Analyze data using SQL, Python, Excel. Create visualizations and reports for business decisions.',
            'Design websites using HTML, CSS, JavaScript, Figma. Create responsive and user-friendly designs.',
            'Manage social media campaigns, SEO, Google Ads, content creation and email marketing.',
            'Handle financial records, Peachtree, Excel, tax preparation and financial reporting.',
            'Build backend services with Python, Flask, FastAPI. Work with databases and APIs.',
            'Manage SQL databases, optimize queries, handle backups and database security.',
            'Develop ML models using scikit-learn, TensorFlow. Deploy models to production.',
            'Lead software projects, manage teams, agile methodology, stakeholder communication.',
            'Create user interfaces, wireframes, prototypes. User research and usability testing.'
        ],
        'required_skills': [
            'Python, Django, SQL, REST API, JavaScript',
            'SQL, Python, Excel, Data Visualization, Statistics',
            'HTML, CSS, JavaScript, Figma, Responsive Design',
            'Social Media, SEO, Google Ads, Content Writing',
            'Accounting, Excel, Peachtree, Tax, Financial Reporting',
            'Python, Flask, FastAPI, PostgreSQL, Git',
            'SQL, MySQL, PostgreSQL, Database Design, Backup',
            'Python, Machine Learning, scikit-learn, TensorFlow',
            'Project Management, Agile, Communication, Leadership',
            'UX Design, Figma, Wireframing, User Research, Prototyping'
        ],
        'category': [
            'Software Development',
            'Data Science',
            'Design',
            'Marketing',
            'Finance',
            'Software Development',
            'Database',
            'Data Science',
            'Management',
            'Design'
        ],
        'experience_level': ['Entry', 'Entry', 'Entry', 'Mid', 'Entry', 
                           'Entry', 'Mid', 'Mid', 'Senior', 'Entry']
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv('data/jobs.csv', index=False)
    print(f"✅ Created sample dataset with {len(df)} jobs in data/jobs.csv")
    return df

if __name__ == "__main__":
    create_sample_data()