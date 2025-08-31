# 🏥 Interactive Healthcare Risk Stratification Dashboard

## 📋 Overview

This is a comprehensive interactive dashboard built with **Streamlit** and **Plotly** for analyzing healthcare risk stratification data. The dashboard provides powerful visualization and analysis tools for the `index.csv` dataset containing patient information, medical conditions, and risk assessments.

## ✨ Features

### 🎯 **Interactive Visualizations**
- **Risk Level Distribution**: Pie chart showing patient risk categories
- **Age vs Risk Score**: Scatter plot with color coding and size indicators
- **Medical Conditions Prevalence**: Horizontal bar chart of condition frequencies
- **Claims Cost Distribution**: Histogram of healthcare costs
- **BMI Distribution**: Box plots across risk levels
- **Blood Pressure vs Glucose**: Scatter plot with patient details
- **Healthcare Utilization**: Bar chart of admission types
- **Medication Adherence**: Distribution histogram
- **Risk Score Trends**: Line chart showing 30/60/90 day trends

### 🔍 **Advanced Filtering & Search**
- **Risk Level Filter**: Filter by Very High/High/Moderate/Low/Very Low Risk
- **Age Group Filter**: Filter by age ranges (18-30, 31-50, 51-65, 66-80, 80+)
- **Gender Filter**: Filter by Male/Female
- **BMI Category Filter**: Filter by Underweight/Normal/Overweight/Obese
- **Patient ID Search**: Real-time search functionality
- **Dynamic Filtering**: All filters work together for precise data selection

### 📊 **Key Metrics Dashboard**
- **Total Patients**: Current count based on filters
- **High Risk Patients**: Count of high and very high risk patients
- **Average Age**: Mean age of filtered patients
- **Average Claims Cost**: Mean healthcare costs

### 📋 **Interactive Data Table**
- **Sortable Columns**: Sort by any column (Patient ID, Age, Risk Score, etc.)
- **Pagination**: Navigate through large datasets
- **Configurable Page Size**: 10, 25, 50, or 100 rows per page
- **Real-time Updates**: Table updates based on applied filters

### 📈 **Summary Statistics**
- **Numerical Variables**: Descriptive statistics for all numeric fields
- **Categorical Variables**: Frequency distributions and percentages
- **Comprehensive Analysis**: Statistical insights for all data columns

### 💾 **Export Functionality**
- **CSV Export**: Download filtered data as CSV file
- **Summary Report**: Generate and download comprehensive analysis report
- **Timestamped Files**: Automatic file naming with date/time stamps

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- `index.csv` file in the same directory

### Installation

1. **Install Dependencies**:
   ```bash
   pip install -r dashboard_requirements.txt
   ```

2. **Run the Dashboard**:
   ```bash
   streamlit run dashboard.py
   ```

3. **Access the Dashboard**:
   - Open your web browser
   - Go to: `http://localhost:8501`
   - The dashboard will load automatically

## 📁 File Structure

```
├── dashboard.py                 # Main dashboard application
├── dashboard_requirements.txt   # Python dependencies
├── index.csv                   # Healthcare dataset
└── DASHBOARD_README.md         # This file
```

## 🎨 Dashboard Layout

### **Header Section**
- Main title with healthcare icon
- Custom styling for professional appearance

### **Sidebar Filters** (Left Panel)
- Risk Level dropdown
- Age Group dropdown
- Gender dropdown
- BMI Category dropdown
- Patient ID search box

### **Main Content Area**
1. **Key Metrics Row**: 4 metric cards showing important statistics
2. **Visualization Grid**: Multiple charts in responsive layout
3. **Interactive Table**: Sortable and paginated data table
4. **Summary Statistics**: Statistical analysis section
5. **Export Section**: Download buttons for data and reports

## 📊 Data Columns Analyzed

### **Patient Demographics**
- `DESYNPUF_ID`: Patient identifier
- `AGE`: Patient age
- `GENDER`: Male/Female (0/1)

### **Medical Conditions** (Binary: 0/1)
- `ALZHEIMER`: Alzheimer's disease
- `HEARTFAILURE`: Heart failure
- `CANCER`: Cancer diagnosis
- `PULMONARY`: Pulmonary disease
- `OSTEOPOROSIS`: Osteoporosis
- `RHEUMATOID`: Rheumatoid arthritis
- `STROKE`: Stroke history
- `RENAL_DISEASE`: Kidney disease

### **Health Metrics**
- `BMI`: Body Mass Index
- `BP_S`: Blood Pressure (Systolic)
- `GLUCOSE`: Blood glucose level
- `HbA1c`: Hemoglobin A1c
- `CHOLESTEROL`: Cholesterol level

### **Healthcare Utilization**
- `TOTAL_CLAIMS_COST`: Total healthcare costs
- `IN_ADM`: Inpatient admissions
- `OUT_VISITS`: Outpatient visits
- `ED_VISITS`: Emergency department visits
- `RX_ADH`: Medication adherence

### **Risk Assessment**
- `RISK_30D`: 30-day risk score
- `RISK_60D`: 60-day risk score
- `RISK_90D`: 90-day risk score
- `RISK_LABEL`: Risk category (Very High/High/Moderate/Low/Very Low)
- `TOP_3_FEATURES`: Most important risk factors

## 🔧 Customization Options

### **Adding New Visualizations**
1. Add new chart functions in the main section
2. Use Plotly Express for quick charts
3. Customize colors and layouts as needed

### **Modifying Filters**
1. Add new filter variables in the sidebar
2. Update the filtering logic in the main function
3. Ensure new filters work with existing ones

### **Changing Styling**
1. Modify the CSS in the `st.markdown` section
2. Update color schemes and fonts
3. Adjust layout and spacing

## 📱 Mobile Responsiveness

The dashboard is fully responsive and works on:
- **Desktop**: Full feature access with wide layout
- **Tablet**: Optimized layout with sidebar
- **Mobile**: Responsive design with touch-friendly controls

## 🎯 Use Cases

### **For Healthcare Administrators**
- Monitor patient risk distributions
- Analyze healthcare utilization patterns
- Track cost trends and outliers
- Generate reports for stakeholders

### **For Medical Professionals**
- Identify high-risk patient groups
- Analyze medical condition correlations
- Monitor medication adherence patterns
- Assess age-related risk factors

### **For Data Analysts**
- Explore dataset patterns and trends
- Perform statistical analysis
- Export filtered data for further analysis
- Generate comprehensive reports

## 🚨 Troubleshooting

### **Common Issues**

1. **Dashboard won't start**:
   - Check if `index.csv` exists in the same directory
   - Verify all dependencies are installed
   - Ensure Python version is 3.8+

2. **Charts not loading**:
   - Check browser console for JavaScript errors
   - Verify internet connection (for Plotly CDN)
   - Try refreshing the page

3. **Filters not working**:
   - Check data column names match exactly
   - Verify data types are correct
   - Clear browser cache and restart

### **Performance Tips**
- Use smaller page sizes for large datasets
- Apply filters before viewing detailed tables
- Close other browser tabs to free memory

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your data format matches the expected structure
3. Ensure all dependencies are properly installed

## 🔄 Updates and Maintenance

### **Regular Updates**
- Keep Streamlit and Plotly updated
- Monitor for new features and improvements
- Update requirements file as needed

### **Data Updates**
- Replace `index.csv` with new data
- Ensure column names remain consistent
- Verify data quality and completeness

---

**🎉 Enjoy exploring your healthcare data with this interactive dashboard!**
