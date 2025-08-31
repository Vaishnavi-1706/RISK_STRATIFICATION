#!/usr/bin/env python3
"""
Enhanced Interactive Healthcare Risk Stratification Dashboard
Integrated with New Patient Form and AI Model
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Enhanced Healthcare Risk Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .prediction-result {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# AI Model Simulation
class AIRiskModel:
    def __init__(self):
        self.risk_thresholds = {
            'AGE': {'high_risk': 75, 'moderate_risk': 65},
            'BMI': {'high': 30, 'low': 18.5},
            'BP_S': {'high': 140, 'low': 90},
            'GLUCOSE': {'high': 126},
            'HbA1c': {'high': 6.5},
            'CHOLESTEROL': {'high': 200},
            'TOTAL_CLAIMS_COST': {'high': 5000}
        }
    
    def predict_risk(self, patient_data: dict) -> dict:
        risk_factors = []
        risk_score_30d = 0
        risk_score_60d = 0
        risk_score_90d = 0
        
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
        
        # HbA1c factor
        hba1c = patient_data.get('HbA1c', 0)
        if hba1c >= 6.5:
            risk_factors.append('HbA1c')
            risk_score_30d += 20
            risk_score_60d += 25
            risk_score_90d += 30
        
        # Cholesterol factor
        cholesterol = patient_data.get('CHOLESTEROL', 0)
        if cholesterol >= 200:
            risk_factors.append('CHOLESTEROL')
            risk_score_30d += 15
            risk_score_60d += 20
            risk_score_90d += 25
        
        # Medical conditions factor
        conditions = patient_data.get('MEDICAL_CONDITIONS', [])
        for condition in conditions:
            risk_factors.append(condition)
            risk_score_30d += 10
            risk_score_60d += 15
            risk_score_90d += 20
        
        # Claims cost factor
        claims_cost = patient_data.get('TOTAL_CLAIMS_COST', 0)
        if claims_cost >= 5000:
            risk_factors.append('TOTAL_CLAIMS_COST')
            risk_score_30d += 15
            risk_score_60d += 20
            risk_score_90d += 25
        
        # Cap risk scores at 100
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
        
        # Generate AI recommendations
        recommendations = self.generate_recommendations(patient_data, risk_factors, risk_label)
        
        return {
            'RISK_30D': risk_score_30d,
            'RISK_60D': risk_score_60d,
            'RISK_90D': risk_score_90d,
            'RISK_LABEL': risk_label,
            'TOP_3_FEATURES': ', '.join(risk_factors[:3]) if risk_factors else 'AGE, BMI, GLUCOSE',
            'AI_RECOMMENDATIONS': recommendations
        }
    
    def generate_recommendations(self, patient_data: dict, risk_factors: list, risk_label: str) -> str:
        recommendations = []
        
        # Age-based recommendations
        age = patient_data.get('AGE', 0)
        if age >= 75:
            recommendations.append("Schedule comprehensive geriatric assessment")
        elif age >= 65:
            recommendations.append("Annual wellness visit recommended")
        
        # Condition-based recommendations
        conditions = patient_data.get('MEDICAL_CONDITIONS', [])
        if 'Diabetes' in conditions or 'GLUCOSE' in risk_factors:
            recommendations.append("Endocrinology consultation for diabetes management")
        if 'Heart Disease' in conditions or 'BP_S' in risk_factors:
            recommendations.append("Cardiology consultation for cardiovascular health")
        if 'Obesity' in conditions or 'BMI' in risk_factors:
            recommendations.append("Nutrition consultation for weight management")
        
        # Risk-level based recommendations
        if risk_label in ["Very High Risk", "High Risk"]:
            recommendations.append("Immediate care coordination recommended")
            recommendations.append("Enhanced monitoring and follow-up scheduling")
        elif risk_label == "Moderate Risk":
            recommendations.append("Regular monitoring recommended")
        else:
            recommendations.append("Continue preventive care routine")
        
        # Limit to 3 recommendations
        return " | ".join(recommendations[:3])

@st.cache_data
def load_data():
    """Load and preprocess the dataset"""
    try:
        df = pd.read_csv('index.csv')
        
        # Convert GENDER to categorical
        df['GENDER'] = df['GENDER'].map({0: 'Female', 1: 'Male'})
        
        # Create age groups
        df['AGE_GROUP'] = pd.cut(df['AGE'], 
                                bins=[0, 30, 50, 65, 80, 100], 
                                labels=['18-30', '31-50', '51-65', '66-80', '80+'])
        
        # Create BMI categories
        df['BMI_CATEGORY'] = pd.cut(df['BMI'], 
                                   bins=[0, 18.5, 25, 30, 100], 
                                   labels=['Underweight', 'Normal', 'Overweight', 'Obese'])
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def save_new_patient(patient_data: dict, predictions: dict):
    """Save new patient data to CSV file"""
    try:
        # Load existing data
        df = load_data()
        
        # Create new patient record
        new_patient = {
            'DESYNPUF_ID': f"NEW_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'AGE': patient_data['AGE'],
            'GENDER': 1 if patient_data['GENDER'] == 'Male' else 0,
            'RENAL_DISEASE': 1 if 'Kidney Disease' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'PARTA': 12,
            'PARTB': 12,
            'HMO': 0,
            'PARTD': 12,
            'ALZHEIMER': 1 if 'Alzheimer' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'HEARTFAILURE': 1 if 'Heart Disease' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'CANCER': 1 if 'Cancer' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'PULMONARY': 1 if 'Lung Disease' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'OSTEOPOROSIS': 1 if 'Osteoporosis' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'RHEUMATOID': 1 if 'Arthritis' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'STROKE': 1 if 'Stroke' in patient_data.get('MEDICAL_CONDITIONS', []) else 0,
            'TOTAL_CLAIMS_COST': patient_data['TOTAL_CLAIMS_COST'],
            'IN_ADM': 0,
            'OUT_VISITS': 1,
            'BMI': patient_data['BMI'],
            'BP_S': patient_data['BP_S'],
            'GLUCOSE': patient_data['GLUCOSE'],
            'HbA1c': patient_data['HbA1c'],
            'CHOLESTEROL': patient_data['CHOLESTEROL'],
            'ED_VISITS': 0,
            'RX_ADH': 0.8,
            'RISK_30D': predictions['RISK_30D'],
            'RISK_60D': predictions['RISK_60D'],
            'RISK_90D': predictions['RISK_90D'],
            'RISK_LABEL': predictions['RISK_LABEL'],
            'TOP_3_FEATURES': predictions['TOP_3_FEATURES'],
            'AI_RECOMMENDATIONS': predictions['AI_RECOMMENDATIONS'],
            'EMAIL': patient_data.get('EMAIL', '')
        }
        
        # Add to dataframe
        df = pd.concat([df, pd.DataFrame([new_patient])], ignore_index=True)
        
        # Save back to CSV
        df.to_csv('index.csv', index=False)
        
        return True, new_patient['DESYNPUF_ID']
    except Exception as e:
        return False, str(e)

def new_patient_form():
    """New Patient Risk Assessment Form"""
    st.markdown("## 🆕 New Patient Risk Assessment")
    
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
             "Osteoporosis", "Arthritis", "Stroke", "Kidney Disease", "Obesity"],
            help="Select all conditions that apply"
        )
        
        st.markdown("### Contact Information")
        email = st.text_input("Email Address (Optional)", placeholder="patient@example.com")
        
        submitted = st.form_submit_button("🚀 Generate Risk Assessment")
        
        if submitted:
            # Prepare patient data
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
            
            # Generate predictions
            ai_model = AIRiskModel()
            predictions = ai_model.predict_risk(patient_data)
            
            # Display results
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
            
            # Display recommendations
            st.markdown("### 🤖 AI Recommendations")
            recommendations = predictions['AI_RECOMMENDATIONS'].split(' | ')
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"**{i}.** {rec}")
            
            # Save to dataset option
            st.markdown("### 💾 Save to Dataset")
            if st.button("✅ Save New Patient to Dataset"):
                success, result = save_new_patient(patient_data, predictions)
                if success:
                    st.success(f"✅ Patient saved successfully! Patient ID: {result}")
                    st.balloons()
                    # Clear cache to reload data
                    st.cache_data.clear()
                else:
                    st.error(f"❌ Error saving patient: {result}")

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Enhanced Healthcare Risk Stratification Dashboard</h1>', unsafe_allow_html=True)
    
    # Navigation
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🆕 New Patient", "📋 Patient Management"])
    
    with tab1:
        # Load data
        df = load_data()
        
        if df.empty:
            st.error("No data loaded. Please check if 'index.csv' exists in the current directory.")
            return
        
        # Sidebar filters
        st.sidebar.markdown("## 🔍 Filters")
        
        # Risk level filter
        risk_levels = ['All'] + list(df['RISK_LABEL'].unique())
        selected_risk = st.sidebar.selectbox("Risk Level", risk_levels)
        
        # Age group filter
        age_groups = ['All'] + list(df['AGE_GROUP'].unique())
        selected_age = st.sidebar.selectbox("Age Group", age_groups)
        
        # Gender filter
        genders = ['All'] + list(df['GENDER'].unique())
        selected_gender = st.sidebar.selectbox("Gender", genders)
        
        # BMI category filter
        bmi_categories = ['All'] + list(df['BMI_CATEGORY'].unique())
        selected_bmi = st.sidebar.selectbox("BMI Category", bmi_categories)
        
        # Apply filters
        filtered_df = df.copy()
        if selected_risk != 'All':
            filtered_df = filtered_df[filtered_df['RISK_LABEL'] == selected_risk]
        if selected_age != 'All':
            filtered_df = filtered_df[filtered_df['AGE_GROUP'] == selected_age]
        if selected_gender != 'All':
            filtered_df = filtered_df[filtered_df['GENDER'] == selected_gender]
        if selected_bmi != 'All':
            filtered_df = filtered_df[filtered_df['BMI_CATEGORY'] == selected_bmi]
        
        # Search functionality
        st.sidebar.markdown("## 🔎 Search")
        search_term = st.sidebar.text_input("Search by Patient ID", "")
        if search_term:
            filtered_df = filtered_df[filtered_df['DESYNPUF_ID'].str.contains(search_term, case=False, na=False)]
        
        # Main content
        col1, col2, col3, col4 = st.columns(4)
        
        # Key metrics
        with col1:
            st.metric("Total Patients", len(filtered_df))
        
        with col2:
            high_risk_count = len(filtered_df[filtered_df['RISK_LABEL'].isin(['High Risk', 'Very High Risk'])])
            st.metric("High Risk Patients", high_risk_count)
        
        with col3:
            avg_age = filtered_df['AGE'].mean()
            st.metric("Average Age", f"{avg_age:.1f} years")
        
        with col4:
            avg_cost = filtered_df['TOTAL_CLAIMS_COST'].mean()
            st.metric("Avg Claims Cost", f"${avg_cost:,.0f}")
        
        # Charts section
        st.markdown("---")
        
        # Row 1: Risk Distribution and Age Analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Risk Level Distribution")
            risk_counts = filtered_df['RISK_LABEL'].value_counts()
            fig_risk = px.pie(
                values=risk_counts.values,
                names=risk_counts.index,
                title="Patient Risk Distribution",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_risk.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_risk, use_container_width=True)
        
        with col2:
            st.markdown("### 📈 Age vs Risk Score")
            fig_age_risk = px.scatter(
                filtered_df,
                x='AGE',
                y='RISK_30D',
                color='RISK_LABEL',
                size='TOTAL_CLAIMS_COST',
                hover_data=['DESYNPUF_ID', 'GENDER', 'BMI'],
                title="Age vs 30-Day Risk Score",
                color_discrete_sequence=px.colors.qualitative.Set1
            )
            fig_age_risk.update_layout(height=400)
            st.plotly_chart(fig_age_risk, use_container_width=True)
        
        # Interactive Data Table
        st.markdown("---")
        st.markdown("### 📋 Patient Data Table")
        
        # Sort options
        col1, col2 = st.columns([1, 3])
        with col1:
            sort_by = st.selectbox("Sort by", ['DESYNPUF_ID', 'AGE', 'RISK_30D', 'TOTAL_CLAIMS_COST', 'BMI'])
        with col2:
            sort_order = st.selectbox("Sort order", ['Ascending', 'Descending'])
        
        # Apply sorting
        ascending = sort_order == 'Ascending'
        sorted_df = filtered_df.sort_values(by=sort_by, ascending=ascending)
        
        # Display table with pagination
        page_size = st.selectbox("Rows per page", [10, 25, 50, 100])
        total_pages = len(sorted_df) // page_size + (1 if len(sorted_df) % page_size > 0 else 0)
        
        if total_pages > 1:
            page = st.selectbox("Page", range(1, total_pages + 1))
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            display_df = sorted_df.iloc[start_idx:end_idx]
        else:
            display_df = sorted_df
        
        # Format the table for display
        display_columns = ['DESYNPUF_ID', 'AGE', 'GENDER', 'RISK_30D', 'RISK_LABEL', 'TOTAL_CLAIMS_COST', 'BMI', 'BP_S', 'GLUCOSE', 'AI_RECOMMENDATIONS']
        st.dataframe(display_df[display_columns], use_container_width=True)
    
    with tab2:
        new_patient_form()
    
    with tab3:
        st.markdown("## 📋 Patient Management")
        
        # Load data for management
        df = load_data()
        
        if not df.empty:
            # Patient selection
            patient_ids = df['DESYNPUF_ID'].tolist()
            selected_patient_id = st.selectbox("Select Patient", patient_ids)
            
            if selected_patient_id:
                patient = df[df['DESYNPUF_ID'] == selected_patient_id].iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Patient Information")
                    st.write(f"**Patient ID:** {patient['DESYNPUF_ID']}")
                    st.write(f"**Age:** {patient['AGE']}")
                    st.write(f"**Gender:** {patient['GENDER']}")
                    st.write(f"**BMI:** {patient['BMI']}")
                    st.write(f"**Blood Pressure:** {patient['BP_S']}")
                    st.write(f"**Glucose:** {patient['GLUCOSE']}")
                    st.write(f"**HbA1c:** {patient['HbA1c']}")
                    st.write(f"**Cholesterol:** {patient['CHOLESTEROL']}")
                    st.write(f"**Total Claims Cost:** ${patient['TOTAL_CLAIMS_COST']:,.0f}")
                
                with col2:
                    st.markdown("### Risk Assessment")
                    st.write(f"**30-Day Risk:** {patient['RISK_30D']}%")
                    st.write(f"**60-Day Risk:** {patient['RISK_60D']}%")
                    st.write(f"**90-Day Risk:** {patient['RISK_90D']}%")
                    st.write(f"**Risk Level:** {patient['RISK_LABEL']}")
                    st.write(f"**Top Features:** {patient['TOP_3_FEATURES']}")
                    
                    st.markdown("### AI Recommendations")
                    recommendations = patient.get('AI_RECOMMENDATIONS', 'No recommendations available')
                    if recommendations and recommendations != 'None':
                        rec_list = recommendations.split(' | ')
                        for i, rec in enumerate(rec_list, 1):
                            st.write(f"**{i}.** {rec}")
                    else:
                        st.write("No recommendations available")
                
                # Update recommendations
                st.markdown("### 🔄 Update AI Recommendations")
                if st.button("🔄 Regenerate AI Recommendations"):
                    # Simulate updating recommendations
                    ai_model = AIRiskModel()
                    
                    # Create patient data for prediction
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
                    
                    # Add medical conditions
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
                    
                    # Generate new predictions
                    new_predictions = ai_model.predict_risk(patient_data)
                    
                    # Update the dataframe
                    df.loc[df['DESYNPUF_ID'] == selected_patient_id, 'AI_RECOMMENDATIONS'] = new_predictions['AI_RECOMMENDATIONS']
                    df.loc[df['DESYNPUF_ID'] == selected_patient_id, 'RISK_30D'] = new_predictions['RISK_30D']
                    df.loc[df['DESYNPUF_ID'] == selected_patient_id, 'RISK_60D'] = new_predictions['RISK_60D']
                    df.loc[df['DESYNPUF_ID'] == selected_patient_id, 'RISK_90D'] = new_predictions['RISK_90D']
                    df.loc[df['DESYNPUF_ID'] == selected_patient_id, 'RISK_LABEL'] = new_predictions['RISK_LABEL']
                    df.loc[df['DESYNPUF_ID'] == selected_patient_id, 'TOP_3_FEATURES'] = new_predictions['TOP_3_FEATURES']
                    
                    # Save updated data
                    df.to_csv('index.csv', index=False)
                    
                    st.success("✅ AI recommendations updated successfully!")
                    st.cache_data.clear()
                    st.rerun()

if __name__ == "__main__":
    main()
