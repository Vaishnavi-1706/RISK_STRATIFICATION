#!/usr/bin/env python3
"""
Working New Patient Risk Assessment Dashboard
Integrated with AI Model for Risk Predictions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import warnings
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import os
import numpy as np # Added for SHAP
import shap # Added for SHAP analysis
from shap_utils import load_shap_explainer, get_patient_shap_explanation, get_global_shap_importance # Added for SHAP analysis

warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="New Patient Risk Assessment",
    page_icon="🏥",
    layout="wide"
)

# AI Model for Risk Prediction
class AIRiskModel:
    def predict_risk(self, patient_data):
        risk_score_30d = 0
        risk_score_60d = 0
        risk_score_90d = 0
        risk_factors = []
        
        # Age factor
        age = patient_data.get('AGE', 0)
        if age >= 75:
            risk_factors.append('AGE')
            risk_score_30d += 25
            risk_score_60d += 30
            risk_score_90d += 35
        elif age >= 65:
            risk_factors.append('AGE')
            risk_score_30d += 15
            risk_score_60d += 20
            risk_score_90d += 25
        
        # BMI factor
        bmi = patient_data.get('BMI', 0)
        if bmi >= 30:
            risk_factors.append('BMI')
            risk_score_30d += 20
            risk_score_60d += 25
            risk_score_90d += 30
        elif bmi < 18.5:
            risk_factors.append('BMI')
            risk_score_30d += 15
            risk_score_60d += 20
            risk_score_90d += 25
        
        # Blood pressure factor
        bp_s = patient_data.get('BP_S', 0)
        if bp_s >= 140:
            risk_factors.append('BP_S')
            risk_score_30d += 20
            risk_score_60d += 25
            risk_score_90d += 30
        
        # Glucose factor
        glucose = patient_data.get('GLUCOSE', 0)
        if glucose >= 126:
            risk_factors.append('GLUCOSE')
            risk_score_30d += 25
            risk_score_60d += 30
            risk_score_90d += 35
        
        # Medical conditions
        conditions = patient_data.get('MEDICAL_CONDITIONS', [])
        for condition in conditions:
            risk_factors.append(condition)
            risk_score_30d += 10
            risk_score_60d += 15
            risk_score_90d += 20
        
        # Cap scores at 100
        risk_score_30d = min(risk_score_30d, 100)
        risk_score_60d = min(risk_score_60d, 100)
        risk_score_90d = min(risk_score_90d, 100)
        
        # Determine risk label
        if risk_score_30d >= 80:
            risk_label = "Very High Risk"
        elif risk_score_30d >= 60:
            risk_label = "High Risk"
        elif risk_score_30d >= 40:
            risk_label = "Moderate Risk"
        elif risk_score_30d >= 20:
            risk_label = "Low Risk"
        else:
            risk_label = "Very Low Risk"
        
        # Generate recommendations
        recommendations = self.generate_recommendations(patient_data, risk_factors, risk_label)
        
        return {
            'RISK_30D': risk_score_30d,
            'RISK_60D': risk_score_60d,
            'RISK_90D': risk_score_90d,
            'RISK_LABEL': risk_label,
            'TOP_3_FEATURES': ', '.join(risk_factors[:3]) if risk_factors else 'AGE, BMI, GLUCOSE',
            'AI_RECOMMENDATIONS': recommendations
        }
    
    def generate_recommendations(self, patient_data, risk_factors, risk_label):
        recommendations = []
        
        age = patient_data.get('AGE', 0)
        if age >= 75:
            recommendations.append("Schedule comprehensive geriatric assessment")
        elif age >= 65:
            recommendations.append("Annual wellness visit recommended")
        
        conditions = patient_data.get('MEDICAL_CONDITIONS', [])
        if 'Diabetes' in conditions or 'GLUCOSE' in risk_factors:
            recommendations.append("Endocrinology consultation for diabetes management")
        if 'Heart Disease' in conditions or 'BP_S' in risk_factors:
            recommendations.append("Cardiology consultation for cardiovascular health")
        if 'Obesity' in conditions or 'BMI' in risk_factors:
            recommendations.append("Nutrition consultation for weight management")
        
        if risk_label in ["Very High Risk", "High Risk"]:
            recommendations.append("Immediate care coordination recommended")
        elif risk_label == "Moderate Risk":
            recommendations.append("Regular monitoring recommended")
        else:
            recommendations.append("Continue preventive care routine")
        
        return " | ".join(recommendations[:3])

@st.cache_data
def load_data():
    """Load patient data with SHAP analysis"""
    try:
        df = pd.read_csv('index.csv')
        
        # Load SHAP explainer if available
        shap_explainer = load_shap_explainer()
        
        # Add SHAP explanations if not present
        if 'SHAP_EXPLANATION' not in df.columns:
            df['SHAP_EXPLANATION'] = "SHAP analysis available"
        
        return df, shap_explainer
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(), None

def get_patient_count():
    """Get the current total patient count for display"""
    try:
        df = pd.read_csv('index.csv')
        return len(df)
    except Exception as e:
        return 0

def get_ai_recommendations_status():
    """Get the status of AI recommendations for all patients"""
    try:
        df = pd.read_csv('index.csv')
        total_patients = len(df)
        
        # Count patients with AI recommendations
        patients_with_ai = 0
        patients_without_ai = 0
        
        for _, patient in df.iterrows():
            recommendations = patient.get('AI_RECOMMENDATIONS', '')
            if pd.isna(recommendations) or recommendations == '' or recommendations == 'None':
                patients_without_ai += 1
            else:
                patients_with_ai += 1
        
        return {
            'total_patients': total_patients,
            'patients_with_ai': patients_with_ai,
            'patients_without_ai': patients_without_ai,
            'ai_coverage_percentage': (patients_with_ai / total_patients * 100) if total_patients > 0 else 0
        }
    except Exception as e:
        return {
            'total_patients': 0,
            'patients_with_ai': 0,
            'patients_without_ai': 0,
            'ai_coverage_percentage': 0
        }

def generate_patient_pdf(patient_data, predictions, patient_id):
    """Generate PDF report for patient"""
    try:
        # Create PDF buffer
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        # Title
        title = Paragraph(f"Patient Risk Assessment Report", title_style)
        elements.append(title)
        
        # Patient Information
        patient_info = f"""
        <b>Patient Information:</b><br/>
        Patient ID: {patient_id}<br/>
        Age: {patient_data['AGE']}<br/>
        Gender: {patient_data['GENDER']}<br/>
        Email: {patient_data.get('EMAIL', 'Not provided')}<br/>
        Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        patient_para = Paragraph(patient_info, styles['Normal'])
        elements.append(patient_para)
        elements.append(Spacer(1, 20))
        
        # Health Metrics
        health_info = f"""
        <b>Health Metrics:</b><br/>
        BMI: {patient_data['BMI']}<br/>
        Blood Pressure (Systolic): {patient_data['BP_S']}<br/>
        Glucose Level: {patient_data['GLUCOSE']}<br/>
        HbA1c: {patient_data['HbA1c']}<br/>
        Cholesterol: {patient_data['CHOLESTEROL']}<br/>
        <b>Insurance Information:</b><br/>
        Part A: {patient_data.get('PARTA', 0)}<br/>
        Part B: {patient_data.get('PARTB', 0)}<br/>
        HMO: {patient_data.get('HMO', 0)}<br/>
        Part D: {patient_data.get('PARTD', 0)}<br/>
        Date: {patient_data.get('DATE', 'N/A')}
        """
        health_para = Paragraph(health_info, styles['Normal'])
        elements.append(health_para)
        elements.append(Spacer(1, 20))
        
        # Medical Conditions
        conditions = patient_data.get('MEDICAL_CONDITIONS', [])
        conditions_text = ', '.join(conditions) if conditions else 'None reported'
        conditions_info = f"""
        <b>Medical Conditions:</b><br/>
        {conditions_text}
        """
        conditions_para = Paragraph(conditions_info, styles['Normal'])
        elements.append(conditions_para)
        elements.append(Spacer(1, 20))
        
        # Risk Assessment
        risk_info = f"""
        <b>Risk Assessment:</b><br/>
        30-Day Risk: {predictions['RISK_30D']}%<br/>
        60-Day Risk: {predictions['RISK_60D']}%<br/>
        90-Day Risk: {predictions['RISK_90D']}%<br/>
        Risk Level: {predictions['RISK_LABEL']}<br/>
        Top Risk Factors: {predictions['TOP_3_FEATURES']}
        """
        risk_para = Paragraph(risk_info, styles['Normal'])
        elements.append(risk_para)
        elements.append(Spacer(1, 20))
        
        # AI Recommendations
        recommendations = predictions['AI_RECOMMENDATIONS']
        rec_info = f"""
        <b>AI-Generated Recommendations:</b><br/>
        {recommendations}
        """
        rec_para = Paragraph(rec_info, styles['Normal'])
        elements.append(rec_para)
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        return None

def send_patient_email(patient_data, predictions, patient_id, pdf_buffer):
    """Send email with PDF attachment to patient using Node.js service"""
    try:
        email = patient_data.get('EMAIL', '')
        if not email:
            print("❌ No email address provided")
            return False, "No email address provided"
        
        # Try to use Node.js email service
        try:
            import email_config_streamlit
            from email_config_streamlit import send_patient_email_wrapper
            
            # Save PDF to file first
            pdf_filename = f'patient_risk_assessment_{patient_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            pdf_path = f'./pdfs/{pdf_filename}'
            
            # Ensure pdfs directory exists
            os.makedirs('./pdfs', exist_ok=True)
            
            # Save PDF buffer to file
            with open(pdf_path, 'wb') as f:
                f.write(pdf_buffer.getvalue())
            
            # Send email using Node.js service
            result = send_patient_email_wrapper(patient_data, patient_id, pdf_path)
            
            if result.get('success', False):
                print(f"✅ Email sent successfully to {email} via Node.js service")
                return True, "Email sent successfully via Node.js service"
            else:
                error_msg = result.get('error', 'Unknown error')
                print(f"❌ Node.js email service error: {error_msg}")
                return False, error_msg
                
        except ImportError:
            # Fallback to direct SMTP if Node.js service not available
            print("⚠️ Node.js email service not available, falling back to direct SMTP")
            
            # Try to load email configuration
            try:
                import email_config_streamlit
                sender_email = email_config_streamlit.SENDER_EMAIL
                sender_password = email_config_streamlit.SENDER_PASSWORD
                smtp_server = email_config_streamlit.SMTP_SERVER
                smtp_port = email_config_streamlit.SMTP_PORT
            except ImportError:
                # Fallback to environment variables
                sender_email = os.getenv('SENDER_EMAIL', 'your-email@gmail.com')
                sender_password = os.getenv('SENDER_PASSWORD', 'your-app-password')
                smtp_server = "smtp.gmail.com"
                smtp_port = 587
            
            # Check if email is configured
            if sender_email == "your-email@gmail.com" or sender_password == "your-app-password":
                return False, "Email not configured. Please update email_config_streamlit.py or set environment variables."
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = f"Your Health Risk Assessment Report - Patient ID: {patient_id}"
            
            # Email body
            body = f"""
Dear Patient,

We are sending you your personalized Health Risk Assessment Report based on your recent medical evaluation.

Your Risk Assessment Summary:
- 30-Day Risk: {predictions['RISK_30D']}%
- 60-Day Risk: {predictions['RISK_60D']}%
- 90-Day Risk: {predictions['RISK_90D']}%
- Risk Level: {predictions['RISK_LABEL']}

Top Risk Factors: {predictions['TOP_3_FEATURES']}

AI-Generated Recommendations:
{predictions['AI_RECOMMENDATIONS']}

Your detailed report is attached to this email as a PDF document. Please review it carefully and discuss the findings with your healthcare provider.

Important Next Steps:
1. Schedule an appointment with your primary care physician
2. Review your current medications with your pharmacist
3. Implement the lifestyle changes recommended in the report
4. Monitor your symptoms and report any changes

If you have any questions or concerns, please contact your healthcare provider immediately.

Best regards,
Your Healthcare Team

---
This is an automated message. Please do not reply to this email.
For medical emergencies, call 911 or your local emergency number.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach PDF
            pdf_attachment = MIMEBase('application', 'pdf')
            pdf_attachment.set_payload(pdf_buffer.getvalue())
            encoders.encode_base64(pdf_attachment)
            pdf_attachment.add_header(
                'Content-Disposition',
                'attachment',
                filename=f'patient_risk_assessment_{patient_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            )
            msg.attach(pdf_attachment)
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, email, text)
            server.quit()
            
            print(f"✅ Email sent successfully to {email} via direct SMTP")
            return True, "Email sent successfully via direct SMTP"
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False, str(e)

def generate_ai_recommendations_for_all_patients():
    """Generate AI recommendations for all patients in the dataset"""
    try:
        # Load the CSV file
        df = pd.read_csv('index.csv')
        
        # Initialize AI model
        ai_model = AIRiskModel()
        
        # Track updates
        updated_count = 0
        
        # Process each patient
        for index, patient in df.iterrows():
            # Check if patient already has AI recommendations
            current_recommendations = patient.get('AI_RECOMMENDATIONS', '')
            if pd.isna(current_recommendations) or current_recommendations == '' or current_recommendations == 'None':
                # Prepare patient data for AI analysis
                patient_data = {
                    'AGE': patient['AGE'],
                    'GENDER': 'Male' if patient['GENDER'] == 1 else 'Female',
                    'BMI': patient['BMI'],
                    'BP_S': patient['BP_S'],
                    'GLUCOSE': patient['GLUCOSE'],
                    'HbA1c': patient['HbA1c'],
                    'CHOLESTEROL': patient['CHOLESTEROL'],
                    'PARTA': patient.get('PARTA', 12),
                    'PARTB': patient.get('PARTB', 12),
                    'HMO': patient.get('HMO', 0),
                    'PARTD': patient.get('PARTD', 0),
                    'MEDICAL_CONDITIONS': []
                }
                
                # Add medical conditions based on existing columns
                conditions = []
                if patient.get('ALZHEIMER', 0) == 1: conditions.append('Alzheimer')
                if patient.get('HEARTFAILURE', 0) == 1: conditions.append('Heart Disease')
                if patient.get('CANCER', 0) == 1: conditions.append('Cancer')
                if patient.get('PULMONARY', 0) == 1: conditions.append('Lung Disease')
                if patient.get('OSTEOPOROSIS', 0) == 1: conditions.append('Osteoporosis')
                if patient.get('RHEUMATOID', 0) == 1: conditions.append('Arthritis')
                if patient.get('STROKE', 0) == 1: conditions.append('Stroke')
                if patient.get('RENAL_DISEASE', 0) == 1: conditions.append('Kidney Disease')
                
                patient_data['MEDICAL_CONDITIONS'] = conditions
                
                # Generate AI recommendations
                predictions = ai_model.predict_risk(patient_data)
                
                # Update the dataframe
                df.at[index, 'AI_RECOMMENDATIONS'] = predictions['AI_RECOMMENDATIONS']
                df.at[index, 'RISK_30D'] = predictions['RISK_30D']
                df.at[index, 'RISK_60D'] = predictions['RISK_60D']
                df.at[index, 'RISK_90D'] = predictions['RISK_90D']
                df.at[index, 'RISK_LABEL'] = predictions['RISK_LABEL']
                df.at[index, 'TOP_3_FEATURES'] = predictions['TOP_3_FEATURES']
                
                updated_count += 1
                print(f"✅ Generated AI recommendations for patient {patient['DESYNPUF_ID']}")
        
        # Save updated dataframe
        df.to_csv('index.csv', index=False)
        
        print(f"🎉 Successfully updated AI recommendations for {updated_count} patients")
        return True, updated_count
        
    except Exception as e:
        print(f"❌ Error generating AI recommendations: {e}")
        return False, str(e)

def save_new_patient(patient_data, predictions):
    try:
        # Load the original CSV file directly (not through load_data which modifies it)
        df = pd.read_csv('index.csv')
        
        # Create new patient data matching the existing CSV structure
        new_patient = {
            'DESYNPUF_ID': f"NEW_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'AGE': patient_data['AGE'],
            'GENDER': 1 if patient_data['GENDER'] == 'Male' else 0,
            'RENAL_DISEASE': 1 if 'Kidney Disease' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'PARTA': patient_data.get('PARTA', 12),
            'PARTB': patient_data.get('PARTB', 12),
            'HMO': patient_data.get('HMO', 0),
            'PARTD': patient_data.get('PARTD', 0),
            'ALZHEIMER': 1 if 'Alzheimer' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'HEARTFAILURE': 1 if 'Heart Disease' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'CANCER': 1 if 'Cancer' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'PULMONARY': 1 if 'Lung Disease' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'OSTEOPOROSIS': 1 if 'Osteoporosis' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'RHEUMATOID': 1 if 'Arthritis' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'STROKE': 1 if 'Stroke' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'TOTAL_CLAIMS_COST': 0,  # Default value for new patients
            'IN_ADM': 0, 'OUT_VISITS': 1, 'ED_VISITS': 0, 'RX_ADH': 0.8,
            'BMI': patient_data['BMI'],
            'BP_S': patient_data['BP_S'],
            'GLUCOSE': patient_data['GLUCOSE'],
            'HbA1c': patient_data['HbA1c'],
            'CHOLESTEROL': patient_data['CHOLESTEROL'],
            'RISK_30D': predictions['RISK_30D'],
            'RISK_60D': predictions['RISK_60D'],
            'RISK_90D': predictions['RISK_90D'],
            'RISK_LABEL': predictions['RISK_LABEL'],
            'TOP_3_FEATURES': predictions['TOP_3_FEATURES'],
            'AI_RECOMMENDATIONS': predictions['AI_RECOMMENDATIONS']
        }
        
        # Add EMAIL column if it doesn't exist
        if 'EMAIL' not in df.columns:
            df['EMAIL'] = ''
        
        # Add EMAIL to new patient data
        new_patient['EMAIL'] = patient_data.get('EMAIL', '')
        
        # Append new patient to dataframe
        df = pd.concat([df, pd.DataFrame([new_patient])], ignore_index=True)
        
        # Save back to CSV
        df.to_csv('index.csv', index=False)
        
        print(f"✅ Successfully saved patient {new_patient['DESYNPUF_ID']} to CSV")
        print(f"📊 Total patients in CSV: {len(df)}")
        
        # Generate PDF for new patient
        print("📄 Generating PDF report for new patient...")
        try:
            from pdf_generator import pdf_generator
            pdf_path = pdf_generator.generate_patient_pdf(patient_data, predictions, new_patient['DESYNPUF_ID'])
            if pdf_path:
                print(f"✅ PDF generated successfully: {pdf_path}")
            else:
                print("⚠️ PDF generation failed")
        except Exception as e:
            print(f"⚠️ PDF generation error: {e}")
        
        # Generate AI recommendations for all patients (including existing ones)
        print("🤖 Generating AI recommendations for all patients...")
        ai_success, ai_count = generate_ai_recommendations_for_all_patients()
        
        if ai_success:
            print(f"✅ AI recommendations updated for {ai_count} patients")
        else:
            print(f"⚠️ AI recommendations update failed: {ai_count}")
        
        return True, new_patient['DESYNPUF_ID']
    except Exception as e:
        print(f"❌ Error saving patient: {e}")
        return False, str(e)

def main():
    st.markdown('<h1 style="text-align: center; color: #1f77b4;">🏥 New Patient Risk Assessment Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data with SHAP
    df, shap_explainer = load_data()
    
    if df.empty:
        st.error("❌ Failed to load patient data. Please check if 'index.csv' exists.")
        return
    
    # Get current patient count and AI recommendations status
    current_patient_count = get_patient_count()
    ai_status = get_ai_recommendations_status()
    
    # Display current patient count and AI status at the top
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div style="text-align: center; padding: 10px; background-color: #f0f2f6; border-radius: 10px; margin: 10px 0;">
            <h3 style="margin: 0; color: #1f77b4;">📊 Current Total Patients: <span style="color: #ff6b6b; font-weight: bold;">{current_patient_count}</span></h3>
            <p style="margin: 5px 0 0 0; color: #666;">
                🤖 AI Recommendations: <span style="color: #28a745; font-weight: bold;">{ai_status['patients_with_ai']}</span> / <span style="color: #ff6b6b; font-weight: bold;">{ai_status['total_patients']}</span> 
                (<span style="color: #17a2b8; font-weight: bold;">{ai_status['ai_coverage_percentage']:.1f}%</span> coverage)
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["🆕 New Patient", "📊 Dashboard", "📋 Patient Management"])
    
    with tab1:
        st.markdown("## 🆕 New Patient Risk Assessment Form")
        
        # Initialize session state for storing patient data and predictions
        if 'patient_data' not in st.session_state:
            st.session_state.patient_data = None
        if 'predictions' not in st.session_state:
            st.session_state.predictions = None
        if 'assessment_generated' not in st.session_state:
            st.session_state.assessment_generated = False
        
        with st.form("new_patient_form"):
            st.markdown("### Patient Demographics")
            col1, col2 = st.columns(2)
            
            with col1:
                age = st.number_input("Age", min_value=18, max_value=120, value=50)
                gender = st.selectbox("Gender", ["Male", "Female"])
                bmi = st.number_input("BMI", min_value=15.0, max_value=50.0, value=25.0, step=0.1)
                bp_s = st.number_input("Blood Pressure (Systolic)", min_value=80, max_value=200, value=120)
                date = st.date_input("Date", value=datetime.now().date())
            
            with col2:
                glucose = st.number_input("Glucose Level", min_value=70, max_value=300, value=100)
                hba1c = st.number_input("HbA1c", min_value=4.0, max_value=15.0, value=5.5, step=0.1)
                cholesterol = st.number_input("Cholesterol", min_value=100, max_value=400, value=200)
                email = st.text_input("Email Address (Required)", placeholder="patient@example.com", help="Email address is required for sending PDF reports")
            
            st.markdown("### Insurance Information")
            col1, col2 = st.columns(2)
            
            with col1:
                parta = st.number_input("Part A", min_value=0, max_value=100, value=12)
                partb = st.number_input("Part B", min_value=0, max_value=100, value=12)
            
            with col2:
                hmo = st.number_input("HMO", min_value=0, max_value=100, value=0)
                partd = st.number_input("Part D", min_value=0, max_value=100, value=0)
            
            st.markdown("### Medical Conditions")
            medical_conditions = st.multiselect(
                "Select Medical Conditions",
                ["Diabetes", "Heart Disease", "Cancer", "Lung Disease", "Alzheimer", 
                 "Osteoporosis", "Arthritis", "Stroke", "Kidney Disease", "Obesity"]
            )
            
            submitted = st.form_submit_button("🚀 Generate Risk Assessment")
            
            if submitted:
                # Validate email is provided
                if not email or email.strip() == "":
                    st.error("❌ Email address is required. Please provide a valid email address.")
                    return
                
                # Validate email format
                if "@" not in email or "." not in email:
                    st.error("❌ Please provide a valid email address.")
                    return
                
                patient_data = {
                    'AGE': age,
                    'GENDER': gender,
                    'BMI': bmi,
                    'BP_S': bp_s,
                    'GLUCOSE': glucose,
                    'HbA1c': hba1c,
                    'CHOLESTEROL': cholesterol,
                    'PARTA': parta,
                    'PARTB': partb,
                    'HMO': hmo,
                    'PARTD': partd,
                    'DATE': date.strftime('%Y-%m-%d'),
                    'MEDICAL_CONDITIONS': medical_conditions,
                    'EMAIL': email
                }
                
                ai_model = AIRiskModel()
                predictions = ai_model.predict_risk(patient_data)
                
                # Store in session state
                st.session_state.patient_data = patient_data
                st.session_state.predictions = predictions
                st.session_state.assessment_generated = True
                
                st.rerun()
        
        # Display results outside the form (only if assessment was generated)
        if st.session_state.assessment_generated and st.session_state.patient_data and st.session_state.predictions:
            st.markdown("## 📊 Risk Assessment Results")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("30-Day Risk", f"{st.session_state.predictions['RISK_30D']}%")
            with col2:
                st.metric("60-Day Risk", f"{st.session_state.predictions['RISK_60D']}%")
            with col3:
                st.metric("90-Day Risk", f"{st.session_state.predictions['RISK_90D']}%")
            with col4:
                st.metric("Risk Level", st.session_state.predictions['RISK_LABEL'])
            
            st.markdown("### 🤖 AI Recommendations")
            recommendations = st.session_state.predictions['AI_RECOMMENDATIONS'].split(' | ')
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"**{i}.** {rec}")
            
            # Add SHAP Analysis for new patient
            if shap_explainer is not None:
                st.markdown("### 🔍 SHAP Feature Analysis")
                st.info("SHAP (SHapley Additive exPlanations) shows how each feature contributes to the risk prediction.")
                
                try:
                    # Prepare patient data for SHAP analysis
                    feature_columns = [col for col in df.columns if col not in ['DESYNPUF_ID', 'RISK_30D', 'RISK_60D', 'RISK_90D', 'RISK_LABEL', 'TOP_3_FEATURES', 'AI_RECOMMENDATIONS', 'EMAIL', 'SHAP_EXPLANATION']]
                    
                    # Create a patient row for SHAP analysis
                    patient_row = pd.Series(st.session_state.patient_data)
                    
                    # Generate SHAP explanation
                    shap_explanation = get_patient_shap_explanation(patient_row, feature_columns, None, shap_explainer)
                    st.write(f"**SHAP Analysis:** {shap_explanation}")
                    
                    # Show global SHAP importance
                    shap_importance = get_global_shap_importance()
                    if shap_importance is not None:
                        st.markdown("**Global Feature Importance (SHAP):**")
                        top_shap_features = shap_importance.head(5)
                        for i, row in top_shap_features.iterrows():
                            st.write(f"• **{row['feature']}**: {row['shap_importance']:.2f}")
                            
                except Exception as e:
                    st.error(f"Error generating SHAP analysis: {str(e)}")
            
            st.markdown("### 💾 Save to Dataset")
            st.markdown("**⚠️ Review the assessment above. Click the button below only if you want to save this patient to the dataset.**")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("✅ Save New Patient to Dataset", type="primary"):
                    # Save patient to CSV
                    success, result = save_new_patient(st.session_state.patient_data, st.session_state.predictions)
                    if success:
                        st.success(f"✅ Patient saved successfully! Patient ID: {result}")
                        
                        # Generate PDF and send email
                        email_sent = False
                        email_message = ""
                        
                        if st.session_state.patient_data.get('EMAIL'):
                            with st.spinner("📧 Generating PDF and sending email..."):
                                # Generate PDF
                                pdf_buffer = generate_patient_pdf(
                                    st.session_state.patient_data, 
                                    st.session_state.predictions, 
                                    result
                                )
                                
                                if pdf_buffer:
                                    # Send email with PDF attachment
                                    email_success, email_message = send_patient_email(
                                        st.session_state.patient_data,
                                        st.session_state.predictions,
                                        result,
                                        pdf_buffer
                                    )
                                    
                                    if email_success:
                                        email_sent = True
                                        st.success(f"📧 PDF report sent to {st.session_state.patient_data.get('EMAIL')}")
                                    else:
                                        st.warning(f"⚠️ Email not sent: {email_message}")
                                else:
                                    st.warning("⚠️ PDF generation failed")
                        else:
                            st.info("ℹ️ No email address provided - PDF report not sent")
                        
                        st.balloons()
                        st.cache_data.clear()
                        
                        # Show updated patient count and AI status
                        new_count = get_patient_count()
                        new_ai_status = get_ai_recommendations_status()
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px; background-color: #d4edda; border-radius: 10px; margin: 10px 0;">
                            <h4 style="margin: 0; color: #155724;">🎉 Total Patients Updated: <span style="color: #28a745; font-weight: bold;">{new_count}</span></h4>
                            <p style="margin: 5px 0 0 0; color: #155724;">
                                🤖 AI Recommendations: <span style="color: #28a745; font-weight: bold;">{new_ai_status['patients_with_ai']}</span> / <span style="color: #28a745; font-weight: bold;">{new_ai_status['total_patients']}</span> 
                                (<span style="color: #17a2b8; font-weight: bold;">{new_ai_status['ai_coverage_percentage']:.1f}%</span> coverage)
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show email status
                        if email_sent:
                            st.markdown(f"""
                            <div style="text-align: center; padding: 10px; background-color: #d1ecf1; border-radius: 10px; margin: 10px 0;">
                                <h4 style="margin: 0; color: #0c5460;">📧 PDF Report Sent: <span style="color: #17a2b8; font-weight: bold;">{st.session_state.patient_data.get('EMAIL')}</span></h4>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Clear session state after successful save
                        st.session_state.patient_data = None
                        st.session_state.predictions = None
                        st.session_state.assessment_generated = False
                        
                        # Auto-refresh the page after 3 seconds
                        st.markdown("🔄 **Auto-refreshing dashboard in 3 seconds...**")
                        import time
                        time.sleep(3)
                        st.rerun()
                    else:
                        st.error(f"❌ Error saving patient: {result}")
            
            # Add a button to clear/reset the assessment
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Generate New Assessment"):
                    st.session_state.patient_data = None
                    st.session_state.predictions = None
                    st.session_state.assessment_generated = False
                    st.rerun()
    
    with tab2:
        # Use the already loaded data from the main function
        # df is already available from the main function scope
        
        if df.empty:
            st.error("No data available.")
            return
        
        st.markdown("## 📊 Patient Dashboard")
        
        # Email Configuration Section
        with st.expander("⚙️ Email Configuration", expanded=False):
            st.markdown("### Email Service Setup")
            
            # Check current email status
            from email_config_streamlit import get_email_config_status, test_email_connection
            config_status = get_email_config_status()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Current Configuration:**")
                st.write(f"SMTP Server: {config_status['smtp_server']}")
                st.write(f"SMTP Port: {config_status['smtp_port']}")
                st.write(f"Sender Email: {config_status['sender_email']}")
                
                if config_status.get('error'):
                    st.error(config_status['error'])
                else:
                    st.success("✅ Email configuration found")
            
            with col2:
                st.markdown("**Test Connection:**")
                if st.button("🔍 Test Email Connection"):
                    with st.spinner("Testing email connection..."):
                        test_result = test_email_connection()
                        
                        if test_result.get('success', False):
                            st.success("✅ Email connection successful!")
                            st.write(f"Server: {test_result.get('server')}")
                            st.write(f"Port: {test_result.get('port')}")
                        else:
                            st.error(f"❌ Connection failed: {test_result.get('error')}")
                            if test_result.get('details'):
                                st.info(f"**Details:** {test_result.get('details')}")
            
            st.markdown("---")
            st.markdown("**Setup Instructions:**")
            st.markdown("""
            1. **For Gmail:**
               - Enable 2-Factor Authentication
               - Generate an App Password
               - Set environment variables:
                 ```bash
                 SENDER_EMAIL=your-email@gmail.com
                 SENDER_PASSWORD=your-16-character-app-password
                 ```
            
            2. **For other providers:**
               - Use your SMTP settings
               - Set environment variables accordingly
            """)
        
        # Refresh button and filters
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
        with col1:
            if st.button("🔄 Refresh Dashboard"):
                st.cache_data.clear()
                st.rerun()
        with col2:
            if st.button("🤖 Generate AI Recommendations for All Patients"):
                with st.spinner("🤖 Generating AI recommendations for all patients..."):
                    ai_success, ai_count = generate_ai_recommendations_for_all_patients()
                    if ai_success:
                        st.success(f"✅ AI recommendations generated for {ai_count} patients!")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error(f"❌ Failed to generate AI recommendations: {ai_count}")
        with col3:
            if st.button("📄 Generate PDFs for All Patients"):
                with st.spinner("📄 Generating PDF reports for all patients..."):
                    try:
                        from pdf_generator import pdf_generator
                        generated_count = pdf_generator.generate_pdfs_for_all_patients()
                        if generated_count > 0:
                            st.success(f"✅ Generated {generated_count} PDF reports!")
                        else:
                            st.warning("⚠️ No new PDFs generated (may already exist)")
                    except Exception as e:
                        st.error(f"❌ PDF generation failed: {e}")
        with col4:
            risk_filter = st.selectbox("Risk Level", ['All'] + list(df['RISK_LABEL'].unique()))
        with col5:
            gender_filter = st.selectbox("Gender", ['All'] + list(df['GENDER'].unique()))
        with col6:
            search = st.text_input("Search Patient ID")
        
        # Add SHAP Analysis Section
        if shap_explainer is not None:
            with st.expander("🔍 SHAP Analysis", expanded=False):
                st.markdown("### SHAP (SHapley Additive exPlanations) Analysis")
                st.info("SHAP provides detailed explanations of how each feature contributes to risk predictions.")
                
                # Show global SHAP importance
                shap_importance = get_global_shap_importance()
                if shap_importance is not None:
                    st.markdown("**Global Feature Importance (SHAP):**")
                    
                    # Create a bar chart of SHAP importance
                    fig = px.bar(shap_importance.head(10), x='shap_importance', y='feature', 
                               title="Top 10 Features by SHAP Importance",
                               color='shap_importance', color_continuous_scale='viridis')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show detailed importance table
                    st.markdown("**Detailed Feature Importance:**")
                    st.dataframe(shap_importance.head(10), use_container_width=True)
                    
                    # Comparison with traditional importance
                    st.markdown("**SHAP vs Traditional Feature Importance:**")
                    st.write("SHAP provides more accurate feature importance by considering feature interactions and non-linear relationships.")
        
        # Apply filters
        filtered_df = df.copy()
        if risk_filter != 'All':
            filtered_df = filtered_df[filtered_df['RISK_LABEL'] == risk_filter]
        if gender_filter != 'All':
            filtered_df = filtered_df[filtered_df['GENDER'] == gender_filter]
        if search:
            filtered_df = filtered_df[filtered_df['DESYNPUF_ID'].str.contains(search, case=False, na=False)]
        
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total_patients = len(filtered_df)
            st.metric("Total Patients", total_patients, delta=f"+{total_patients - current_patient_count}" if total_patients > current_patient_count else None)
        with col2:
            high_risk = len(filtered_df[filtered_df['RISK_LABEL'].isin(['High Risk', 'Very High Risk'])])
            st.metric("High Risk Patients", high_risk)
        with col3:
            avg_age = filtered_df['AGE'].mean()
            st.metric("Average Age", f"{avg_age:.1f} years")
        with col4:
            avg_part_a = filtered_df['PARTA'].mean()
            st.metric("Avg Part A", f"{avg_part_a:.1f}")
        
        # Charts
        col1, col2 = st.columns(2)
        with col1:
            risk_counts = filtered_df['RISK_LABEL'].value_counts()
            fig_risk = px.pie(values=risk_counts.values, names=risk_counts.index, title="Risk Distribution")
            st.plotly_chart(fig_risk, use_container_width=True)
        
        with col2:
            fig_age = px.scatter(filtered_df, x='AGE', y='RISK_30D', color='RISK_LABEL', 
                               title="Age vs Risk Score", hover_data=['DESYNPUF_ID'])
            st.plotly_chart(fig_age, use_container_width=True)
        
        # Data table with email and send buttons
        st.markdown("### 📋 Patient Data")
        
        # Add email column if it exists
        if 'EMAIL' in filtered_df.columns:
            # Create a copy for display
            display_df = filtered_df.copy()
            
            # Add header row
            header_col1, header_col2, header_col3, header_col4, header_col5, header_col6, header_col7, header_col8 = st.columns([2, 1, 1, 1, 1, 2, 1, 1])
            with header_col1:
                st.markdown("**Patient ID**")
            with header_col2:
                st.markdown("**Age**")
            with header_col3:
                st.markdown("**Gender**")
            with header_col4:
                st.markdown("**Risk**")
            with header_col5:
                st.markdown("**Level**")
            with header_col6:
                st.markdown("**Email** (✅=PDF available, ❌=PDF missing)")
            with header_col7:
                st.markdown("**Download**")
            with header_col8:
                st.markdown("**Send**")
            
            st.markdown("---")
            
            # Add Send Email button for each patient
            for index, row in display_df.iterrows():
                patient_id = row['DESYNPUF_ID']
                patient_email = row.get('EMAIL', '')
                
                # Create a unique key for each button
                button_key = f"send_email_{patient_id}_{index}"
                
                # Check if PDF exists for this patient
                try:
                    from pdf_generator import pdf_generator
                    pdf_path = pdf_generator.get_patient_pdf_path(patient_id)
                    pdf_exists = pdf_path is not None and os.path.exists(pdf_path)
                except:
                    pdf_exists = False
                
                # Create columns for the row
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([2, 1, 1, 1, 1, 2, 1, 1])
                
                with col1:
                    st.write(f"**{patient_id}**")
                with col2:
                    st.write(f"{row['AGE']}")
                with col3:
                    st.write(f"{row['GENDER']}")
                with col4:
                    st.write(f"{row['RISK_30D']}%")
                with col5:
                    st.write(f"{row['RISK_LABEL']}")
                with col6:
                    email_text = patient_email if patient_email else 'No email'
                    pdf_status = "✅" if pdf_exists else "❌"
                    st.write(f"{email_text} {pdf_status}")
                with col7:
                    # Download button
                    if pdf_exists:
                        # Create download button with PDF data
                        try:
                            with open(pdf_path, "rb") as pdf_file:
                                pdf_data = pdf_file.read()
                                st.download_button(
                                    label="📄 Download",
                                    data=pdf_data,
                                    file_name=f"patient_report_{patient_id}.pdf",
                                    mime="application/pdf",
                                    key=f"download_{patient_id}_{index}",
                                    help=f"Download PDF report for patient {patient_id}"
                                )
                        except Exception as e:
                            st.error(f"❌ Download error: {str(e)}")
                    else:
                        st.button("📄 Download", key=f"download_disabled_{patient_id}_{index}", disabled=True, help="PDF not available")
                with col8:
                    # Send button
                    if st.button(f"📧 Send", key=button_key, disabled=not patient_email or not pdf_exists):
                        if not patient_email:
                            st.error("❌ No email address for this patient")
                        elif not pdf_exists:
                            st.error("❌ PDF not found. Generate PDF first.")
                        else:
                            with st.spinner(f"📧 Sending email to {patient_email}..."):
                                try:
                                    # Get patient data for email service
                                    patient_data = {
                                        'EMAIL': patient_email,
                                        'DESYNPUF_ID': patient_id
                                    }
                                    
                                    # Use the enhanced email service
                                    from email_config_streamlit import send_patient_email_wrapper
                                    result = send_patient_email_wrapper(patient_data, patient_id, pdf_path)
                                    
                                    if result.get('success', False):
                                        method = result.get('method', 'Email')
                                        st.success(f"✅ Email sent to {patient_email} via {method}")
                                    else:
                                        error_msg = result.get('error', 'Unknown error')
                                        details = result.get('details', '')
                                        if details:
                                            st.error(f"❌ Email failed: {error_msg}\n\n**Details:** {details}")
                                        else:
                                            st.error(f"❌ Email failed: {error_msg}")
                                except Exception as e:
                                    st.error(f"❌ Email error: {str(e)}")
            
            # Show PDF status with detailed information
            try:
                from pdf_generator import pdf_generator
                pdf_files = pdf_generator.list_all_pdfs()
                
                # Count patients with PDFs
                patients_with_pdfs = 0
                for index, row in display_df.iterrows():
                    patient_id = row['DESYNPUF_ID']
                    pdf_path = pdf_generator.get_patient_pdf_path(patient_id)
                    if pdf_path and os.path.exists(pdf_path):
                        patients_with_pdfs += 1
                
                st.info(f"📄 PDF Status: {patients_with_pdfs}/{len(display_df)} patients have PDF reports available")
                
                if patients_with_pdfs < len(display_df):
                    st.warning(f"⚠️ {len(display_df) - patients_with_pdfs} patients missing PDF reports. Click '📄 Generate PDFs for All Patients' to create missing reports.")
                
            except Exception as e:
                st.warning(f"📄 PDF Status: Unable to check PDF files - {str(e)}")
        else:
            # Fallback to regular dataframe if no EMAIL column
            base_cols = ['DESYNPUF_ID', 'AGE', 'GENDER', 'RISK_30D', 'RISK_LABEL', 'PARTA', 'PARTB', 'HMO', 'PARTD']
            existing_cols = [col for col in base_cols if col in filtered_df.columns]
            if 'AI_RECOMMENDATIONS' in filtered_df.columns:
                existing_cols.append('AI_RECOMMENDATIONS')
            st.dataframe(filtered_df[existing_cols], use_container_width=True)
    
    with tab3:
        st.markdown("## 📋 Patient Management")
        
        # Use the already loaded data from the main function
        # df is already available from the main function scope
        if not df.empty:
            patient_ids = df['DESYNPUF_ID'].tolist()
            selected_patient = st.selectbox("Select Patient", patient_ids)
            
            if selected_patient:
                patient = df[df['DESYNPUF_ID'] == selected_patient].iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### Patient Information")
                    st.write(f"**ID:** {patient['DESYNPUF_ID']}")
                    st.write(f"**Age:** {patient['AGE']}")
                    st.write(f"**Gender:** {patient['GENDER']}")
                    st.write(f"**BMI:** {patient['BMI']}")
                    st.write(f"**BP:** {patient['BP_S']}")
                    st.write(f"**Glucose:** {patient['GLUCOSE']}")
                
                with col2:
                    st.markdown("### Risk Assessment")
                    st.write(f"**30-Day Risk:** {patient['RISK_30D']}%")
                    st.write(f"**60-Day Risk:** {patient['RISK_60D']}%")
                    st.write(f"**90-Day Risk:** {patient['RISK_90D']}%")
                    st.write(f"**Risk Level:** {patient['RISK_LABEL']}")
                    st.write(f"**Top Features:** {patient['TOP_3_FEATURES']}")
                
                # Add SHAP Analysis Section
                if shap_explainer is not None:
                    st.markdown("### 🔍 SHAP Feature Analysis")
                    st.info("SHAP (SHapley Additive exPlanations) shows how each feature contributes to the risk prediction.")
                    
                    # Generate SHAP explanation for this patient
                    try:
                        feature_columns = [col for col in df.columns if col not in ['DESYNPUF_ID', 'RISK_30D', 'RISK_60D', 'RISK_90D', 'RISK_LABEL', 'TOP_3_FEATURES', 'AI_RECOMMENDATIONS', 'EMAIL', 'SHAP_EXPLANATION']]
                        shap_explanation = get_patient_shap_explanation(patient, feature_columns, None, shap_explainer)
                        st.write(f"**SHAP Analysis:** {shap_explanation}")
                        
                        # Show global SHAP importance
                        shap_importance = get_global_shap_importance()
                        if shap_importance is not None:
                            st.markdown("**Global Feature Importance (SHAP):**")
                            top_shap_features = shap_importance.head(5)
                            for i, row in top_shap_features.iterrows():
                                st.write(f"• **{row['feature']}**: {row['shap_importance']:.2f}")
                    except Exception as e:
                        st.error(f"Error generating SHAP analysis: {str(e)}")
                
                st.markdown("### AI Recommendations")
                if 'AI_RECOMMENDATIONS' in patient.index:
                    recommendations = patient.get('AI_RECOMMENDATIONS', 'No recommendations')
                    if recommendations and recommendations != 'None' and recommendations != '' and not pd.isna(recommendations):
                        try:
                            rec_list = recommendations.split(' | ')
                            for i, rec in enumerate(rec_list, 1):
                                st.write(f"**{i}.** {rec}")
                        except AttributeError:
                            st.write("No recommendations available")
                    else:
                        st.write("No recommendations available")
                else:
                    st.write("AI recommendations not available for this patient")
                
                # Update recommendations
                if st.button("🔄 Regenerate AI Recommendations"):
                    ai_model = AIRiskModel()
                    
                    patient_data = {
                        'AGE': patient['AGE'],
                        'GENDER': 'Male' if patient['GENDER'] == 1 else 'Female',
                        'BMI': patient['BMI'],
                        'BP_S': patient['BP_S'],
                        'GLUCOSE': patient['GLUCOSE'],
                        'HbA1c': patient['HbA1c'],
                        'CHOLESTEROL': patient['CHOLESTEROL'],
                        'PARTA': patient.get('PARTA', 12),
                        'PARTB': patient.get('PARTB', 12),
                        'HMO': patient.get('HMO', 0),
                        'PARTD': patient.get('PARTD', 0),
                        'MEDICAL_CONDITIONS': []
                    }
                    
                    # Add conditions
                    conditions = []
                    if patient['ALZHEIMER'] == 1: conditions.append('Alzheimer')
                    if patient['HEARTFAILURE'] == 1: conditions.append('Heart Disease')
                    if patient['CANCER'] == 1: conditions.append('Cancer')
                    if patient['PULMONARY'] == 1: conditions.append('Lung Disease')
                    if patient['OSTEOPOROSIS'] == 1: conditions.append('Osteoporosis')
                    if patient['RHEUMATOID'] == 1: conditions.append('Arthritis')
                    if patient['STROKE'] == 1: conditions.append('Stroke')
                    if patient['RENAL_DISEASE'] == 1: conditions.append('Kidney Disease')
                    
                    patient_data['MEDICAL_CONDITIONS'] = conditions
                    
                    new_predictions = ai_model.predict_risk(patient_data)
                    
                    # Update dataframe
                    df.loc[df['DESYNPUF_ID'] == selected_patient, 'AI_RECOMMENDATIONS'] = new_predictions['AI_RECOMMENDATIONS']
                    df.loc[df['DESYNPUF_ID'] == selected_patient, 'RISK_30D'] = new_predictions['RISK_30D']
                    df.loc[df['DESYNPUF_ID'] == selected_patient, 'RISK_60D'] = new_predictions['RISK_60D']
                    df.loc[df['DESYNPUF_ID'] == selected_patient, 'RISK_90D'] = new_predictions['RISK_90D']
                    df.loc[df['DESYNPUF_ID'] == selected_patient, 'RISK_LABEL'] = new_predictions['RISK_LABEL']
                    df.loc[df['DESYNPUF_ID'] == selected_patient, 'TOP_3_FEATURES'] = new_predictions['TOP_3_FEATURES']
                    
                    df.to_csv('index.csv', index=False)
                    st.success("✅ AI recommendations updated successfully!")
                    st.cache_data.clear()
                    st.rerun()

if __name__ == "__main__":
    main()
