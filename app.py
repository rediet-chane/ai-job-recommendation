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
        'python': ['python', 'django', 'flask', 'pandas', 'numpy'],
        'sql': ['sql', 'mysql', 'postgresql', 'database'],
        'javascript': ['javascript', 'react', 'node', 'vue'],
        'java': ['java', 'spring'],
        'html': ['html', 'css', 'frontend'],
        'communication': ['communication', 'presentation', 'public speaking'],
        'leadership': ['leadership', 'management', 'team lead'],
        'accounting': ['accounting', 'finance', 'quickbooks'],
        'marketing': ['marketing', 'seo', 'social media'],
        'design': ['design', 'photoshop', 'illustrator', 'figma'],
        'project management': ['project management', 'agile', 'scrum', 'jira'],
        'data analysis': ['data analysis', 'analytics', 'statistics', 'tableau'],
        'machine learning': ['machine learning', 'ml', 'ai', 'tensorflow'],
        'aws': ['aws', 'amazon', 'cloud', 'ec2', 's3'],
        'docker': ['docker', 'kubernetes', 'container'],
        'git': ['git', 'github', 'version control'],
        'excel': ['excel', 'spreadsheet'],
        'problem solving': ['problem solving', 'analytical', 'critical thinking'],
        'teamwork': ['teamwork', 'collaboration', 'team player'],
        'creativity': ['creativity', 'creative', 'innovation']
    }
    
    for skill, keywords in skill_database.items():
        for keyword in keywords:
            if keyword in text_lower:
                skills.append(skill)
                break
    
    return list(set(skills))

# ============================================
# PERSONALIZED RESUME TIPS
# ============================================

def generate_personalized_tips(skills, text):
    tips = []
    
    # Basic tips
    tips.append({'category': '📝 Keywords', 'tips': ['Use action verbs: Developed, Led, Created, Implemented']})
    tips.append({'category': '📄 Format', 'tips': ['Keep to 1-2 pages', 'Use bullet points', 'Quantify achievements']})
    
    # Skill-based tips
    if skills:
        tips.append({'category': '🎯 Skills to Highlight', 'tips': [f'Emphasize your {skills[0]} experience', f'Add specific projects using {", ".join(skills[:3])}']})
    
    # Missing common skills detection
    common_skills = ['communication', 'teamwork', 'problem solving']
    missing = [s for s in common_skills if s not in skills]
    if missing:
        tips.append({'category': '📚 Skills to Add', 'tips': [f'Consider adding {", ".join(missing)} to your resume']})
    
    # Length check
    words = len(text.split())
    if words < 200:
        tips.append({'category': '📏 Length', 'tips': ['Your resume seems short. Add more details about your experience and projects.']})
    
    return tips

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
        
        skills = extract_skills_from_text(text)
        session['user_skills'] = skills
        
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
                # Check if similar skill exists
                is_similar = False
                for uskill in user_skills_lower:
                    if fuzz.ratio(skill, uskill) > 85:
                        is_similar = True
                        break
                if not is_similar:
                    # Calculate priority based on job importance
                    if len(required_skills) <= 3:
                        priority = 'High'
                    elif len(required_skills) <= 6:
                        priority = 'Medium'
                    else:
                        priority = 'Low'
                    
                    gaps.append({
                        'skill': skill.title(),
                        'priority': priority,
                        'learning_url': f"https://www.google.com/search?q=learn+{skill.replace(' ', '+')}"
                    })
        
        return jsonify({
            'gaps': gaps[:8],
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
                        {'title': f'Learn {skill.title()} - Course', 'url': f'https://www.coursera.org/search?query={skill}'},
                        {'title': f'{skill.title()} Tutorial', 'url': f'https://www.youtube.com/results?search_query={skill}+tutorial'}
                    ]
                })
        return jsonify({'resources': resources})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/resume-tips')
def resume_tips():
    tips = [
        {'category': '🎯 Keywords', 'tips': ['Use action verbs: Developed, Implemented, Led, Created', 'Include skills from job descriptions', 'Add industry keywords']},
        {'category': '📄 Format', 'tips': ['Keep to 1-2 pages', 'Use bullet points', 'Quantify achievements with numbers']},
        {'category': '✨ Content', 'tips': ['Tailor resume for each job', 'Include relevant projects', 'Add certifications']}
    ]
    return jsonify({'tips': tips})

if __name__ == '__main__':
    app.run(debug=True, port=5000)