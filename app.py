from flask import Flask, render_template, request, jsonify, session
import secrets
import json
import os
from utils.nlp_processor import NLPProcessor
from models.recommender import JobRecommender

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize components
nlp = NLPProcessor()
recommender = JobRecommender()

# Load job data
try:
    recommender.load_jobs('data/jobs.csv')
    print("✅ Job data loaded successfully!")
except Exception as e:
    print(f"⚠️ Could not load jobs: {e}")

# Load learning resources
def load_resources():
    try:
        with open('data/learning_resources.json', 'r') as f:
            return json.load(f)
    except:
        return {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manual-input')
def manual_input():
    return render_template('manual_input.html')

@app.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    data = request.json
    skills_text = data.get('skills', '')
    
    skills_list = [s.strip() for s in skills_text.split(',') if s.strip()]
    session['user_skills'] = skills_list
    
    recommendations = recommender.get_recommendations(skills_list)
    
    return jsonify({
        'success': True,
        'skills': skills_list,
        'recommendations': recommendations
    })

@app.route('/skill-gap/<int:job_id>')
def skill_gap(job_id):
    user_skills = session.get('user_skills', [])
    
    if not user_skills:
        return jsonify({'error': 'No user skills found'}), 400
    
    job = recommender.jobs_df[recommender.jobs_df['job_id'] == job_id].iloc[0]
    
    required = [s.strip().lower() for s in str(job.get('required_skills', '')).split(',')]
    user_skills_lower = [s.lower() for s in user_skills]
    
    gaps = []
    for skill in required:
        if skill and skill not in user_skills_lower:
            freq = recommender.jobs_df['required_skills'].str.lower().str.contains(skill).mean()
            if freq > 0.7:
                priority = 'High'
            elif freq > 0.4:
                priority = 'Medium'
            else:
                priority = 'Low'
            
            gaps.append({
                'skill': skill,
                'priority': priority
            })
    
    return jsonify({
        'job_title': job['title'],
        'gaps': gaps
    })

@app.route('/learning-resources')
def learning_resources():
    skills = request.args.get('skills', '').split(',')
    resources = load_resources()
    
    result = []
    for skill in skills:
        skill = skill.strip().lower()
        if skill in resources:
            result.append({
                'skill': skill,
                'resources': resources[skill]
            })
    
    return jsonify({'resources': result})

@app.route('/resume-tips')
def resume_tips():
    user_skills = session.get('user_skills', [])
    
    if not user_skills:
        return jsonify({'error': 'No skills found'}), 400
    
    recommendations = recommender.get_recommendations(user_skills, top_n=3)
    
    tips = {
        'keywords': [
            f"Add these skills: {', '.join(user_skills[:5])}",
            "Use action verbs like 'Developed', 'Implemented', 'Led'",
            "Include specific technologies and tools"
        ],
        'formatting': [
            "Use a clean, professional layout",
            "Keep resume to 1-2 pages",
            "Use bullet points for readability",
            "Quantify achievements with numbers"
        ],
        'target_jobs': []
    }
    
    for rec in recommendations[:2]:
        tips['target_jobs'].append({
            'title': rec['title'],
            'tip': f"Highlight your {rec['required_skills'][:50]} skills"
        })
    
    return jsonify(tips)

if __name__ == '__main__':
    app.run(debug=True, port=5000)