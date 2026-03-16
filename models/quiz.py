import random

class SkillQuiz:
    def __init__(self):
        """Initialize beautiful quiz with colorful questions"""
        self.questions = self.load_questions()
        self.current_score = 0
        self.responses = []
        print("🎨 Loading colorful quiz questions...")
        
    def load_questions(self):
        """Load beautiful quiz questions with categories"""
        return [
            {
                'id': 1,
                'category': '💻 Programming',
                'question': 'How would you process a large CSV file that doesn\'t fit in memory?',
                'options': [
                    'Load entire file with pandas.read_csv()',
                    'Use chunksize parameter to process in batches',
                    'Convert to Excel first',
                    'Use a text editor to split manually'
                ],
                'correct': 1,
                'skill': 'python',
                'weight': 3,
                'explanation': 'Using chunksize allows processing large files in manageable batches!'
            },
            {
                'id': 2,
                'category': '🗄️ Database',
                'question': 'Which SQL command is used to retrieve data from a database?',
                'options': ['INSERT', 'UPDATE', 'SELECT', 'DELETE'],
                'correct': 2,
                'skill': 'sql',
                'weight': 2,
                'explanation': 'SELECT is the command to query and retrieve data!'
            },
            {
                'id': 3,
                'category': '🤖 Machine Learning',
                'question': 'Which algorithm is best for classification problems?',
                'options': [
                    'Linear Regression',
                    'K-Means Clustering',
                    'Random Forest',
                    'Apriori Algorithm'
                ],
                'correct': 2,
                'skill': 'machine_learning',
                'weight': 3,
                'explanation': 'Random Forest is excellent for classification tasks!'
            },
            {
                'id': 4,
                'category': '💼 Soft Skills',
                'question': 'A teammate misses deadlines. What\'s the best approach?',
                'options': [
                    'Report to manager immediately',
                    'Privately discuss and offer help',
                    'Ignore it to avoid conflict',
                    'Do their work for them'
                ],
                'correct': 1,
                'skill': 'communication',
                'weight': 1,
                'explanation': 'Private, supportive communication is key!'
            },
            {
                'id': 5,
                'category': '☁️ Cloud',
                'question': 'What does IaaS stand for in cloud computing?',
                'options': [
                    'Infrastructure as a Service',
                    'Internet as a Service',
                    'Integration as a Service',
                    'Identity as a Service'
                ],
                'correct': 0,
                'skill': 'aws',
                'weight': 2,
                'explanation': 'IaaS provides virtualized computing resources over the internet!'
            },
            {
                'id': 6,
                'category': '🔧 DevOps',
                'question': 'What is Docker primarily used for?',
                'options': [
                    'Virtual machines',
                    'Containerization',
                    'Database management',
                    'Version control'
                ],
                'correct': 1,
                'skill': 'docker',
                'weight': 2,
                'explanation': 'Docker containerizes applications for consistency across environments!'
            },
            {
                'id': 7,
                'category': '🎨 Design',
                'question': 'What does UX stand for?',
                'options': [
                    'User Experience',
                    'Universal XML',
                    'Unix Extension',
                    'User Xpress'
                ],
                'correct': 0,
                'skill': 'ux_design',
                'weight': 1,
                'explanation': 'UX focuses on the overall feel of the user experience!'
            }
        ]
    
    def get_questions(self):
        """Get shuffled questions"""
        questions = self.questions.copy()
        random.shuffle(questions)
        return questions
    
    def check_answer(self, question_id, selected_option):
        """Check answer and return result"""
        question = next((q for q in self.questions if q['id'] == question_id), None)
        if question:
            is_correct = (selected_option == question['correct'])
            self.responses.append({
                'question_id': question_id,
                'selected': selected_option,
                'correct': is_correct,
                'skill': question['skill'],
                'weight': question['weight']
            })
            
            if is_correct:
                self.current_score += question['weight']
            
            return {
                'correct': is_correct,
                'skill': question['skill'],
                'points': question['weight'] if is_correct else 0,
                'explanation': question.get('explanation', '')
            }
        return None
    
    def calculate_skill_profile(self):
        """Generate skill profile from responses"""
        skill_scores = {}
        total_possible = sum(q['weight'] for q in self.questions)
        
        for response in self.responses:
            skill = response['skill']
            if skill not in skill_scores:
                skill_scores[skill] = {'correct': 0, 'total': 0, 'weight': 0}
            
            question = next(q for q in self.questions if q['id'] == response['question_id'])
            skill_scores[skill]['total'] += 1
            skill_scores[skill]['weight'] += question['weight']
            
            if response['correct']:
                skill_scores[skill]['correct'] += 1
        
        # Generate skills based on performance
        skills = []
        display_skills = []
        
        for skill, scores in skill_scores.items():
            if scores['correct'] > 0:
                proficiency = scores['correct'] / scores['total']
                count = max(1, int(proficiency * 3))
                skills.extend([skill] * count)
                display_skills.append(skill)
        
        return {
            'skills': list(set(skills)),
            'display_skills': list(set(display_skills)),
            'score': self.current_score,
            'total_possible': total_possible
        }
    
    def reset(self):
        """Reset quiz"""
        self.current_score = 0
        self.responses = []

# Test
if __name__ == "__main__":
    quiz = SkillQuiz()
    print(f"✅ Loaded {len(quiz.questions)} beautiful questions")