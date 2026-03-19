@echo off
echo ========================================
echo 🤖 Starting Ethiopian Job Scraper
echo Date: %date% Time: %time%
echo ========================================

cd /d C:\Users\Redie\ai-job-recommendation

C:\Users\Redie\ai-job-recommendation\venv\Scripts\python.exe data/telegram_scraper.py

echo ✅ Scraper finished at %time%
echo ========================================
pause