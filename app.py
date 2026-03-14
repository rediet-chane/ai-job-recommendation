from flask import Flask, render_template, request, jsonify, session
import os
import secrets
import os
import secrets
import random  # <-- ADD THIS LINE
import json
from flask import Flask, render_template, request, jsonify, session
from utils.nlp_processor import NLPProcessor
from models.recommender import JobRecommender
from models.quiz import SkillQuiz
import json

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
    print(f"❌ Error loading jobs: {e}")

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
        
        # Check if questions exist
        if not questions:
            print("❌ No quiz questions found!")
            return jsonify({'questions': [], 'error': 'No questions available'})
        
        # Shuffle questions for variety
        random.shuffle(questions)
        print(f"✅ Loaded {len(questions)} quiz questions")
        return jsonify({'questions': questions})
    except Exception as e:
        print(f"❌ Error loading quiz: {e}")
        return jsonify({'questions': [], 'error': str(e)}), 500
@app.route('/manual-input')
def manual_input():
    """Manual skill input page"""
    return render_template('manual_input.html')

@app.route('/submit-quiz', methods=['POST'])
def submit_quiz():
    """Process quiz submission"""
    try:
        data = request.json
        answers = data.get('answers', [])
        
        quiz_instance = SkillQuiz()
        
        # Process each answer
        for answer in answers:
            quiz_instance.check_answer(answer['question_id'], answer['selected'])
        
        # Generate skill profile
        profile = quiz_instance.calculate_skill_profile()
        skills = profile['skills']
        display_skills = profile['display_skills']
        
        # Store in session
        session['user_skills'] = skills
        session['display_skills'] = display_skills
        
        # Get recommendations
        recommendations = recommender.get_recommendations(skills)
        
        return jsonify({
            'success': True,
            'skills': display_skills,
            'recommendations': recommendations,
            'score': profile['score'],
            'total_possible': profile['total_possible']
        })
    except Exception as e:
        print(f"Error in submit-quiz: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/get-recommendations', methods=['POST'])
def get_recommendations():
    """Get job recommendations from skills"""
    try:
        data = request.json
        print("📥 Received data:", data)
        
        skills_text = data.get('skills', '')
        experience = data.get('experience', 'entry')
        
        # Parse skills
        if isinstance(skills_text, str):
            skills_list = [s.strip() for s in skills_text.split(',') if s.strip()]
        else:
            skills_list = []
        
        print("📋 Skills:", skills_list)
        print("💼 Experience:", experience)
        
        # Store in session
        session['user_skills'] = skills_list
        session['display_skills'] = skills_list
        session['experience'] = experience
        
        # Get recommendations (filter by experience if your model supports it)
        recommendations = recommender.get_recommendations(skills_list)
        
        # Filter by experience level if job data has experience_level
        filtered_recommendations = []
        for rec in recommendations:
            # You can add experience filtering logic here if your job data has experience_level
            filtered_recommendations.append(rec)
        
        print(f"✅ Found {len(filtered_recommendations)} recommendations")
        
        return jsonify({
            'success': True,
            'skills': skills_list,
            'experience': experience,
            'recommendations': filtered_recommendations
        })
    except Exception as e:
        print(f"❌ Error in get-recommendations: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/skill-gap/<int:job_id>')
def skill_gap(job_id):
    """Get skill gap analysis for a specific job"""
    try:
        user_skills = session.get('user_skills', [])
        
        if not user_skills:
            return jsonify({'error': 'No user skills found'}), 400
        
        # Get job details
        job = recommender.jobs_df[recommender.jobs_df['job_id'] == job_id].iloc[0]
        
        # Parse required skills
        required_skills = [s.strip().lower() for s in str(job.get('required_skills', '')).split(',')]
        user_skills_lower = [s.lower() for s in user_skills]
        
        # Find gaps
        gaps = []
        for skill in required_skills:
            if skill and skill not in user_skills_lower:
                # Determine priority based on frequency
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
            'gaps': gaps,
            'job_title': job['title']
        })
    except Exception as e:
        print(f"Error in skill-gap: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/learning-resources')
def learning_resources():
    """Get learning resources for skills"""
    try:
        skills = request.args.get('skills', '').split(',')
        
        # Define resources
        resources_db = {
            'python': [{'title': 'Python for Beginners', 'platform': 'Coursera', 'url': '#', 'difficulty': 'Beginner'}],
            'sql': [{'title': 'SQL Fundamentals', 'platform': 'Udemy', 'url': '#', 'difficulty': 'Beginner'}],
            'javascript': [{'title': 'JavaScript Tutorial', 'platform': 'freeCodeCamp', 'url': '#', 'difficulty': 'Beginner'}],
            'machine learning': [{'title': 'Machine Learning Course', 'platform': 'Coursera', 'url': '#', 'difficulty': 'Intermediate'}],
            'data analysis': [{'title': 'Data Analysis with Python', 'platform': 'edX', 'url': '#', 'difficulty': 'Intermediate'}],
            'communication': [{'title': 'Effective Communication', 'platform': 'LinkedIn Learning', 'url': '#', 'difficulty': 'Beginner'}]
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
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/resume-tips')
def resume_tips():
    """Generate resume tips"""
    try:
        tips = [
            {
                'category': 'Keywords to Include',
                'tips': [
                    'Use action verbs: Developed, Implemented, Managed, Created',
                    'Include relevant technical skills',
                    'Add industry-specific keywords'
                ]
            },
            {
                'category': 'Formatting Tips',
                'tips': [
                    'Keep resume to 1-2 pages',
                    'Use clean, professional layout',
                    'Use bullet points for readability'
                ]
            },
            {
                'category': 'Content Suggestions',
                'tips': [
                    'Quantify achievements with numbers',
                    'Tailor resume for each job',
                    'Include relevant projects'
                ]
            }
        ]
        
        return jsonify({'tips': tips})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test-recommender')
def test_recommender():
    """Test route"""
    try:
        test_skills = ['python', 'sql']
        recommendations = recommender.get_recommendations(test_skills)
        return jsonify({
            'working': True,
            'recommendations': recommendations
        })
    except Exception as e:
        return jsonify({'working': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)