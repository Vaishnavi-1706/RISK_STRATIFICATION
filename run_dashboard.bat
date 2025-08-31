@echo off
echo Starting Healthcare Risk Dashboard...
echo.
echo Installing dependencies...
pip install -r dashboard_requirements.txt
echo.
echo Starting Streamlit dashboard...
echo Dashboard will be available at: http://localhost:8501
echo.
streamlit run dashboard.py
pause
