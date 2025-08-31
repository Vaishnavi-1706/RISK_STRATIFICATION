#!/usr/bin/env python3
"""
Interactive Healthcare Risk Stratification Dashboard
Built with Streamlit for the index.csv dataset
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Healthcare Risk Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .risk-high { color: #d62728; font-weight: bold; }
    .risk-moderate { color: #ff7f0e; font-weight: bold; }
    .risk-low { color: #2ca02c; font-weight: bold; }
    .stSelectbox > div > div > div > div {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

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
        
        # Create cost categories
        df['COST_CATEGORY'] = pd.cut(df['TOTAL_CLAIMS_COST'], 
                                    bins=[0, 1000, 3000, 5000, 10000], 
                                    labels=['Low', 'Medium', 'High', 'Very High'])
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">🏥 Healthcare Risk Stratification Dashboard</h1>', unsafe_allow_html=True)
    
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
    
    # Row 2: Medical Conditions and Cost Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏥 Medical Conditions Prevalence")
        conditions = ['ALZHEIMER', 'HEARTFAILURE', 'CANCER', 'PULMONARY', 'OSTEOPOROSIS', 'RHEUMATOID', 'STROKE', 'RENAL_DISEASE']
        condition_counts = filtered_df[conditions].sum().sort_values(ascending=True)
        
        fig_conditions = px.bar(
            x=condition_counts.values,
            y=condition_counts.index,
            orientation='h',
            title="Number of Patients with Medical Conditions",
            color=condition_counts.values,
            color_continuous_scale='Reds'
        )
        fig_conditions.update_layout(height=400)
        st.plotly_chart(fig_conditions, use_container_width=True)
    
    with col2:
        st.markdown("### 💰 Claims Cost Distribution")
        fig_cost = px.histogram(
            filtered_df,
            x='TOTAL_CLAIMS_COST',
            nbins=20,
            title="Distribution of Total Claims Cost",
            color_discrete_sequence=['#2E86AB']
        )
        fig_cost.update_layout(height=400)
        st.plotly_chart(fig_cost, use_container_width=True)
    
    # Row 3: BMI and Health Metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📏 BMI Distribution by Risk Level")
        fig_bmi = px.box(
            filtered_df,
            x='RISK_LABEL',
            y='BMI',
            color='RISK_LABEL',
            title="BMI Distribution Across Risk Levels",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_bmi.update_layout(height=400)
        st.plotly_chart(fig_bmi, use_container_width=True)
    
    with col2:
        st.markdown("### 🩸 Blood Pressure vs Glucose")
        fig_bp_glucose = px.scatter(
            filtered_df,
            x='BP_S',
            y='GLUCOSE',
            color='RISK_LABEL',
            size='AGE',
            hover_data=['DESYNPUF_ID', 'BMI', 'CHOLESTEROL'],
            title="Blood Pressure vs Glucose Levels",
            color_discrete_sequence=px.colors.qualitative.Set1
        )
        fig_bp_glucose.update_layout(height=400)
        st.plotly_chart(fig_bp_glucose, use_container_width=True)
    
    # Row 4: Healthcare Utilization
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏥 Healthcare Utilization")
        utilization_data = filtered_df[['IN_ADM', 'OUT_VISITS', 'ED_VISITS']].sum()
        fig_utilization = px.bar(
            x=utilization_data.index,
            y=utilization_data.values,
            title="Healthcare Utilization Summary",
            color=utilization_data.values,
            color_continuous_scale='Blues'
        )
        fig_utilization.update_layout(height=400)
        st.plotly_chart(fig_utilization, use_container_width=True)
    
    with col2:
        st.markdown("### 💊 Medication Adherence")
        fig_adherence = px.histogram(
            filtered_df,
            x='RX_ADH',
            nbins=15,
            title="Medication Adherence Distribution",
            color_discrete_sequence=['#A23B72']
        )
        fig_adherence.update_layout(height=400)
        st.plotly_chart(fig_adherence, use_container_width=True)
    
    # Row 5: Risk Trends and Correlations
    st.markdown("### 📈 Risk Score Trends")
    risk_trends = filtered_df[['RISK_30D', 'RISK_60D', 'RISK_90D']].mean()
    fig_trends = px.line(
        x=['30 Days', '60 Days', '90 Days'],
        y=risk_trends.values,
        title="Average Risk Scores Over Time",
        markers=True
    )
    fig_trends.update_layout(height=400)
    st.plotly_chart(fig_trends, use_container_width=True)
    
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
    display_columns = ['DESYNPUF_ID', 'AGE', 'GENDER', 'RISK_30D', 'RISK_LABEL', 'TOTAL_CLAIMS_COST', 'BMI', 'BP_S', 'GLUCOSE']
    st.dataframe(display_df[display_columns], use_container_width=True)
    
    # Summary statistics
    st.markdown("---")
    st.markdown("### 📊 Summary Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Numerical Variables")
        numeric_cols = ['AGE', 'BMI', 'BP_S', 'GLUCOSE', 'HbA1c', 'CHOLESTEROL', 'TOTAL_CLAIMS_COST', 'RISK_30D']
        summary_stats = filtered_df[numeric_cols].describe()
        st.dataframe(summary_stats, use_container_width=True)
    
    with col2:
        st.markdown("#### Categorical Variables")
        categorical_cols = ['GENDER', 'RISK_LABEL', 'AGE_GROUP', 'BMI_CATEGORY']
        for col in categorical_cols:
            if col in filtered_df.columns:
                st.markdown(f"**{col}:**")
                value_counts = filtered_df[col].value_counts()
                for value, count in value_counts.items():
                    st.write(f"  - {value}: {count} ({count/len(filtered_df)*100:.1f}%)")
    
    # Export functionality
    st.markdown("---")
    st.markdown("### 💾 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Download Filtered Data as CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                label="Click to download",
                data=csv,
                file_name=f"healthcare_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📊 Download Summary Report"):
            # Create a summary report
            report = f"""
Healthcare Risk Stratification Dashboard - Summary Report
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Total Patients: {len(filtered_df)}
High Risk Patients: {high_risk_count}
Average Age: {avg_age:.1f} years
Average Claims Cost: ${avg_cost:,.0f}

Risk Level Distribution:
{filtered_df['RISK_LABEL'].value_counts().to_string()}

Top Medical Conditions:
{filtered_df[conditions].sum().sort_values(ascending=False).head(5).to_string()}
            """
            st.download_button(
                label="Click to download report",
                data=report,
                file_name=f"healthcare_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
