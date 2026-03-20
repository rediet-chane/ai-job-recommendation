import pandas as pd
from models.smart_matcher import SmartMatcher

matcher = SmartMatcher()
matcher.load_jobs('data/jobs.csv')

print("\n📊 Testing with skills: python, sql")
recs = matcher.get_recommendations(['python', 'sql'])
for rec in recs[:3]:
    print(f"  {rec['title']} - {rec['match_score']}%")

print("\n📊 Testing with typo: pyton")
recs = matcher.get_recommendations(['pyton'])
for rec in recs[:3]:
    print(f"  {rec['title']} - {rec['match_score']}%")

print("\n✅ System test complete!")