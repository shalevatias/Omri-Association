@echo off
echo בדיקת התקנת Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo Python לא מותקן במערכת.
    echo אנא התקן Python מהאתר הרשמי: https://www.python.org/downloads/
    echo וודא שסימנת את האפשרות "Add Python to PATH" בזמן ההתקנה.
    pause
    exit
)

echo בדיקת התקנת חבילות נדרשות...
python -m pip install --upgrade pip
python -m pip install streamlit pandas plotly openpyxl

echo הפעלת הדשבורד...
start http://localhost:8501
streamlit run dashboard.py

pause 