from flask import Flask, render_template, request, jsonify, session
import secrets
import pandas as pd
import re
import io
from fuzzywuzzy import fuzz
import PyPDF2
import docx
from models.smart_matcher import SmartMatcher

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# ============================================
# INITIALIZE AI MATCHER
# ============================================

matcher = SmartMatcher()
try:
    matcher.load_jobs('data/jobs.csv')
    print(f"✅ AI Matcher ready with {len(matcher.jobs_df)} jobs")
except Exception as e:
    print(f"⚠️ Error: {e}")

# ============================================
# CV PARSING FUNCTIONS
# ============================================

def extract_text_from_pdf(file_bytes):
    try:
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except:
        return ""

def extract_text_from_docx(file_bytes):
    try:
        doc = docx.Document(io.BytesIO(file_bytes))
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except:
        return ""

def extract_text_from_txt(file_bytes):
    try:
        return file_bytes.decode('utf-8', errors='ignore')
    except:
        return ""

# ============================================
# SKILL EXTRACTION
# ============================================

def extract_skills_from_text(text):
    text_lower = text.lower()
    skills = []
    
    skill_database = {
        'python': ['python', 'django', 'flask', 'pandas', 'numpy', 'fastapi'],
        'sql': ['sql', 'mysql', 'postgresql', 'database', 'query', 'oracle'],
        'javascript': ['javascript', 'react', 'node', 'vue', 'angular', 'typescript'],
        'java': ['java', 'spring', 'j2ee', 'hibernate'],
        'html': ['html', 'css', 'frontend', 'bootstrap'],
        'communication': ['communication', 'presentation', 'public speaking', 'verbal', 'written'],
        'leadership': ['leadership', 'management', 'team lead', 'supervisor', 'director'],
        'teamwork': ['teamwork', 'collaboration', 'team player', 'interpersonal'],
        'problem solving': ['problem solving', 'analytical', 'critical thinking', 'troubleshooting'],
        'project management': ['project management', 'agile', 'scrum', 'jira', 'trello'],
        'data analysis': ['data analysis', 'analytics', 'statistics', 'tableau', 'power bi'],
        'machine learning': ['machine learning', 'ml', 'ai', 'tensorflow', 'pytorch', 'keras'],
        'aws': ['aws', 'amazon', 'cloud', 'ec2', 's3', 'lambda'],
        'docker': ['docker', 'kubernetes', 'container', 'devops'],
        'git': ['git', 'github', 'version control'],
        'excel': ['excel', 'spreadsheet', 'sheets'],
        'accounting': ['accounting', 'finance', 'quickbooks', 'peachtree', 'tax'],
        'marketing': ['marketing', 'seo', 'social media', 'digital marketing', 'content'],
        'design': ['design', 'photoshop', 'illustrator', 'figma', 'adobe xd', 'ui', 'ux'],
        'engineering': ['engineering', 'engineer', 'civil', 'mechanical', 'electrical'],
        'architecture': ['architecture', 'architect', 'autocad', 'revit', 'sketchup']
    }
    
    for skill, keywords in skill_database.items():
        for keyword in keywords:
            if keyword in text_lower:
                skills.append(skill)
                break
    
    return list(set(skills))

# ============================================
# PERSONALIZED RESUME TIPS (Based on CV content)
# ============================================

def generate_personalized_tips(skills, text):
    tips = []
    text_lower = text.lower()
    words = text.split()
    
    # Skills analysis
    if skills:
        tips.append({
            'category': '🎯 Skills Detected',
            'tips': [f'We found these skills: {", ".join(skills[:5])}', 
                     f'Highlight these skills prominently in your resume']
        })
    
    # Missing common skills
    common_skills = ['communication', 'teamwork', 'problem solving', 'leadership']
    missing = [s for s in common_skills if s not in skills]
    if missing:
        tips.append({
            'category': '📚 Skills to Add',
            'tips': [f'Consider adding these in-demand skills: {", ".join(missing)}']
        })
    
    # Length analysis
    if len(words) < 300:
        tips.append({
            'category': '📏 Resume Length',
            'tips': ['Your resume seems short. Aim for 300-500 words', 'Add more details about your experience and projects']
        })
    elif len(words) > 1000:
        tips.append({
            'category': '📏 Resume Length',
            'tips': ['Your resume is quite long. Consider keeping it to 2 pages', 'Focus on most relevant experiences']
        })
    
    # Action verb analysis
    action_verbs = ['developed', 'created', 'managed', 'led', 'implemented', 'designed', 'analyzed', 'improved']
    has_verbs = any(verb in text_lower for verb in action_verbs)
    if not has_verbs:
        tips.append({
            'category': '💪 Action Verbs',
            'tips': ['Use strong action verbs: Developed, Created, Managed, Led, Implemented', 'Quantify achievements with numbers']
        })
    
    # Numbers/achievements
    has_numbers = bool(re.search(r'\d+%|\d+,\d+|\d+', text))
    if not has_numbers:
        tips.append({
            'category': '📊 Achievements',
            'tips': ['Add numbers to quantify your achievements', 'Example: "Improved efficiency by 20%"']
        })
    
    # Customization tip
    tips.append({
        'category': '🎯 Customization',
        'tips': ['Tailor your resume for each job application', 'Use keywords from the job description']
    })
    
    return tips[:6]  # Limit to 6 tips

# ============================================
# CALCULATE SKILL PRIORITY (Based on market demand)
# ============================================

def calculate_skill_priority(skill, user_skills, all_jobs_df):
    """Calculate priority based on how common the skill is in jobs matching user skills"""
    try:
        # Find jobs similar to user skills
        user_skills_set = set(user_skills)
        matching_jobs = []
        for _, job in all_jobs_df.iterrows():
            job_skills = str(job.get('required_skills', '')).lower()
            job_skills_set = set([s.strip() for s in job_skills.split(',') if s.strip()])
            if user_skills_set & job_skills_set:  # If shares at least one skill
                matching_jobs.append(job_skills)
        
        # Count how many matching jobs require this skill
        count = 0
        for job_skills in matching_jobs:
            if skill in job_skills:
                count += 1
        
        total = len(matching_jobs) if matching_jobs else 1
        frequency = count / total
        
        if frequency > 0.5:
            return 'High'
        elif frequency > 0.2:
            return 'Medium'
        else:
            return 'Low'
    except:
        return 'Medium'

# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

@app.route('/manual-input')
def manual_input():
    return render_template('manual_input.html')

@app.route('/upload-cv')
def upload_cv():
    return render_template('upload_cv.html')

@app.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    try:
        data = request.json
        skills_text = data.get('skills', '')
        skills_list = [s.strip() for s in skills_text.split(',') if s.strip()]
        
        session['user_skills'] = skills_list
        
        recommendations = matcher.get_recommendations(skills_list)
        
        return jsonify({
            'success': True,
            'skills': skills_list,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/analyze-cv', methods=['POST'])
def analyze_cv():
    try:
        if 'cv' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['cv']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        file_bytes = file.read()
        filename = file.filename.lower()
        text = ""
        
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(file_bytes)
        elif filename.endswith('.docx'):
            text = extract_text_from_docx(file_bytes)
        else:
            text = extract_text_from_txt(file_bytes)
        
        if not text.strip():
            return jsonify({'error': 'Could not extract text'}), 400
        
        # Extract skills
        skills = extract_skills_from_text(text)
        session['user_skills'] = skills
        
        # Get job recommendations
        recommendations = matcher.get_recommendations(skills)
        
        # Personalized resume tips
        tips = generate_personalized_tips(skills, text)
        
        # Learning resources
        learning_resources = []
        for skill in skills[:5]:
            learning_resources.append({
                'skill': skill,
                'resources': [
                    {'title': f'Learn {skill.title()}', 'url': f'https://www.google.com/search?q=learn+{skill}'}
                ]
            })
        
        return jsonify({
            'success': True,
            'skills': skills,
            'recommendations': recommendations[:8],
            'learning_resources': learning_resources,
            'resume_tips': tips,
            'filename': file.filename
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/skill-gap/<int:job_id>')
def skill_gap(job_id):
    try:
        user_skills = session.get('user_skills', [])
        if not user_skills:
            return jsonify({'gaps': [], 'job_title': ''})
        
        job = matcher.jobs_df.iloc[job_id]
        required_skills = [s.strip().lower() for s in str(job.get('required_skills', '')).split(',') if s.strip()]
        user_skills_lower = [s.lower() for s in user_skills]
        
        gaps = []
        for skill in required_skills:
            if skill and skill not in user_skills_lower:
                # Check if similar skill exists (fuzzy match)
                is_similar = False
                for uskill in user_skills_lower:
                    if fuzz.ratio(skill, uskill) > 85:
                        is_similar = True
                        break
                if not is_similar:
                    # Calculate priority based on market demand
                    priority = calculate_skill_priority(skill, user_skills, matcher.jobs_df)
                    
                    gaps.append({
                        'skill': skill.title(),
                        'priority': priority,
                        'learning_url': f"https://www.google.com/search?q=learn+{skill.replace(' ', '+')}"
                    })
        
        return jsonify({
            'gaps': gaps[:10],
            'job_title': job['title']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/learning-resources')
def learning_resources():
    try:
        skills = request.args.get('skills', '').split(',')
        resources = []
        for skill in skills:
            if skill.strip():
                resources.append({
                    'skill': skill.strip(),
                    'resources': [
                        {'title': f'Learn {skill.title()}', 'url': f'https://www.coursera.org/search?query={skill}'}
                    ]
                })
        return jsonify({'resources': resources})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/resume-tips')
def resume_tips():
    # Generic tips as fallback
    tips = [
        {'category': '📝 Keywords', 'tips': ['Use action verbs', 'Include skills from job descriptions']},
        {'category': '📄 Format', 'tips': ['Keep to 1-2 pages', 'Use bullet points']},
        {'category': '✨ Content', 'tips': ['Quantify achievements', 'Tailor for each job']}
    ]
    return jsonify({'tips': tips})

if __name__ == '__main__':
    app.run(debug=True, port=5000)