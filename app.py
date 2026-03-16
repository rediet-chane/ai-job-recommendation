from flask import Flask, render_template, request, jsonify, session
import secrets
import random
from utils.nlp_processor import NLPProcessor
from models.recommender import JobRecommender
from models.quiz import SkillQuiz

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Initialize components
nlp = NLPProcessor()
recommender = JobRecommender()

# Load job data
try:
    recommender.load_jobs('data/jobs.csv')
    print("✅ Job data loaded with colors!")
except Exception as e:
    print(f"⚠️ Could not load jobs: {e}")

@app.route('/')
def index():
    """Beautiful home page"""
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    """Colorful quiz page"""
    return render_template('quiz.html')

@app.route('/get-quiz-questions')
def get_quiz_questions():
    """Get beautiful quiz questions"""
    quiz_instance = SkillQuiz()
    questions = quiz_instance.get_questions()
    return jsonify({'questions': questions})

@app.route('/manual-input')
def manual_input():
    """Manual skill input page"""
    return render_template('manual_input.html')

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    """Process colorful quiz submission"""
    try:
        data = request.json
        answers = data.get('answers', [])
        
        quiz_instance = SkillQuiz()
        
        for answer in answers:
            quiz_instance.check_answer(answer['question_id'], answer['selected'])
        
        profile = quiz_instance.calculate_skill_profile()
        skills = profile['skills']
        display_skills = profile['display_skills']
        
        session['user_skills'] = skills
        session['display_skills'] = display_skills
        
        recommendations = recommender.get_recommendations(skills)
        
        return jsonify({
            'success': True,
            'skills': display_skills,
            'recommendations': recommendations,
            'score': profile['score'],
            'total_possible': profile['total_possible']
        })
    except Exception as e:
        print(f"❌ Quiz error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    """Get beautiful job recommendations"""
    try:
        data = request.json
        print("📥 Received skills:", data)
        
        skills_text = data.get('skills', '')
        experience = data.get('experience', 'entry')
        
        if isinstance(skills_text, str):
            skills_list = [s.strip() for s in skills_text.split(',') if s.strip()]
        else:
            skills_list = []
        
        print("🎯 Skills:", skills_list)
        print("💼 Experience:", experience)
        
        session['user_skills'] = skills_list
        
        recommendations = recommender.get_recommendations(skills_list)
        print(f"✅ Found {len(recommendations)} colorful matches")
        
        return jsonify({
            'success': True,
            'skills': skills_list,
            'experience': experience,
            'recommendations': recommendations
        })
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/skill-gap/<int:job_id>')
def skill_gap(job_id):
    """Get beautiful skill gap analysis"""
    try:
        user_skills = session.get('user_skills', [])
        
        if not user_skills:
            return jsonify({'error': 'No skills found'}), 400
        
        gap_analysis = recommender.analyze_skill_gap(user_skills, job_id)
        
        return jsonify({
            'gaps': gap_analysis.get('missing_skills', []),
            'matched': gap_analysis.get('matched_skills', []),
            'total_required': gap_analysis.get('total_required', 0),
            'total_matched': gap_analysis.get('total_matched', 0)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/learning-resources')
def learning_resources():
    """Get colorful learning resources"""
    skills = request.args.get('skills', '').split(',')
    
    resources_db = {
        'python': [{'title': '🐍 Python for Beginners', 'platform': 'Coursera', 'url': '#', 'difficulty': '🌟 Beginner'}],
        'sql': [{'title': '🗄️ SQL Mastery', 'platform': 'Udemy', 'url': '#', 'difficulty': '🌟 Beginner'}],
        'javascript': [{'title': '📜 JavaScript Complete', 'platform': 'freeCodeCamp', 'url': '#', 'difficulty': '🌟 Beginner'}],
        'machine_learning': [{'title': '🤖 Machine Learning A-Z', 'platform': 'Coursera', 'url': '#', 'difficulty': '🚀 Intermediate'}],
        'aws': [{'title': '☁️ AWS Certified', 'platform': 'AWS Training', 'url': '#', 'difficulty': '🚀 Intermediate'}],
        'docker': [{'title': '🐳 Docker Mastery', 'platform': 'Udemy', 'url': '#', 'difficulty': '🚀 Intermediate'}],
        'communication': [{'title': '💬 Communication Skills', 'platform': 'LinkedIn', 'url': '#', 'difficulty': '🌟 Beginner'}]
    }
    
    result = []
    for skill in skills:
        skill = skill.strip().lower()
        if skill in resources_db:
            result.append({
                'skill': skill,
                'resources': resources_db[skill]
            })
    
    return jsonify({'resources': result})

@app.route('/resume-tips')
def resume_tips():
    """Get beautiful resume tips"""
    tips = [
        {
            'category': '🎯 Keywords to Include',
            'tips': [
                'Use action verbs: Developed, Implemented, Led, Created',
                'Include relevant technical skills',
                'Add industry-specific keywords from job descriptions'
            ]
        },
        {
            'category': '📄 Formatting Tips',
            'tips': [
                'Keep resume to 1-2 pages',
                'Use clean, professional layout',
                'Use bullet points for readability'
            ]
        },
        {
            'category': '✨ Content Suggestions',
            'tips': [
                'Quantify achievements with numbers',
                'Tailor resume for each job',
                'Include relevant projects and outcomes'
            ]
        }
    ]
    
    return jsonify({'tips': tips})

if __name__ == '__main__':
    app.run(debug=True, port=5000)