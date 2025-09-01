# 🚀 Setup Guide for Risk Stratification Web Application

This guide will help you set up and run the Risk Stratification Web Application on your local machine.

## 📋 Prerequisites

Before you start, make sure you have:

- **Python 3.8+** installed on your system
- **Git** installed for cloning the repository
- **Internet connection** for downloading dependencies

## 🔧 Step-by-Step Setup

### Step 1: Clone the Repository

```bash
git clone <your-github-repo-url>
cd Risk_App12
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Set Up Email Configuration (Optional)

Create an `email_config.env` file in the root directory:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
EMAIL_FROM_NAME=Risk Stratification System
```

**Note**: If you don't set up email, the app will still work but won't send email reports.

### Step 5: Train the Model (First Time Only)

```bash
python train_model.py
```

This will:
- Load the training data from `trainingk.csv`
- Train a new ML model with weighted disease scoring
- Save the model to `models/risk_model.pkl`

### Step 6: Run the Application

```bash
python app.py
```

You should see output like:
```
🚀 Starting Risk Stratification Web App (CSV-based)...
📊 Dashboard: http://localhost:5000
📁 Data Source: trainingk.csv
🤖 ML Model: Loaded
API endpoints:
 - /api/data
 - /api/summary
 - /api/health
 - /api/predict (POST)
 * Debugger is active!
 * Running on http://127.0.0.1:5000
```

### Step 7: Access the Dashboard

Open your web browser and go to:
```
http://localhost:5000
```

## 🎯 What You Can Do

### 1. View Existing Patient Data
- The dashboard will show 100 patients by default
- Use filters to search by risk level, gender, age
- Export data as PDF reports

### 2. Add New Patients
- Fill out the "New Patient" form
- Include all required fields:
  - Demographics (Age, Gender)
  - Vitals (BMI, BP, Glucose, HbA1c, Cholesterol)
  - Chronic conditions (check the diseases present)
  - Insurance info (PartA, PartB, HMO, PartD)
  - Healthcare utilization (admissions, visits)
  - Contact info (Email, Index Date)
- Click "Predict Risk" to get instant predictions
- Patient data is automatically saved to `trainingk.csv`

### 3. Understand Risk Predictions
- **30-Day Risk**: Risk of readmission in 30 days
- **60-Day Risk**: Risk of readmission in 60 days  
- **90-Day Risk**: Risk of readmission in 90 days
- **Risk Label**: Overall risk category (Very Low to Very High)

## 🏥 Disease Weightage System

The system uses weighted scoring for chronic diseases:

| Disease | Weight | Risk Level |
|---------|--------|------------|
| Heart Failure | 3.0 | Highest |
| Stroke | 2.8 | Very High |
| Cancer | 2.5 | High |
| Renal Disease | 2.3 | High |
| Pulmonary | 2.0 | Moderate-High |
| Alzheimer's | 1.8 | Moderate |
| Rheumatoid | 1.5 | Moderate |
| Osteoporosis | 1.2 | Lower |

## 🔧 Troubleshooting

### Common Issues:

1. **"No module named 'flask'"**
   ```bash
   pip install flask
   ```

2. **"Model not found"**
   ```bash
   python train_model.py
   ```

3. **"Port 5000 already in use"**
   - Kill the process using port 5000
   - Or change the port in `app.py`

4. **"Permission denied"**
   - Make sure you have write permissions in the directory
   - Try running as administrator (Windows) or with sudo (Linux/Mac)

### File Structure After Setup:

```
Risk_App12/
├── app.py                  # Main application
├── train_model.py          # Model training
├── trainingk.csv           # Patient data
├── requirements.txt        # Dependencies
├── email_config.env        # Email config (optional)
├── models/
│   └── risk_model.pkl     # Trained model
├── risk/                  # ML modules
├── templates/
│   └── index.html         # Web interface
└── README.md              # Documentation
```

## 📊 Data Overview

- **Total Patients**: 56,634+ patients in `trainingk.csv`
- **Features**: 29 comprehensive features
- **Model Performance**: R² = 0.67+ (good predictive power)
- **Risk Categories**: 5 levels from Very Low to Very High

## 🚀 Quick Test

1. Run the app: `python app.py`
2. Open browser: `http://localhost:5000`
3. Fill out a new patient form with:
   - Age: 75
   - Heart Failure: Checked
   - Stroke: Checked
   - High vitals (BP: 180, Glucose: 200)
4. Click "Predict Risk"
5. You should see "Very High Risk" predictions!

## 📞 Support

If you encounter any issues:
1. Check the terminal output for error messages
2. Ensure all dependencies are installed
3. Make sure Python 3.8+ is being used
4. Verify the model was trained successfully

## 🎉 You're Ready!

Your Risk Stratification Web Application is now running! You can start predicting patient risks and managing healthcare data.
