@echo off
echo Starting Working New Patient Risk Assessment Dashboard...
echo.
echo Installing dependencies...
pip install streamlit plotly pandas numpy
echo.
echo Starting Streamlit dashboard...
echo Dashboard will be available at: http://localhost:8504
echo.
streamlit run working_patient_dashboard.py
pause
