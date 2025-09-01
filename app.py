#!/usr/bin/env python3
"""
Risk Stratification Web Application (CSV-based)
- Reads patient data from trainingk.csv
- Supports filtering and new patient addition
- Generates AI recommendations
"""

import os
import io
import re
import smtplib
import traceback
from datetime import datetime
import pandas as pd

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from flask import Flask, render_template, jsonify, request, send_file

# ReportLab for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch

# Matplotlib for charts embedded in PDF
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt

# dotenv for env variables
from dotenv import load_dotenv
load_dotenv()

# Import AI recommendations and ML model
from risk.recommendations import get_ai_recommendations
from risk.model import load_model, assign_label
from risk.preprocess import preprocess_features, feature_cols, target_cols

# ---------------------------
# Email configuration
# ---------------------------
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", EMAIL_HOST_USER or "no-reply")

def send_email(to_email: str, subject: str, message: str, attachment_bytes: bytes = None, attachment_filename: str = None):
    """Send an email using SMTP with optional attachment"""
    if not (EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD):
        raise RuntimeError("SMTP configuration is incomplete")

    msg = MIMEMultipart()
    msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_HOST_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    body = MIMEText(message, "plain")
    msg.attach(body)

    if attachment_bytes is not None and attachment_filename:
        part = MIMEApplication(attachment_bytes, Name=attachment_filename)
        part['Content-Disposition'] = f'attachment; filename="{attachment_filename}"'
        msg.attach(part)

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(msg)

    print(f"[INFO] Email sent to {to_email} (subject: {subject})")

# ---------------------------
# CSV Data Management
# ---------------------------
CSV_FILE = "trainingk.csv"

# Load ML model
def load_ml_model():
    """Load the trained ML model"""
    try:
        # Try to load the most recent model
        model_paths = [
            "models/risk_model_20250902_010322.pkl"
        ]
        
        for model_path in model_paths:
            if os.path.exists(model_path):
                print(f"Loading ML model from {model_path}")
                return load_model(model_path)
        
        print("No ML model found, using fallback prediction")
        return None
    except Exception as e:
        print(f"Error loading ML model: {e}")
        return None

# Load model at startup
ml_model = load_ml_model()

def predict_single_patient(patient_data, regressors):
    """Predict risk for a single patient using ML model"""
    try:
        # Create DataFrame
        patient_df = pd.DataFrame([patient_data])
        
        # Preprocess
        processed_df = preprocess_features(patient_df)
        
        # Get features
        X = processed_df[feature_cols].values
        
        # Make predictions
        predictions = {}
        for col in target_cols:
            pred = regressors[col].predict(X)
            predictions[col] = float(pred[0])
        
        # Assign risk label
        risk_label = assign_label(predictions['RISK_30D'])
        
        # Generate top features (simplified - using feature importance)
        top_features = "AGE, TOTAL_CLAIMS_COST, COMOR_COUNT"  # Default
        
        # Generate AI recommendations
        ai_recommendations = get_ai_recommendations(patient_data, top_features)
        
        return {
            'RISK_30D': round(predictions['RISK_30D'], 2),
            'RISK_60D': round(predictions['RISK_60D'], 2),
            'RISK_90D': round(predictions['RISK_90D'], 2),
            'RISK_LABEL': risk_label,
            'TOP_3_FEATURES': top_features,
            'AI_RECOMMENDATIONS': ai_recommendations
        }
        
    except Exception as e:
        print(f"Error in predict_single_patient: {e}")
        raise e

def load_csv_data():
    """Load data from CSV file"""
    try:
        df = pd.read_csv(CSV_FILE, low_memory=False)
        return df
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return pd.DataFrame()

def save_csv_data(df):
    """Save data to CSV file"""
    try:
        df.to_csv(CSV_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving CSV: {e}")
        return False

def get_patient_by_id(patient_id: str):
    """Get patient data by ID"""
    df = load_csv_data()
    if df.empty:
        return pd.DataFrame()
    
    patient = df[df['DESYNPUF_ID'] == patient_id]
    return patient

# ---------------------------
# Flask app initialization
# ---------------------------
app = Flask(__name__)

# ---------------------------
# PDF Generation (same as before)
# ---------------------------
def _create_risk_bar_chart_png(risk30, risk60, risk90):
    """Create PNG bytes for risk bar chart"""
    fig, ax = plt.subplots(figsize=(6, 3.5))
    labels = ['30-day', '60-day', '90-day']
    values = [risk30 if risk30 is not None else 0,
              risk60 if risk60 is not None else 0,
              risk90 if risk90 is not None else 0]
    ax.bar(labels, values)
    ax.set_ylim(0, max(100, max(values) * 1.1))
    ax.set_ylabel('Risk (%)')
    ax.set_title('Predicted Risk over Time')
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

def _create_label_pie_chart_png(risk_label):
    """Create PNG bytes for risk label pie chart"""
    labels = [risk_label if risk_label else 'Unknown']
    sizes = [1]
    fig, ax = plt.subplots(figsize=(4, 2.5))
    ax.pie(sizes, labels=labels, startangle=90, wedgeprops=dict(width=0.5))
    ax.set_title('Risk Level')
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

def create_patient_pdf_bytes(patient: dict, include_large_table: bool = True):
    """Build a PDF report for a single patient and return bytes"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER, spaceAfter=14)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, alignment=TA_LEFT, spaceAfter=8)
    normal = styles['Normal']

    # Title
    title = Paragraph("Patient Risk Assessment Report", title_style)
    elements.append(title)

    # Patient Info block
    gender_str = 'Male' if patient.get('GENDER') == 1 else 'Female'
    info_html = f"""
    <b>Patient Information</b><br/>
    <b>Patient ID:</b> {patient.get('DESYNPUF_ID', 'N/A')}<br/>
    <b>Age:</b> {patient.get('AGE', 'N/A')}<br/>
    <b>Gender:</b> {gender_str}<br/>
    <b>Email:</b> {patient.get('EMAIL', 'Not Provided')}<br/>
    <b>Total Claims Cost:</b> {patient.get('TOTAL_CLAIMS_COST', 'N/A')}<br/>
    <b>Index Date:</b> {patient.get('INDEX_DATE', 'N/A')}<br/>
    <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    elements.append(Paragraph(info_html, normal))
    elements.append(Spacer(1, 12))

    # Risk summary table
    risk_30 = patient.get('RISK_30D', 'N/A')
    risk_60 = patient.get('RISK_60D', 'N/A')
    risk_90 = patient.get('RISK_90D', 'N/A')
    label = patient.get('RISK_LABEL', 'N/A')
    top_feats = patient.get('TOP_3_FEATURES', 'N/A')

    table_data = [
        ['Metric', 'Value'],
        ['30-Day Risk (%)', f"{risk_30}"],
        ['60-Day Risk (%)', f"{risk_60}"],
        ['90-Day Risk (%)', f"{risk_90}"],
        ['Risk Label', str(label)],
        ['Top Features', str(top_feats)]
    ]
    table = Table(table_data, colWidths=[2.5 * inch, 3.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc"))
    ]))
    elements.append(table)
    elements.append(Spacer(1, 14))

    # Charts
    try:
        bar_png = _create_risk_bar_chart_png(
            risk30=(risk_30 if isinstance(risk_30, (int, float)) else (float(risk_30) if str(risk_30).replace('.', '', 1).isdigit() else 0)),
            risk60=(risk_60 if isinstance(risk_60, (int, float)) else (float(risk_60) if str(risk_60).replace('.', '', 1).isdigit() else 0)),
            risk90=(risk_90 if isinstance(risk_90, (int, float)) else (float(risk_90) if str(risk_90).replace('.', '', 1).isdigit() else 0))
        )
        pie_png = _create_label_pie_chart_png(label)
        bar_img = Image(io.BytesIO(bar_png), width=6 * inch, height=3 * inch)
        elements.append(bar_img)
        elements.append(Spacer(1, 8))
        pie_img = Image(io.BytesIO(pie_png), width=3.5 * inch, height=2.5 * inch)
        elements.append(pie_img)
        elements.append(Spacer(1, 12))
    except Exception as chart_err:
        print(f"Chart generation error: {chart_err}")
        elements.append(Paragraph("Charts unavailable due to rendering error.", normal))
        elements.append(Spacer(1, 8))

    # AI Recommendations section
    recommendations = patient.get('AI_RECOMMENDATIONS', 'No recommendations available')
    elements.append(Paragraph("<b>AI-Generated Recommendations:</b>", h2_style))
    elements.append(Paragraph(str(recommendations), normal))
    elements.append(Spacer(1, 12))

    # Footer
    elements.append(Spacer(1, 16))
    elements.append(Paragraph("Generated by Risk Stratification System", styles['Italic']))

    # Build PDF
    try:
        doc.build(elements)
    except Exception as build_err:
        print(f"PDF build failed: {build_err}")
        raise

    buffer.seek(0)
    return buffer.getvalue()

# ---------------------------
# Flask endpoints
# ---------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    """Get patient data with filtering support"""
    limit = request.args.get('limit', default=100, type=int)
    risk_label = request.args.get('risk_label', default=None)
    gender = request.args.get('gender', default=None)
    min_age = request.args.get('min_age', default=None, type=int)
    max_age = request.args.get('max_age', default=None, type=int)
    search = request.args.get('search', default=None)
    
    # Load data from CSV
    df = load_csv_data()
    if df.empty:
        return jsonify({'error': 'No data available'}), 500
    
    # Apply filters
    if risk_label and risk_label != 'All':
        df = df[df['RISK_LABEL'] == risk_label]
    
    if gender and gender != 'All':
        gender_value = 1 if gender == 'Male' else 0
        df = df[df['GENDER'] == gender_value]
    
    if min_age is not None:
        df = df[df['AGE'] >= min_age]
    
    if max_age is not None:
        df = df[df['AGE'] <= max_age]
    
    if search:
        search_mask = (
            df['DESYNPUF_ID'].astype(str).str.contains(search, case=False, na=False) |
            df['TOP_3_FEATURES'].astype(str).str.contains(search, case=False, na=False) |
            df['AI_RECOMMENDATIONS'].astype(str).str.contains(search, case=False, na=False)
        )
        df = df[search_mask]
    
    # Sort by risk and limit
    df = df.sort_values('RISK_30D', ascending=False)
    df = df.head(limit)
    
    # Convert to JSON format
    def row_to_dict(row):
        gender_val = row.get('GENDER')
        if pd.isna(gender_val):
            gender = 'Unknown'
        else:
            gender = 'Male' if int(gender_val) == 1 else 'Female'
        
        return {
            'patient_id': str(row.get('DESYNPUF_ID')),
            'age': int(row.get('AGE')) if pd.notna(row.get('AGE')) else None,
            'gender': gender,
            'claims_cost': float(row.get('TOTAL_CLAIMS_COST')) if pd.notna(row.get('TOTAL_CLAIMS_COST')) else 0.0,
            'risk_30d': float(row.get('RISK_30D')) if pd.notna(row.get('RISK_30D')) else None,
            'risk_60d': float(row.get('RISK_60D')) if pd.notna(row.get('RISK_60D')) else None,
            'risk_90d': float(row.get('RISK_90D')) if pd.notna(row.get('RISK_90D')) else None,
            'risk_label': str(row.get('RISK_LABEL')) if pd.notna(row.get('RISK_LABEL')) else 'Unknown',
            'top_features': str(row.get('TOP_3_FEATURES')) if pd.notna(row.get('TOP_3_FEATURES')) else 'N/A',
            'ai_recommendations': str(row.get('AI_RECOMMENDATIONS')) if pd.notna(row.get('AI_RECOMMENDATIONS')) else 'N/A',
            'email': str(row.get('EMAIL')) if pd.notna(row.get('EMAIL')) else '',
            'index_date': str(row.get('INDEX_DATE')) if pd.notna(row.get('INDEX_DATE')) else 'N/A'
        }
    
    data = [row_to_dict(r) for _, r in df.iterrows()]
    return jsonify({'data': data})

@app.route('/api/summary')
def api_summary():
    """Get summary statistics"""
    df = load_csv_data()
    if df.empty:
        return jsonify({})
    
    summary = {
        'total_patients': len(df),
        'avg_risk_30d': float(df['RISK_30D'].mean()) if not df['RISK_30D'].isna().all() else 0,
        'avg_risk_60d': float(df['RISK_60D'].mean()) if not df['RISK_60D'].isna().all() else 0,
        'avg_risk_90d': float(df['RISK_90D'].mean()) if not df['RISK_90D'].isna().all() else 0,
        'very_high_risk': int((df['RISK_LABEL'] == 'Very High Risk').sum()),
        'high_risk': int((df['RISK_LABEL'] == 'High Risk').sum()),
        'moderate_risk': int((df['RISK_LABEL'] == 'Moderate Risk').sum()),
        'low_risk': int((df['RISK_LABEL'] == 'Low Risk').sum()),
        'very_low_risk': int((df['RISK_LABEL'] == 'Very Low Risk').sum())
    }
    
    return jsonify(summary)

@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    try:
        df = load_csv_data()
        if df.empty:
            return jsonify({'status': 'unhealthy', 'data': 'no_data'}), 500
        return jsonify({'status': 'healthy', 'data': 'csv_loaded', 'records': len(df)})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """Predict for a new patient and save to CSV"""
    try:
        data = request.json or {}
        
        # Generate new patient ID if not provided
        if not data.get('DESYNPUF_ID'):
            data['DESYNPUF_ID'] = f"NEW_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Set default values for missing fields (all 29 features)
        defaults = {
            # Demographics
            'GENDER': 1,  # 1=Male, 0=Female
            # Insurance
            'PARTA': 12,
            'PARTB': 12,
            'HMO': 0,
            'PARTD': 12,
            # Chronic conditions
            'RENAL_DISEASE': 0,
            'ALZHEIMER': 0,
            'HEARTFAILURE': 0,
            'CANCER': 0,
            'PULMONARY': 0,
            'OSTEOPOROSIS': 0,
            'RHEUMATOID': 0,
            'STROKE': 0,
            # Vitals
            'BMI': 25.0,
            'BP_S': 120.0,
            'GLUCOSE': 100.0,
            'HbA1c': 5.5,
            'CHOLESTEROL': 200.0,
            # Trends
            'BP_trend': 0.0,
            'HbA1c_trend': 0.0,
            # Costs
            'OUTPATIENT_COST': 0.0,
            'ED_COST': 0.0,
            'TOTAL_CLAIMS_COST': 0.0,
            # Utilization
            'IN_ADM': 0,
            'OUT_VISITS': 0,
            'ED_VISITS': 0,
            # Adherence
            'RX_ADH': 0.8,
            # Derived
            'COMOR_COUNT': 0,
            'COMOR_WEIGHTED_SCORE': 0,
            'CLAIMS_FLAG': 0,
            'TOP_3_FEATURES': 'AGE, BMI, GLUCOSE'
        }
        
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        # Calculate weighted disease score based on chronic conditions
        disease_weights = {
            'HEARTFAILURE': 3.0,    # Highest risk - heart failure
            'STROKE': 2.8,          # Very high risk - stroke
            'CANCER': 2.5,          # High risk - cancer
            'RENAL_DISEASE': 2.3,   # High risk - kidney disease
            'PULMONARY': 2.0,       # Moderate-high risk - lung disease
            'ALZHEIMER': 1.8,       # Moderate risk - dementia
            'RHEUMATOID': 1.5,      # Moderate risk - arthritis
            'OSTEOPOROSIS': 1.2     # Lower risk - bone disease
        }
        
        # Calculate weighted comorbidity score
        data['COMOR_WEIGHTED_SCORE'] = 0
        for disease, weight in disease_weights.items():
            data['COMOR_WEIGHTED_SCORE'] += data.get(disease, 0) * weight
        
        # Keep simple count for backward compatibility
        chronic_conditions = ['ALZHEIMER', 'HEARTFAILURE', 'CANCER', 'PULMONARY', 
                             'OSTEOPOROSIS', 'RHEUMATOID', 'STROKE', 'RENAL_DISEASE']
        data['COMOR_COUNT'] = sum(data.get(condition, 0) for condition in chronic_conditions)
        
        # Calculate CLAIMS_FLAG
        data['CLAIMS_FLAG'] = 1 if data.get('TOTAL_CLAIMS_COST', 0) > 0 else 0
        
        # Generate risk predictions using ML model
        if ml_model:
            try:
                # Use the ML model to predict
                predictions = predict_single_patient(data, ml_model)
                
                # Update data with ML predictions
                data.update(predictions)
                
                print(f"ML Model Prediction: 30D={predictions['RISK_30D']:.2f}, 60D={predictions['RISK_60D']:.2f}, 90D={predictions['RISK_90D']:.2f}, Label={predictions['RISK_LABEL']}")
                
            except Exception as e:
                print(f"ML model prediction failed: {e}, using fallback")
                # Fallback to simple prediction
                age = float(data.get('AGE', 50))
                bmi = float(data.get('BMI', 25))
                glucose = float(data.get('GLUCOSE', 100))
                
                risk_30d = min(95, max(5, (age - 30) * 0.5 + (bmi - 20) * 0.3 + (glucose - 80) * 0.1))
                risk_60d = risk_30d * 1.1
                risk_90d = risk_30d * 1.2
                
                if risk_30d >= 80:
                    risk_label = 'Very High Risk'
                elif risk_30d >= 60:
                    risk_label = 'High Risk'
                elif risk_30d >= 40:
                    risk_label = 'Moderate Risk'
                elif risk_30d >= 20:
                    risk_label = 'Low Risk'
                else:
                    risk_label = 'Very Low Risk'
                
                data.update({
                    'RISK_30D': round(risk_30d, 2),
                    'RISK_60D': round(risk_60d, 2),
                    'RISK_90D': round(risk_90d, 2),
                    'RISK_LABEL': risk_label,
                    'TOP_3_FEATURES': 'AGE, BMI, GLUCOSE'
                })
                
                ai_recommendations = get_ai_recommendations(data, data.get('TOP_3_FEATURES', 'AGE, BMI, GLUCOSE'))
                data['AI_RECOMMENDATIONS'] = ai_recommendations
        else:
            # Fallback to simple prediction if no ML model
            age = float(data.get('AGE', 50))
            bmi = float(data.get('BMI', 25))
            glucose = float(data.get('GLUCOSE', 100))
            
            risk_30d = min(95, max(5, (age - 30) * 0.5 + (bmi - 20) * 0.3 + (glucose - 80) * 0.1))
            risk_60d = risk_30d * 1.1
            risk_90d = risk_30d * 1.2
            
            if risk_30d >= 80:
                risk_label = 'Very High Risk'
            elif risk_30d >= 60:
                risk_label = 'High Risk'
            elif risk_30d >= 40:
                risk_label = 'Moderate Risk'
            elif risk_30d >= 20:
                risk_label = 'Low Risk'
            else:
                risk_label = 'Very Low Risk'
            
            data.update({
                'RISK_30D': round(risk_30d, 2),
                'RISK_60D': round(risk_60d, 2),
                'RISK_90D': round(risk_90d, 2),
                'RISK_LABEL': risk_label,
                'TOP_3_FEATURES': 'AGE, BMI, GLUCOSE'
            })
            
            ai_recommendations = get_ai_recommendations(data, data.get('TOP_3_FEATURES', 'AGE, BMI, GLUCOSE'))
            data['AI_RECOMMENDATIONS'] = ai_recommendations
        
        # Load existing CSV and add new patient
        df = load_csv_data()
        new_row = pd.DataFrame([data])
        df = pd.concat([df, new_row], ignore_index=True)
        
        # Save updated CSV
        if save_csv_data(df):
            # Send email if email provided
            email_addr = data.get('EMAIL')
            if email_addr:
                try:
                    pdf_bytes = create_patient_pdf_bytes(data)
                    attachment_name = f"patient_report_{data['DESYNPUF_ID']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                    
                    message_body = (
                        f"Hello,\n\nPlease find attached the risk prediction report for patient {data['DESYNPUF_ID']}.\n\n"
                        f"Summary:\n30-day: {data.get('RISK_30D', 0):.2f}%\n60-day: {data.get('RISK_60D', 0):.2f}%\n90-day: {data.get('RISK_90D', 0):.2f}%\n"
                        f"Label: {data.get('RISK_LABEL', 'Unknown')}\n\nRegards,\nRisk Stratification System"
                    )
                    send_email(email_addr, "Patient Risk Prediction Report", message_body, 
                             attachment_bytes=pdf_bytes, attachment_filename=attachment_name)
                except Exception as mail_err:
                    print(f"Failed to send email: {mail_err}")
            
            return jsonify({
                'success': True, 
                'predictions': {
                    'RISK_30D': data.get('RISK_30D'),
                    'RISK_60D': data.get('RISK_60D'),
                    'RISK_90D': data.get('RISK_90D'),
                    'RISK_LABEL': data.get('RISK_LABEL'),
                    'TOP_3_FEATURES': data.get('TOP_3_FEATURES'),
                    'AI_RECOMMENDATIONS': data.get('AI_RECOMMENDATIONS')
                },
                'message': f'New patient {data["DESYNPUF_ID"]} added successfully',
                'model_used': 'ML Model' if ml_model else 'Fallback Formula'
            })
        else:
            return jsonify({'error': 'Failed to save patient data'}), 500
            
    except Exception as e:
        print(f"Prediction error: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# ---------------------------
# App run
# ---------------------------
if __name__ == '__main__':
    # Ensure templates directory
    os.makedirs('templates', exist_ok=True)
    
    print("🚀 Starting Risk Stratification Web App (CSV-based)...")
    print("📊 Dashboard: http://localhost:5000")
    print("📁 Data Source: trainingk.csv")
    print(f"🤖 ML Model: {'Loaded' if ml_model else 'Not Available (using fallback)'}")
    print("API endpoints:")
    print(" - /api/data")
    print(" - /api/summary")
    print(" - /api/health")
    print(" - /api/predict (POST)")

    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=True)
