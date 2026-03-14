import json
import random

class SkillQuiz:
    def __init__(self):
        """Initialize quiz with questions"""
        self.questions = self.load_questions()
        self.current_score = 0
        self.responses = []
        
    def load_questions(self):
        """Load quiz questions"""
        return [
            {
                'id': 1,
                'category': 'Programming',
                'question': 'How would you process a large CSV file that doesn\'t fit in memory?',
                'options': [
                    'Load the entire file with pandas.read_csv()',
                    'Use chunksize parameter to process in batches',
                    'Convert to Excel first',
                    'Split the file manually with a text editor'
                ],
                'correct': 1,
                'skill': 'python',
                'weight': 3
            },
            {
                'id': 2,
                'category': 'Data Analysis',
                'question': 'What method is best for handling missing values in a dataset?',
                'options': [
                    'Delete all rows with missing values',
                    'Fill with mean/median or use interpolation',
                    'Ignore them completely',
                    'Convert them to zeros'
                ],
                'correct': 1,
                'skill': 'data_analysis',
                'weight': 2
            },
            {
                'id': 3,
                'category': 'Database',
                'question': 'Which SQL command is used to retrieve data from a database?',
                'options': [
                    'INSERT',
                    'UPDATE',
                    'SELECT',
                    'DELETE'
                ],
                'correct': 2,
                'skill': 'sql',
                'weight': 2
            },
            {
                'id': 4,
                'category': 'Soft Skills',
                'question': 'A teammate misses deadlines repeatedly. What\'s the best approach?',
                'options': [
                    'Report to manager immediately',
                    'Privately discuss challenges and offer help',
                    'Ignore it to avoid conflict',
                    'Do their work for them'
                ],
                'correct': 1,
                'skill': 'communication',
                'weight': 1
            },
            {
                'id': 5,
                'category': 'Web Development',
                'question': 'What does API stand for?',
                'options': [
                    'Application Programming Interface',
                    'Advanced Programming Integration',
                    'Application Process Integration',
                    'Automated Program Interface'
                ],
                'correct': 0,
                'skill': 'api',
                'weight': 1
            }
        ]
    
    def get_questions(self):
        """Get all questions"""
        return self.questions
    
    def check_answer(self, question_id, selected_option):
        """Check if answer is correct"""
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
                'points_earned': question['weight'] if is_correct else 0
            }
        return None
    
    def calculate_skill_profile(self):
        """Generate skill profile from quiz responses"""
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
        
        # Generate skill list based on performance
        skills = []
        display_skills = []
        
        for skill, scores in skill_scores.items():
            if scores['correct'] > 0:
                # Add skill multiple times based on proficiency
                proficiency = scores['correct'] / scores['total']
                count = max(1, int(proficiency * 3))
                skills.extend([skill] * count)
                display_skills.append(skill)
        
        return {
            'skills': list(set(skills)),  # Remove duplicates for processing
            'display_skills': list(set(display_skills)),  # For display
            'score': self.current_score,
            'total_possible': total_possible
        }
    
    def reset(self):
        """Reset quiz state"""
        self.current_score = 0
        self.responses = []

# Test the quiz
if __name__ == "__main__":
    quiz = SkillQuiz()
    print(f"✅ Loaded {len(quiz.questions)} questions")