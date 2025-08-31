#!/usr/bin/env python3
"""
Email Service for Sending Patient PDF Reports
Handles sending PDF reports from temp folder to patients
"""

import os
import requests
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

class PatientEmailService:
    """Email service for sending patient PDF reports"""
    
    def __init__(self, nodejs_url="http://localhost:3000"):
        self.nodejs_url = nodejs_url
        self.is_nodejs_available = self._check_nodejs_service()
    
    def _check_nodejs_service(self):
        """Check if Node.js email service is running"""
        try:
            response = requests.get(f"{self.nodejs_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def send_patient_pdf_email(self, patient_id, patient_email, patient_name=None):
        """Send PDF report to patient via email"""
        try:
            # Import PDF generator to get PDF path
            from pdf_generator import pdf_generator
            
            # Get PDF path for patient
            pdf_path = pdf_generator.get_patient_pdf_path(patient_id)
            
            if not pdf_path:
                return {
                    "success": False,
                    "error": f"PDF report not found for patient {patient_id}. Please generate the PDF first."
                }
            
            if not os.path.exists(pdf_path):
                return {
                    "success": False,
                    "error": f"PDF file not found at path: {pdf_path}"
                }
            
            # Try Node.js service first
            if self.is_nodejs_available:
                return self._send_via_nodejs(patient_id, patient_email, patient_name, pdf_path)
            else:
                # Fallback to direct SMTP
                return self._send_via_smtp(patient_id, patient_email, patient_name, pdf_path)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Email sending failed: {str(e)}"
            }
    
    def _send_via_nodejs(self, patient_id, patient_email, patient_name, pdf_path):
        """Send email via Node.js service"""
        try:
            url = f"{self.nodejs_url}/api/email/send-patient-report"
            
            # Prepare email data
            email_data = {
                "email": patient_email,
                "patientId": patient_id,
                "patientName": patient_name or f"Patient {patient_id}",
                "pdfPath": pdf_path
            }
            
            # Send request to Node.js service
            response = requests.post(url, json=email_data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    return {
                        "success": True,
                        "message": f"Email sent successfully to {patient_email} via Node.js service",
                        "messageId": result.get('messageId', 'Unknown')
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get('error', 'Unknown error from Node.js service')
                    }
            else:
                return {
                    "success": False,
                    "error": f"Node.js service error: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": f"Node.js service connection error: {str(e)}"
            }
    
    def _send_via_smtp(self, patient_id, patient_email, patient_name, pdf_path):
        """Send email via direct SMTP"""
        try:
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
                return {
                    "success": False,
                    "error": "Email not configured. Please update email_config_streamlit.py or set environment variables."
                }
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = patient_email
            msg['Subject'] = f"Your Health Risk Assessment Report - Patient ID: {patient_id}"
            
            # Email body
            body = f"""
Dear {patient_name or 'Patient'},

We are sending you your personalized Health Risk Assessment Report based on your recent medical evaluation.

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
            with open(pdf_path, 'rb') as f:
                pdf_attachment = MIMEBase('application', 'pdf')
                pdf_attachment.set_payload(f.read())
                encoders.encode_base64(pdf_attachment)
                pdf_attachment.add_header(
                    'Content-Disposition',
                    'attachment',
                    filename=os.path.basename(pdf_path)
                )
                msg.attach(pdf_attachment)
            
            # Send email
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, patient_email, text)
            server.quit()
            
            return {
                "success": True,
                "message": f"Email sent successfully to {patient_email} via direct SMTP",
                "messageId": f"SMTP_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"SMTP email sending failed: {str(e)}"
            }
    
    def send_bulk_pdf_emails(self, patients_data):
        """Send PDF emails to multiple patients"""
        results = {
            "successful": [],
            "failed": []
        }
        
        for patient_data in patients_data:
            patient_id = patient_data.get('patient_id')
            patient_email = patient_data.get('email')
            patient_name = patient_data.get('name')
            
            if not patient_id or not patient_email:
                results["failed"].append({
                    "patient": patient_data,
                    "error": "Missing patient ID or email"
                })
                continue
            
            # Send email
            result = self.send_patient_pdf_email(patient_id, patient_email, patient_name)
            
            if result.get('success', False):
                results["successful"].append({
                    "patient": patient_data,
                    "result": result
                })
            else:
                results["failed"].append({
                    "patient": patient_data,
                    "error": result.get('error', 'Unknown error')
                })
        
        return results
    
    def get_service_status(self):
        """Get email service status"""
        return {
            "nodejs_available": self.is_nodejs_available,
            "nodejs_url": self.nodejs_url,
            "temp_folder_exists": os.path.exists("temp")
        }

# Create global instance
email_service = PatientEmailService()
