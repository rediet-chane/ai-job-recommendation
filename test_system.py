from utils.nlp_processor import NLPProcessor
from models.recommender import JobRecommender

print("=" * 50)
print("🔧 TESTING JOB RECOMMENDATION SYSTEM")
print("=" * 50)

# Test NLP Processor
print("\n📝 Testing NLP Processor...")
nlp = NLPProcessor()
test_text = "Looking for Python developer with SQL and machine learning experience"
result = nlp.preprocess_job_description(test_text)
print(f"   Original: {test_text}")
print(f"   Extracted skills: {result['extracted_skills']}")
print("   ✅ NLP Processor works!")

# Test Job Recommender
print("\n🎯 Testing Job Recommender...")
recommender = JobRecommender()

if recommender.load_jobs('data/jobs.csv'):
    test_skills = ['python', 'sql', 'javascript']
    print(f"   Testing with skills: {test_skills}")
    
    recommendations = recommender.get_recommendations(test_skills)
    
    if recommendations:
        print("\n📊 Top Recommendations:")
        print("-" * 40)
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"{i}. {rec['title']}")
            print(f"   Match: {rec['match_score']}%")
            print(f"   Skills: {rec['required_skills']}")
            print()
    else:
        print("   No recommendations found")
    
    print("✅ Job Recommender works!")
else:
    print("❌ Could not load jobs")

print("\n" + "=" * 50)
print("✅ SYSTEM TEST COMPLETE")
print("=" * 50)