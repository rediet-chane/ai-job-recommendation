from flask import Flask, render_template, request, jsonify, session
import secrets
import random
import json
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
    print("✅ Job data loaded successfully!")
except Exception as e:
    print(f"⚠️ Could not load jobs: {e}")

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/quiz')
def quiz():
    """Quiz page"""
    return render_template('quiz.html')

@app.route('/get-quiz-questions')
def get_quiz_questions():
    """Get quiz questions"""
    try:
        quiz_instance = SkillQuiz()
        questions = quiz_instance.get_questions()
        print(f"✅ Loaded {len(questions)} quiz questions")
        return jsonify({'questions': questions})
    except Exception as e:
        print(f"❌ Error loading quiz questions: {e}")
        return jsonify({'questions': [], 'error': str(e)}), 500

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    """Process quiz submission"""
    try:
        data = request.json
        print(f"📥 Quiz submission received: {data}")
        
        answers = data.get('answers', [])
        
        if not answers:
            return jsonify({'success': False, 'error': 'No answers provided'}), 400
        
        print(f"📝 Processing {len(answers)} answers")
        
        quiz_instance = SkillQuiz()
        
        # Process each answer
        for answer in answers:
            question_id = answer.get('question_id')
            selected = answer.get('selected')
            if question_id is not None and selected is not None:
                quiz_instance.check_answer(question_id, selected)
        
        # Generate skill profile
        profile = quiz_instance.calculate_skill_profile()
        skills = profile.get('skills', [])
        display_skills = profile.get('display_skills', [])
        
        print(f"✅ Quiz completed - Score: {profile.get('score', 0)}/{profile.get('total_possible', 0)}")
        print(f"📊 Skills identified: {display_skills}")
        
        # Store in session
        session['user_skills'] = skills
        session['display_skills'] = display_skills
        
        # Get recommendations
        recommendations = []
        if skills:
            recommendations = recommender.get_recommendations(skills)
            print(f"🎯 Found {len(recommendations)} job recommendations")
        else:
            print("⚠️ No skills identified, skipping recommendations")
        
        return jsonify({
            'success': True,
            'skills': display_skills,
            'recommendations': recommendations,
            'score': profile.get('score', 0),
            'total_possible': profile.get('total_possible', 0)
        })
        
    except Exception as e:
        print(f"❌ Error in submit-quiz: {e}")
        import traceback
        traceback.print_exc()  # This will print the full error in terminal
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/manual-input')
def manual_input():
    """Manual skill input page"""
    return render_template('manual_input.html')

@app.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    """Get job recommendations from skills"""
    try:
        data = request.json
        print(f"📥 Received skills data: {data}")
        
        skills_text = data.get('skills', '')
        experience = data.get('experience', 'entry')
        
        # Parse skills
        if isinstance(skills_text, str):
            skills_list = [s.strip() for s in skills_text.split(',') if s.strip()]
        else:
            skills_list = []
        
        print(f"📋 Skills parsed: {skills_list}")
        print(f"💼 Experience level: {experience}")
        
        # Store in session
        session['user_skills'] = skills_list
        session['display_skills'] = skills_list
        session['experience'] = experience
        
        # Get recommendations
        recommendations = recommender.get_recommendations(skills_list)
        print(f"✅ Found {len(recommendations)} recommendations")
        
        return jsonify({
            'success': True,
            'skills': skills_list,
            'experience': experience,
            'recommendations': recommendations
        })
    except Exception as e:
        print(f"❌ Error in get-recommendations: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/skill-gap/<int:job_id>')
def skill_gap(job_id):
    """Get skill gap analysis for a specific job"""
    try:
        user_skills = session.get('user_skills', [])
        
        if not user_skills:
            return jsonify({'error': 'No skills found in session'}), 400
        
        # Get job details
        job = recommender.jobs_df[recommender.jobs_df['job_id'] == job_id].iloc[0]
        
        # Parse required skills
        required_skills = [s.strip().lower() for s in str(job.get('required_skills', '')).split(',') if s.strip()]
        user_skills_lower = [s.lower() for s in user_skills]
        
        # Find gaps
        gaps = []
        for skill in required_skills:
            if skill and skill not in user_skills_lower:
                # Determine priority
                freq = recommender.jobs_df['required_skills'].str.lower().str.contains(skill).mean()
                if freq > 0.7:
                    priority = 'High'
                elif freq > 0.4:
                    priority = 'Medium'
                else:
                    priority = 'Low'
                
                gaps.append({
                    'skill': skill.title(),
                    'priority': priority
                })
        
        print(f"📊 Skill gap analysis for job {job_id}: {len(gaps)} gaps found")
        
        return jsonify({
            'gaps': gaps,
            'job_title': job['title']
        })
    except Exception as e:
        print(f"❌ Error in skill-gap: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/learning-resources')
def learning_resources():
    """Get learning resources for skills"""
    try:
        skills = request.args.get('skills', '').split(',')
        
        # Sample resources database
        resources_db = {
            'python': [
                {'title': '🐍 Python for Beginners', 'platform': 'Coursera', 'url': '#', 'difficulty': 'Beginner'},
                {'title': 'Complete Python Bootcamp', 'platform': 'Udemy', 'url': '#', 'difficulty': 'Beginner'}
            ],
            'sql': [
                {'title': '🗄️ SQL Mastery', 'platform': 'Udemy', 'url': '#', 'difficulty': 'Beginner'}
            ],
            'javascript': [
                {'title': '📜 JavaScript Complete', 'platform': 'freeCodeCamp', 'url': '#', 'difficulty': 'Beginner'}
            ],
            'machine learning': [
                {'title': '🤖 Machine Learning A-Z', 'platform': 'Coursera', 'url': '#', 'difficulty': 'Intermediate'}
            ],
            'aws': [
                {'title': '☁️ AWS Certified', 'platform': 'AWS Training', 'url': '#', 'difficulty': 'Intermediate'}
            ],
            'docker': [
                {'title': '🐳 Docker Mastery', 'platform': 'Udemy', 'url': '#', 'difficulty': 'Intermediate'}
            ],
            'communication': [
                {'title': '💬 Communication Skills', 'platform': 'LinkedIn', 'url': '#', 'difficulty': 'Beginner'}
            ]
        }
        
        result = []
        for skill in skills:
            skill_clean = skill.strip().lower()
            if skill_clean in resources_db:
                result.append({
                    'skill': skill_clean,
                    'resources': resources_db[skill_clean]
                })
        
        return jsonify({'resources': result})
    except Exception as e:
        print(f"❌ Error in learning-resources: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/resume-tips')
def resume_tips():
    """Get resume tips"""
    try:
        tips = [
            {
                'category': '🎯 Keywords to Include',
                'tips': [
                    'Use action verbs: Developed, Implemented, Led, Created',
                    'Include relevant technical skills from job descriptions',
                    'Add industry-specific keywords'
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
                    'Tailor resume for each job application',
                    'Include relevant projects and outcomes'
                ]
            }
        ]
        
        return jsonify({'tips': tips})
    except Exception as e:
        print(f"❌ Error in resume-tips: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)