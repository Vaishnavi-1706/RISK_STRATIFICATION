#!/usr/bin/env python3
"""
New Patient Risk Assessment Dashboard
Integrated with AI Model for Risk Predictions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import warnings
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
    try:
        df = pd.read_csv('index.csv')
        df['GENDER'] = df['GENDER'].map({0: 'Female', 1: 'Male'})
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def save_new_patient(patient_data, predictions):
    try:
        df = load_data()
        
        # Add AI_RECOMMENDATIONS column if it doesn't exist
        if 'AI_RECOMMENDATIONS' not in df.columns:
            df['AI_RECOMMENDATIONS'] = ''
        
        new_patient = {
            'DESYNPUF_ID': f"NEW_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'AGE': patient_data['AGE'],
            'GENDER': 1 if patient_data['GENDER'] == 'Male' else 0,
            'RENAL_DISEASE': 1 if 'Kidney Disease' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'PARTA': 12, 'PARTB': 12, 'HMO': 0, 'PARTD': 12,
            'ALZHEIMER': 1 if 'Alzheimer' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'HEARTFAILURE': 1 if 'Heart Disease' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'CANCER': 1 if 'Cancer' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'PULMONARY': 1 if 'Lung Disease' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'OSTEOPOROSIS': 1 if 'Osteoporosis' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'RHEUMATOID': 1 if 'Arthritis' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'STROKE': 1 if 'Stroke' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'TOTAL_CLAIMS_COST': patient_data['TOTAL_CLAIMS_COST'],
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
            'AI_RECOMMENDATIONS': predictions['AI_RECOMMENDATIONS'],
            'EMAIL': patient_data.get('EMAIL', '')
        }
        
        df = pd.concat([df, pd.DataFrame([new_patient])], ignore_index=True)
        df.to_csv('index.csv', index=False)
        return True, new_patient['DESYNPUF_ID']
    except Exception as e:
        return False, str(e)

def main():
    st.markdown('<h1 style="text-align: center; color: #1f77b4;">🏥 New Patient Risk Assessment Dashboard</h1>', unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["🆕 New Patient", "📊 Dashboard", "📋 Patient Management"])
    
    with tab1:
        st.markdown("## 🆕 New Patient Risk Assessment Form")
        
        with st.form("new_patient_form"):
            st.markdown("### Patient Demographics")
            col1, col2 = st.columns(2)
            
            with col1:
                age = st.number_input("Age", min_value=18, max_value=120, value=50)
                gender = st.selectbox("Gender", ["Male", "Female"])
                bmi = st.number_input("BMI", min_value=15.0, max_value=50.0, value=25.0, step=0.1)
                bp_s = st.number_input("Blood Pressure (Systolic)", min_value=80, max_value=200, value=120)
            
            with col2:
                glucose = st.number_input("Glucose Level", min_value=70, max_value=300, value=100)
                hba1c = st.number_input("HbA1c", min_value=4.0, max_value=15.0, value=5.5, step=0.1)
                cholesterol = st.number_input("Cholesterol", min_value=100, max_value=400, value=200)
                total_claims_cost = st.number_input("Total Claims Cost ($)", min_value=0, max_value=50000, value=2000)
            
            st.markdown("### Medical Conditions")
            medical_conditions = st.multiselect(
                "Select Medical Conditions",
                ["Diabetes", "Heart Disease", "Cancer", "Lung Disease", "Alzheimer", 
                 "Osteoporosis", "Arthritis", "Stroke", "Kidney Disease", "Obesity"]
            )
            
            email = st.text_input("Email Address (Optional)", placeholder="patient@example.com")
            
            submitted = st.form_submit_button("🚀 Generate Risk Assessment")
            
            if submitted:
                patient_data = {
                    'AGE': age,
                    'GENDER': gender,
                    'BMI': bmi,
                    'BP_S': bp_s,
                    'GLUCOSE': glucose,
                    'HbA1c': hba1c,
                    'CHOLESTEROL': cholesterol,
                    'TOTAL_CLAIMS_COST': total_claims_cost,
                    'MEDICAL_CONDITIONS': medical_conditions,
                    'EMAIL': email
                }
                
                ai_model = AIRiskModel()
                predictions = ai_model.predict_risk(patient_data)
                
                st.markdown("## 📊 Risk Assessment Results")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("30-Day Risk", f"{predictions['RISK_30D']}%")
                with col2:
                    st.metric("60-Day Risk", f"{predictions['RISK_60D']}%")
                with col3:
                    st.metric("90-Day Risk", f"{predictions['RISK_90D']}%")
                with col4:
                    st.metric("Risk Level", predictions['RISK_LABEL'])
                
                st.markdown("### 🤖 AI Recommendations")
                recommendations = predictions['AI_RECOMMENDATIONS'].split(' | ')
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"**{i}.** {rec}")
                
                st.markdown("### 💾 Save to Dataset")
                save_button = st.form_submit_button("✅ Save New Patient to Dataset")
                if save_button:
                    success, result = save_new_patient(patient_data, predictions)
                    if success:
                        st.success(f"✅ Patient saved successfully! Patient ID: {result}")
                        st.balloons()
                        st.cache_data.clear()
                    else:
                        st.error(f"❌ Error saving patient: {result}")
    
    with tab2:
        df = load_data()
        
        if df.empty:
            st.error("No data available.")
            return
        
        st.markdown("## 📊 Patient Dashboard")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            risk_filter = st.selectbox("Risk Level", ['All'] + list(df['RISK_LABEL'].unique()))
        with col2:
            gender_filter = st.selectbox("Gender", ['All'] + list(df['GENDER'].unique()))
        with col3:
            search = st.text_input("Search Patient ID")
        
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
            st.metric("Total Patients", len(filtered_df))
        with col2:
            high_risk = len(filtered_df[filtered_df['RISK_LABEL'].isin(['High Risk', 'Very High Risk'])])
            st.metric("High Risk Patients", high_risk)
        with col3:
            avg_age = filtered_df['AGE'].mean()
            st.metric("Average Age", f"{avg_age:.1f} years")
        with col4:
            avg_cost = filtered_df['TOTAL_CLAIMS_COST'].mean()
            st.metric("Avg Cost", f"${avg_cost:,.0f}")
        
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
        
        # Data table
        st.markdown("### 📋 Patient Data")
        # Check which columns exist in the dataset
        available_cols = ['DESYNPUF_ID', 'AGE', 'GENDER', 'RISK_30D', 'RISK_LABEL', 'TOTAL_CLAIMS_COST']
        if 'AI_RECOMMENDATIONS' in filtered_df.columns:
            available_cols.append('AI_RECOMMENDATIONS')
        st.dataframe(filtered_df[available_cols], use_container_width=True)
    
    with tab3:
        st.markdown("## 📋 Patient Management")
        
        df = load_data()
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
                
                st.markdown("### AI Recommendations")
                if 'AI_RECOMMENDATIONS' in patient.index:
                    recommendations = patient.get('AI_RECOMMENDATIONS', 'No recommendations')
                    if recommendations and recommendations != 'None':
                        rec_list = recommendations.split(' | ')
                        for i, rec in enumerate(rec_list, 1):
                            st.write(f"**{i}.** {rec}")
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
                        'TOTAL_CLAIMS_COST': patient['TOTAL_CLAIMS_COST'],
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
                    # Add AI_RECOMMENDATIONS column if it doesn't exist
                    if 'AI_RECOMMENDATIONS' not in df.columns:
                        df['AI_RECOMMENDATIONS'] = ''
                    
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
