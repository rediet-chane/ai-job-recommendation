from flask import Flask, render_template, request, jsonify, session
import secrets
import pandas as pd
from models.ai_matcher import AIMatcher
from utils.cv_parser import CVParser
from utils.nlp_processor import NLPProcessor

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize AI components
ai_matcher = AIMatcher()
nlp = NLPProcessor()

# Load jobs
try:
    ai_matcher.load_jobs('data/jobs.csv')
    print(f"✅ AI Matcher ready with {len(ai_matcher.jobs_df)} jobs")
except Exception as e:
    print(f"⚠️ Error loading jobs: {e}")

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
        skills = [s.strip() for s in data.get('skills', '').split(',') if s.strip()]
        session['user_skills'] = skills
        recs = ai_matcher.get_recommendations(skills)
        return jsonify({'success': True, 'recommendations': recs})
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
            text = CVParser.extract_text_from_pdf(file_bytes)
        elif filename.endswith('.docx'):
            text = CVParser.extract_text_from_docx(file_bytes)
        else:
            text = CVParser.extract_text_from_txt(file_bytes)
        
        if not text.strip():
            return jsonify({'error': 'Could not extract text'}), 400
        
        skills = ai_matcher.extract_skills_from_cv(text)
        session['user_skills'] = skills
        recs = ai_matcher.get_recommendations(skills)
        
        # Generate personalized tips
        tips = [
            {'category': '🎯 Skills Detected', 'tips': [f'We found: {", ".join(skills[:5])}']},
            {'category': '📝 Resume Tips', 'tips': ['Use action verbs', 'Quantify achievements', 'Tailor for each job']}
        ]
        
        return jsonify({
            'success': True,
            'skills': skills,
            'recommendations': recs[:8],
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
            return jsonify({'gaps': []})
        
        gaps = ai_matcher.analyze_skill_gap(user_skills, job_id)
        job = ai_matcher.jobs_df.iloc[job_id]
        return jsonify({'gaps': gaps, 'job_title': job['title']})
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
                    'resources': [{'title': f'Learn {skill.title()}', 'url': f'https://www.google.com/search?q=learn+{skill}'}]
                })
        return jsonify({'resources': resources})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/resume-tips')
def resume_tips():
    tips = [
        {'category': '🎯 Keywords', 'tips': ['Use action verbs', 'Include skills from job descriptions']},
        {'category': '📄 Format', 'tips': ['Keep to 1-2 pages', 'Use bullet points']},
        {'category': '✨ Content', 'tips': ['Quantify achievements', 'Tailor for each job']}
    ]
    return jsonify({'tips': tips})

if __name__ == '__main__':
    app.run(debug=True, port=5000)