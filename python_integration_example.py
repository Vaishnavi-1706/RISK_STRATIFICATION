#!/usr/bin/env python3
"""
Python Integration Example for Node.js Email Service
Demonstrates how to call the Node.js email API from Python
"""

import requests
import json
import os
from datetime import datetime

class NodeJSEmailService:
    """Python wrapper for Node.js Email Service"""
    
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        
    def check_health(self):
        """Check if the Node.js email service is running"""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Service not available: {str(e)}"}
    
    def get_email_status(self):
        """Get email service status"""
        try:
            response = requests.get(f"{self.base_url}/api/email/status")
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to get status: {str(e)}"}
    
    def test_email_connection(self):
        """Test email service connection"""
        try:
            response = requests.post(f"{self.base_url}/api/email/test-connection")
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to test connection: {str(e)}"}
    
    def send_invoice_email(self, email, patient_id, patient_data=None):
        """Send invoice email with PDF attachment"""
        try:
            url = f"{self.base_url}/api/email/send-invoice"
            data = {
                "email": email,
                "patientId": patient_id,
                "patientData": patient_data or {}
            }
            
            response = requests.post(url, json=data)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to send invoice: {str(e)}"}
    
    def send_patient_report(self, email, patient_id, patient_name, pdf_path):
        """Send patient risk assessment report"""
        try:
            url = f"{self.base_url}/api/email/send-patient-report"
            data = {
                "email": email,
                "patientId": patient_id,
                "patientName": patient_name,
                "pdfPath": pdf_path
            }
            
            response = requests.post(url, json=data)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to send patient report: {str(e)}"}
    
    def send_bulk_reports(self, patients):
        """Send bulk patient reports"""
        try:
            url = f"{self.base_url}/api/email/send-bulk-reports"
            data = {"patients": patients}
            
            response = requests.post(url, json=data)
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to send bulk reports: {str(e)}"}
    
    def list_pdf_files(self):
        """List all PDF files in storage"""
        try:
            response = requests.get(f"{self.base_url}/api/email/pdf-files")
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to list PDF files: {str(e)}"}

def test_nodejs_email_service():
    """Test the Node.js email service integration"""
    print("🧪 Testing Node.js Email Service Integration\n")
    
    # Initialize the service
    email_service = NodeJSEmailService()
    
    # Test 1: Health Check
    print("1️⃣ Testing Health Check...")
    health = email_service.check_health()
    print(f"✅ Health Check: {health}")
    print()
    
    # Test 2: Email Status
    print("2️⃣ Testing Email Status...")
    status = email_service.get_email_status()
    print(f"✅ Email Status: {status}")
    print()
    
    # Test 3: Test Connection
    print("3️⃣ Testing Email Connection...")
    connection = email_service.test_email_connection()
    print(f"✅ Email Connection: {connection}")
    print()
    
    # Test 4: Send Invoice Email
    print("4️⃣ Testing Send Invoice Email...")
    invoice_data = {
        "name": "John Doe",
        "age": 45,
        "gender": "Male",
        "bmi": 25.5,
        "bloodPressure": "120/80",
        "glucose": 95,
        "cholesterol": 180,
        "risk30d": 25,
        "risk60d": 30,
        "risk90d": 35,
        "riskLabel": "Low Risk",
        "recommendations": "Continue preventive care routine | Annual wellness visit recommended",
        "conditions": "None reported"
    }
    
    invoice_result = email_service.send_invoice_email(
        email="test@example.com",
        patient_id="TEST001",
        patient_data=invoice_data
    )
    print(f"✅ Send Invoice: {invoice_result}")
    print()
    
    # Test 5: List PDF Files
    print("5️⃣ Testing List PDF Files...")
    pdf_files = email_service.list_pdf_files()
    print(f"✅ PDF Files: {pdf_files}")
    print()
    
    # Test 6: Send Patient Report
    print("6️⃣ Testing Send Patient Report...")
    patient_report = email_service.send_patient_report(
        email="patient@example.com",
        patient_id="PATIENT001",
        patient_name="Jane Smith",
        pdf_path="./pdfs/patient_risk_assessment_TEST001_2025-08-31.pdf"
    )
    print(f"✅ Send Patient Report: {patient_report}")
    print()
    
    # Test 7: Send Bulk Reports
    print("7️⃣ Testing Send Bulk Reports...")
    bulk_patients = [
        {
            "email": "patient1@example.com",
            "name": "Patient One",
            "id": "PAT001",
            "pdfPath": "./pdfs/patient_risk_assessment_PAT001_2025-08-31.pdf"
        },
        {
            "email": "patient2@example.com",
            "name": "Patient Two",
            "id": "PAT002",
            "pdfPath": "./pdfs/patient_risk_assessment_PAT002_2025-08-31.pdf"
        }
    ]
    
    bulk_result = email_service.send_bulk_reports(bulk_patients)
    print(f"✅ Send Bulk Reports: {bulk_result}")
    print()
    
    print("🎉 All integration tests completed!")

def integrate_with_streamlit_dashboard():
    """Example integration with Streamlit dashboard"""
    
    # This function shows how to integrate with your existing Streamlit dashboard
    
    def send_patient_email_from_dashboard(patient_data, predictions, patient_id):
        """Send email when patient is saved in Streamlit dashboard"""
        email_service = NodeJSEmailService()
        
        # Generate PDF path (assuming PDF is already created)
        pdf_path = f"./pdfs/patient_risk_assessment_{patient_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        # Send patient report
        result = email_service.send_patient_report(
            email=patient_data.get('EMAIL', ''),
            patient_id=patient_id,
            patient_name=f"Patient {patient_id}",
            pdf_path=pdf_path
        )
        
        return result
    
    def send_bulk_emails_from_dashboard(patients_with_emails):
        """Send bulk emails from dashboard"""
        email_service = NodeJSEmailService()
        
        # Prepare patients data
        patients = []
        for patient in patients_with_emails:
            if patient.get('EMAIL'):
                patients.append({
                    "email": patient['EMAIL'],
                    "name": f"Patient {patient['DESYNPUF_ID']}",
                    "id": patient['DESYNPUF_ID'],
                    "pdfPath": f"./pdfs/patient_risk_assessment_{patient['DESYNPUF_ID']}_{datetime.now().strftime('%Y%m%d')}.pdf"
                })
        
        # Send bulk reports
        result = email_service.send_bulk_reports(patients)
        return result
    
    return {
        "send_patient_email": send_patient_email_from_dashboard,
        "send_bulk_emails": send_bulk_emails_from_dashboard
    }

if __name__ == "__main__":
    # Run the integration tests
    test_nodejs_email_service()
    
    # Example usage
    print("\n" + "="*50)
    print("📋 Example Usage:")
    print("="*50)
    
    email_service = NodeJSEmailService()
    
    # Example 1: Send invoice email
    print("\n📧 Example 1: Send Invoice Email")
    result = email_service.send_invoice_email(
        email="your-email@gmail.com",
        patient_id="PATIENT123",
        patient_data={"name": "John Doe", "age": 45}
    )
    print(f"Result: {result}")
    
    # Example 2: Send patient report
    print("\n📧 Example 2: Send Patient Report")
    result = email_service.send_patient_report(
        email="patient@example.com",
        patient_id="PATIENT123",
        patient_name="John Doe",
        pdf_path="./pdfs/patient_report.pdf"
    )
    print(f"Result: {result}")
    
    # Example 3: Integration with Streamlit
    print("\n📧 Example 3: Streamlit Integration")
    integration = integrate_with_streamlit_dashboard()
    print("Functions available:")
    print("- integration['send_patient_email'](patient_data, predictions, patient_id)")
    print("- integration['send_bulk_emails'](patients_with_emails)")
