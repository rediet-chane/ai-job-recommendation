import random

class SkillQuiz:
    def __init__(self):
        """Initialize quiz with questions"""
        self.questions = self.load_questions()
        self.current_score = 0
        self.responses = []
        print("🎨 Loading quiz questions...")
        
    def load_questions(self):
        """Load quiz questions"""
        return [
            {
                'id': 1,
                'category': '💻 Programming',
                'question': 'How would you process a large CSV file that doesn\'t fit in memory?',
                'options': [
                    'Load entire file with pandas.read_csv()',
                    'Use chunksize parameter to process in batches',
                    'Convert to Excel first',
                    'Split the file manually with a text editor'
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
        
        # If no responses, return empty profile
        if not self.responses:
            return {
                'skills': [],
                'display_skills': [],
                'score': 0,
                'total_possible': total_possible
            }
        
        for response in self.responses:
            skill = response['skill']
            if skill not in skill_scores:
                skill_scores[skill] = {'correct': 0, 'total': 0, 'weight': 0}
            
            # Find the question to get its weight
            question = next((q for q in self.questions if q['id'] == response['question_id']), None)
            if question:
                skill_scores[skill]['total'] += 1
                skill_scores[skill]['weight'] += question['weight']
                
                if response['correct']:
                    skill_scores[skill]['correct'] += 1
        
        # Generate skills based on performance
        skills = []
        display_skills = []
        
        for skill, scores in skill_scores.items():
            if scores['correct'] > 0:
                # Add the skill to the list
                display_skills.append(skill)
                # Add multiple times based on proficiency for better matching
                proficiency = scores['correct'] / max(scores['total'], 1)
                count = max(1, int(proficiency * 2))
                skills.extend([skill] * count)
        
        # Ensure we have at least one skill
        if not skills:
            skills = ['python']  # Default skill
            display_skills = ['Python']
        
        return {
            'skills': skills,
            'display_skills': display_skills,
            'score': self.current_score,
            'total_possible': total_possible
        }

# Test
if __name__ == "__main__":
    quiz = SkillQuiz()
    print(f"✅ Loaded {len(quiz.questions)} quiz questions")