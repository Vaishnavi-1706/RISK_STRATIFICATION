@echo off
echo Starting New Patient Risk Assessment Dashboard...
echo.
echo Installing dependencies...
pip install streamlit plotly pandas numpy
echo.
echo Starting Streamlit dashboard...
echo Dashboard will be available at: http://localhost:8502
echo.
streamlit run new_patient_dashboard.py
pause
