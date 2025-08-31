#!/usr/bin/env python3
"""
PDF Generator for Patient Risk Assessment Reports
Creates professional PDF reports similar to patient_report_004.pdf
"""

import os
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfgen import canvas
import io

class PatientPDFGenerator:
    """Generate professional patient risk assessment PDF reports"""
    
    def __init__(self, temp_folder="temp"):
        self.temp_folder = temp_folder
        self.ensure_temp_folder()
        
    def ensure_temp_folder(self):
        """Ensure temp folder exists"""
        if not os.path.exists(self.temp_folder):
            os.makedirs(self.temp_folder)
    
    def generate_patient_pdf(self, patient_data, predictions, patient_id):
        """Generate PDF report for a patient matching the sample format"""
        try:
            # Create PDF filename
            pdf_filename = f'patient_report_{patient_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            pdf_path = os.path.join(self.temp_folder, pdf_filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Custom styles matching the sample
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=20,
                alignment=TA_CENTER,
                textColor=colors.darkblue
            )
            
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=15,
                alignment=TA_LEFT,
                textColor=colors.darkblue
            )
            
            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                alignment=TA_LEFT
            )
            
            # Title - matching the sample format
            title = Paragraph("Risk Stratification – Patient Report", title_style)
            elements.append(title)
            
            # Date - top left like in sample
            date_text = f"Aug {datetime.now().strftime('%d, %Y')}"
            date_para = Paragraph(date_text, normal_style)
            elements.append(date_para)
            elements.append(Spacer(1, 20))
            
            # Patient Data Table - matching the sample format exactly
            # Determine primary condition
            conditions = patient_data.get('MEDICAL_CONDITIONS', [])
            primary_condition = conditions[0] if conditions else 'None'
            
            # Determine tier based on risk level
            risk_30d = predictions.get('RISK_30D', 0)
            if risk_30d >= 80:
                tier = 'Very High'
            elif risk_30d >= 60:
                tier = 'High'
            elif risk_30d >= 40:
                tier = 'Moderate'
            elif risk_30d >= 20:
                tier = 'Low'
            else:
                tier = 'Very Low'
            
            # Create patient data table matching the sample
            patient_data_table = [
                ['Patient ID', patient_id],
                ['Email', patient_data.get('EMAIL', 'Not provided')],
                ['Age', str(patient_data.get('AGE', 'N/A'))],
                ['Condition', primary_condition],
                ['Tier', tier],
                ['Cholesterol', f"{patient_data.get('CHOLESTEROL', 'N/A')} mg/dL"],
                ['HbA1c', f"{patient_data.get('HbA1c', 'N/A')}%"],
                ['Glucose', f"{patient_data.get('GLUCOSE', 'N/A')} mg/dL"],
                ['BMI', str(patient_data.get('BMI', 'N/A'))],
                ['30d Risk', f"{predictions.get('RISK_30D', 'N/A')}%"],
                ['60d Risk', f"{predictions.get('RISK_60D', 'N/A')}%"],
                ['90d Risk', f"{predictions.get('RISK_90D', 'N/A')}%"],
                ['Total Claims', f"${patient_data.get('TOTAL_CLAIMS_COST', 'N/A'):,.0f}"]
            ]
            
            # Create table with alternating row colors like the sample
            table_data = []
            for i, (label, value) in enumerate(patient_data_table):
                # Alternate background colors: light blue and white
                bg_color = colors.lightblue if i % 2 == 0 else colors.white
                table_data.append([label, value])
            
            # Add header row
            table_data.insert(0, ['Field', 'Value'])
            
            patient_table = Table(table_data, colWidths=[2.5*inch, 3.5*inch])
            patient_table.setStyle(TableStyle([
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                # Data rows styling
                ('BACKGROUND', (0, 1), (0, 1), colors.lightblue),
                ('BACKGROUND', (0, 3), (0, 3), colors.lightblue),
                ('BACKGROUND', (0, 5), (0, 5), colors.lightblue),
                ('BACKGROUND', (0, 7), (0, 7), colors.lightblue),
                ('BACKGROUND', (0, 9), (0, 9), colors.lightblue),
                ('BACKGROUND', (0, 11), (0, 11), colors.lightblue),
                ('BACKGROUND', (0, 13), (0, 13), colors.lightblue),
                # White rows
                ('BACKGROUND', (0, 2), (0, 2), colors.white),
                ('BACKGROUND', (0, 4), (0, 4), colors.white),
                ('BACKGROUND', (0, 6), (0, 6), colors.white),
                ('BACKGROUND', (0, 8), (0, 8), colors.white),
                ('BACKGROUND', (0, 10), (0, 10), colors.white),
                ('BACKGROUND', (0, 12), (0, 12), colors.white),
                # All cells styling
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(patient_table)
            elements.append(Spacer(1, 30))
            
            # Risk Timeline Section - matching the sample
            elements.append(Paragraph("Risk Timeline", subtitle_style))
            
            # Create risk timeline data
            risk_timeline_data = [
                ['Time Period', 'Risk Level', 'Risk Score', 'Trend'],
                ['30 Days', self._get_risk_level(predictions.get('RISK_30D', 0)), f"{predictions.get('RISK_30D', 'N/A')}%", self._get_trend_arrow(predictions.get('RISK_30D', 0))],
                ['60 Days', self._get_risk_level(predictions.get('RISK_60D', 0)), f"{predictions.get('RISK_60D', 'N/A')}%", self._get_trend_arrow(predictions.get('RISK_60D', 0))],
                ['90 Days', self._get_risk_level(predictions.get('RISK_90D', 0)), f"{predictions.get('RISK_90D', 'N/A')}%", self._get_trend_arrow(predictions.get('RISK_90D', 0))]
            ]
            
            timeline_table = Table(risk_timeline_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            timeline_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(timeline_table)
            elements.append(Spacer(1, 20))
            
            # Top Risk Factors Section
            elements.append(Paragraph("Top Risk Factors", subtitle_style))
            
            # Get top risk factors
            top_factors = predictions.get('TOP_3_FEATURES', 'AGE, BMI, GLUCOSE')
            factors_list = top_factors.split(', ')
            
            # Create risk factors table
            risk_factors_data = [
                ['Factor', 'Impact', 'Description'],
                [factors_list[0] if len(factors_list) > 0 else 'AGE', 'High', f"{factors_list[0] if len(factors_list) > 0 else 'Age'} contributes significantly to risk"],
                [factors_list[1] if len(factors_list) > 1 else 'BMI', 'Medium', f"{factors_list[1] if len(factors_list) > 1 else 'BMI'} affects overall health status"],
                [factors_list[2] if len(factors_list) > 2 else 'GLUCOSE', 'Medium', f"{factors_list[2] if len(factors_list) > 2 else 'Glucose'} indicates metabolic health"]
            ]
            
            factors_table = Table(risk_factors_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
            factors_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(factors_table)
            elements.append(Spacer(1, 20))
            
            # Prescribed Intervention Section
            elements.append(Paragraph("Prescribed Intervention", subtitle_style))
            
            recommendations = predictions.get('AI_RECOMMENDATIONS', 'No specific recommendations available')
            if recommendations and recommendations != 'None':
                rec_list = recommendations.split(' | ')
                intervention_text = f"Monthly care manager review, medication optimization, and diet counseling. {rec_list[0] if rec_list else 'Monitor health metrics closely'}."
            else:
                intervention_text = "Monthly care manager review, medication optimization, and diet counseling. Monitor health metrics closely."
            
            intervention_para = Paragraph(intervention_text, normal_style)
            elements.append(intervention_para)
            
            # Build PDF
            doc.build(elements)
            
            print(f"✅ PDF generated successfully: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            print(f"❌ Error generating PDF for patient {patient_id}: {e}")
            return None
    
    def _get_risk_color(self, risk_score):
        """Get risk level based on score"""
        if risk_score >= 80:
            return "Very High Risk"
        elif risk_score >= 60:
            return "High Risk"
        elif risk_score >= 40:
            return "Moderate Risk"
        elif risk_score >= 20:
            return "Low Risk"
        else:
            return "Very Low Risk"
    
    def _get_risk_level(self, risk_score):
        """Get risk level for timeline"""
        if risk_score >= 80:
            return "Very High"
        elif risk_score >= 60:
            return "High"
        elif risk_score >= 40:
            return "Moderate"
        elif risk_score >= 20:
            return "Low"
        else:
            return "Very Low"
    
    def _get_trend_arrow(self, risk_score):
        """Get trend arrow based on risk score"""
        if risk_score >= 70:
            return "↗️ High"
        elif risk_score >= 50:
            return "→ Medium"
        else:
            return "↘️ Low"
    
    def generate_pdfs_for_all_patients(self):
        """Generate PDFs for all existing patients in the dataset"""
        try:
            # Load the CSV file
            df = pd.read_csv('index.csv')
            
            # Initialize AI model
            from working_patient_dashboard import AIRiskModel
            ai_model = AIRiskModel()
            
            generated_count = 0
            
            for index, patient in df.iterrows():
                patient_id = patient['DESYNPUF_ID']
                
                # Check if PDF already exists
                existing_pdfs = [f for f in os.listdir(self.temp_folder) if f.startswith(f'patient_report_{patient_id}_')]
                if existing_pdfs:
                    print(f"⚠️ PDF already exists for patient {patient_id}, skipping...")
                    continue
                
                # Prepare patient data
                patient_data = {
                    'AGE': patient['AGE'],
                    'GENDER': 'Male' if patient['GENDER'] == 1 else 'Female',
                    'BMI': patient['BMI'],
                    'BP_S': patient['BP_S'],
                    'GLUCOSE': patient['GLUCOSE'],
                    'HbA1c': patient['HbA1c'],
                    'CHOLESTEROL': patient['CHOLESTEROL'],
                    'TOTAL_CLAIMS_COST': patient['TOTAL_CLAIMS_COST'],
                    'EMAIL': patient.get('EMAIL', ''),
                    'MEDICAL_CONDITIONS': []
                }
                
                # Add medical conditions
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
                
                # Generate predictions
                predictions = ai_model.predict_risk(patient_data)
                
                # Generate PDF
                pdf_path = self.generate_patient_pdf(patient_data, predictions, patient_id)
                
                if pdf_path:
                    generated_count += 1
                    print(f"✅ Generated PDF for patient {patient_id}")
                else:
                    print(f"❌ Failed to generate PDF for patient {patient_id}")
            
            print(f"🎉 Successfully generated {generated_count} PDF reports")
            return generated_count
            
        except Exception as e:
            print(f"❌ Error generating PDFs for all patients: {e}")
            return 0
    
    def get_patient_pdf_path(self, patient_id):
        """Get the PDF path for a specific patient"""
        try:
            # Look for existing PDF files for this patient
            existing_pdfs = [f for f in os.listdir(self.temp_folder) if f.startswith(f'patient_report_{patient_id}_')]
            
            if existing_pdfs:
                # Return the most recent one
                latest_pdf = sorted(existing_pdfs)[-1]
                return os.path.join(self.temp_folder, latest_pdf)
            else:
                return None
                
        except Exception as e:
            print(f"❌ Error getting PDF path for patient {patient_id}: {e}")
            return None
    
    def list_all_pdfs(self):
        """List all PDF files in temp folder"""
        try:
            pdf_files = [f for f in os.listdir(self.temp_folder) if f.endswith('.pdf')]
            return sorted(pdf_files)
        except Exception as e:
            print(f"❌ Error listing PDF files: {e}")
            return []

# Create global instance
pdf_generator = PatientPDFGenerator()
