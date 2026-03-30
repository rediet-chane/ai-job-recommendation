from flask import Flask, render_template, request, jsonify, session
import secrets
import os
from models.ai_job_matcher import AIJobMatcher
from utils.ai_cv_parser import AICVParser

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Initialize AI components
print("🤖 Initializing AI Job Recommendation System...")
ai_matcher = AIJobMatcher()
cv_parser = AICVParser()

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
        skills_text = data.get('skills', '')
        skills_list = [s.strip() for s in skills_text.split(',') if s.strip()]
        
        session['user_skills'] = skills_list
        
        # AI-powered recommendations
        recommendations = ai_matcher.get_recommendations(skills_list)
        
        return jsonify({
            'success': True,
            'skills': skills_list,
            'recommendations': recommendations
        })
    except Exception as e:
        print(f"Error: {e}")
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
        filename = file.filename
        
        # AI-powered CV analysis
        result = cv_parser.analyze_cv(file_bytes, filename)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 400
        
        skills = result['skills']
        session['user_skills'] = skills
        
        # Get job recommendations based on CV skills
        recommendations = ai_matcher.get_recommendations(skills)
        
        return jsonify({
            'success': True,
            'skills': skills,
            'recommendations': recommendations[:8],
            'resume_tips': result['resume_tips'],
            'experience_years': result['experience_years'],
            'word_count': result['word_count'],
            'filename': filename
        })
    except Exception as e:
        print(f"Error in analyze-cv: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/skill-gap/<int:job_id>')
def skill_gap(job_id):
    try:
        user_skills = session.get('user_skills', [])
        if not user_skills:
            return jsonify({'gaps': []})
        
        gaps = ai_matcher.analyze_skill_gap(user_skills, job_id)
        job = ai_matcher.jobs_df.iloc[job_id]
        
        return jsonify({
            'gaps': gaps,
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
                        {'title': f'Learn {skill.title()} on Coursera', 'url': f'https://www.coursera.org/search?query={skill}'},
                        {'title': f'{skill.title()} Tutorial on YouTube', 'url': f'https://www.youtube.com/results?search_query={skill}+tutorial'}
                    ]
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