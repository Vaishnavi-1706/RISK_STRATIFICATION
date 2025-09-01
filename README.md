# Risk Stratification Web Application

A comprehensive web application for predicting patient risk using machine learning with weighted disease scoring and AI-powered recommendations.

## 🚀 Features

- **ML-Powered Risk Prediction**: Uses Random Forest model with 29 features
- **Weighted Disease Scoring**: Each chronic disease has specific weight based on severity
- **AI Recommendations**: Intelligent recommendations based on patient risk factors
- **CSV-Based Data Management**: Easy data import/export with `trainingk.csv`
- **Real-time Predictions**: Instant risk assessment for new patients
- **PDF Report Generation**: Automated patient reports with charts
- **Email Integration**: Send reports directly to patients/doctors
- **Responsive Dashboard**: Modern web interface with filtering and search

## 🏥 Disease Weightage System

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

## 📊 Model Performance

- **Features Used**: 29 comprehensive features
- **Average R²**: 0.67+ (good predictive power)
- **Risk Predictions**: 30-day, 60-day, 90-day risk scores
- **Risk Labels**: Very Low, Low, Moderate, High, Very High

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd Risk_App12
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Access the dashboard**:
   Open your browser and go to `http://localhost:5000`

## 📁 Project Structure

```
Risk_App12/
├── app.py              # Main Flask application
├── train_model.py          # Model training script
├── trainingk.csv           # Patient data (56K+ records)
├── requirements.txt        # Python dependencies
├── risk/                   # Core ML modules
│   ├── model.py           # Model loading/prediction
│   ├── preprocess.py      # Feature preprocessing
│   ├── recommendations.py # AI recommendations
│   └── email_service.py   # Email functionality
├── templates/
│   └── index.html         # Web dashboard
├── models/                # Trained ML models
└── README.md             # This file
```

## 🎯 Usage

### Training a New Model
```bash
python train_model.py
```

### Adding New Patients
1. Fill out the "New Patient" form on the dashboard
2. Include all required fields (age, vitals, chronic conditions)
3. Click "Predict Risk" to get instant predictions
4. Patient data is automatically saved to `trainingk.csv`

### Viewing Patient Data
- Use filters to search by risk level, gender, age
- Export data as PDF reports
- Send bulk emails to patient groups

## 🔧 Configuration

### Email Setup
Create an `email_config.env` file:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
EMAIL_FROM_NAME=Risk Stratification System
```

## 📈 Key Features

- **Weighted Disease Scoring**: More accurate than simple disease counting
- **All 29 Features**: Comprehensive patient data analysis
- **2 Decimal Precision**: Clean, professional risk score display
- **Real-time Updates**: Instant predictions and data saving
- **Professional Reports**: PDF generation with charts and recommendations

## 🤖 AI Recommendations

The system generates intelligent recommendations based on:
- Patient risk level
- Chronic conditions present
- Age and vital signs
- Healthcare utilization patterns

## 📊 Data Management

- **Primary Data Source**: `trainingk.csv` (56,634+ patients)
- **Automatic Saving**: New patients saved immediately
- **Data Export**: PDF reports and CSV exports
- **Backup Compatible**: Easy data migration and backup

## 🚀 Quick Start

1. Run `python app.py`
2. Open `http://localhost:5000`
3. Fill out a new patient form
4. Get instant risk predictions
5. View patient data in the dashboard

## 📝 License

This project is for educational and research purposes.

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

---

**Built with**: Python, Flask, scikit-learn, pandas, ReportLab, Bootstrap