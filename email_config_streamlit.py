#!/usr/bin/env python3
"""
Email Configuration for Streamlit Dashboard
Provides both Node.js and direct SMTP email services
"""

import os
import requests
from datetime import datetime

# Try to load email credentials from email_credentials.py first
try:
    from email_credentials import setup_email_environment
    setup_email_environment()
except ImportError:
    pass  # File doesn't exist, use environment variables

# Gmail SMTP Configuration (for direct email sending)
SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'your-email@gmail.com')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', 'your-app-password')
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
USE_SSL = os.getenv('USE_SSL', 'false').lower() == 'true'

# Node.js Email Service Configuration
NODEJS_URL = os.getenv("NODEJS_EMAIL_URL", "http://localhost:3000")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "true").lower() == "true"

# Email Configuration Dictionary
EMAIL_CONFIG = {
    "SENDER_EMAIL": SENDER_EMAIL,
    "SENDER_PASSWORD": SENDER_PASSWORD,
    "SMTP_SERVER": SMTP_SERVER,
    "SMTP_PORT": SMTP_PORT,
    "NODEJS_URL": NODEJS_URL,
    "ENABLED": EMAIL_ENABLED
}

def is_email_configured():
    """Check if email is properly configured"""
    # Check if SMTP credentials are set (not default values)
    smtp_configured = (
        SENDER_EMAIL != "your-email@gmail.com" and 
        SENDER_PASSWORD != "your-app-password" and
        SENDER_EMAIL and SENDER_PASSWORD
    )
    
    return smtp_configured

def get_email_config_status():
    """Get detailed email configuration status"""
    smtp_configured = is_email_configured()
    
    status = {
        "smtp_configured": smtp_configured,
        "smtp_server": SMTP_SERVER,
        "smtp_port": SMTP_PORT,
        "sender_email": SENDER_EMAIL if smtp_configured else "Not configured",
        "nodejs_url": NODEJS_URL,
        "email_enabled": EMAIL_ENABLED
    }
    
    if not smtp_configured:
        status["error"] = "SMTP credentials not configured. Please set SENDER_EMAIL and SENDER_PASSWORD environment variables."
    
    return status

def test_email_connection():
    """Test email connection and return detailed status"""
    if not is_email_configured():
        return {
            "success": False,
            "error": "Email not configured. Please set SENDER_EMAIL and SENDER_PASSWORD environment variables.",
            "details": "Use Gmail App Password for authentication"
        }
    
    try:
        import smtplib
        if USE_SSL:
            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        else:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.quit()
        
        return {
            "success": True,
            "message": "SMTP connection successful",
            "server": SMTP_SERVER,
            "port": SMTP_PORT
        }
    except smtplib.SMTPAuthenticationError:
        return {
            "success": False,
            "error": "SMTP Authentication failed",
            "details": "Please check your email and app password. Make sure 2-factor authentication is enabled and you're using an App Password."
        }
    except smtplib.SMTPConnectError:
        return {
            "success": False,
            "error": "SMTP Connection failed",
            "details": f"Cannot connect to {SMTP_SERVER}:{SMTP_PORT}. Check your internet connection and firewall settings."
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"SMTP Error: {str(e)}",
            "details": "Unexpected error during SMTP connection test"
        }

class StreamlitEmailService:
    """Enhanced email service with better error handling"""
    
    def __init__(self, nodejs_url="http://localhost:3000"):
        self.nodejs_url = nodejs_url
        self.smtp_configured = is_email_configured()
        self.nodejs_available = self._check_nodejs_service()
    
    def _check_nodejs_service(self):
        """Check if Node.js email service is running"""
        try:
            response = requests.get(f"{self.nodejs_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def send_patient_email(self, patient_data, patient_id, pdf_path=None):
        """Send email for a patient with enhanced error handling"""
        
        # Check if we have any email service available
        if not self.smtp_configured and not self.nodejs_available:
            return {
                "success": False,
                "error": "No email service available. Please configure SMTP credentials or start Node.js email service.",
                "details": "Set SENDER_EMAIL and SENDER_PASSWORD environment variables for SMTP, or start Node.js service on localhost:3000"
            }
        
        # Always try SMTP first (more reliable and direct)
        if self.smtp_configured:
            result = self._send_via_smtp(patient_data, patient_id, pdf_path)
            if result.get("success", False):
                return result
            else:
                # If SMTP fails, try Node.js as fallback only if available
                if self.nodejs_available:
                    print(f"⚠️ SMTP failed, trying Node.js fallback...")
                    return self._send_via_nodejs(patient_data, patient_id, pdf_path)
                else:
                    return result
        
        # If SMTP not configured, try Node.js
        elif self.nodejs_available:
            print(f"⚠️ SMTP not configured, using Node.js service...")
            return self._send_via_nodejs(patient_data, patient_id, pdf_path)
        
        return {
            "success": False,
            "error": "No email service available"
        }
    
    def _send_via_smtp(self, patient_data, patient_id, pdf_path):
        """Send email via direct SMTP with detailed error handling"""
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            from email.mime.base import MIMEBase
            from email import encoders
            
            # Get patient email
            patient_email = patient_data.get('EMAIL', '')
            if not patient_email:
                return {
                    "success": False,
                    "error": "No email address provided for patient"
                }
            
            # Find PDF file if not provided
            if not pdf_path:
                try:
                    from pdf_generator import pdf_generator
                    pdf_path = pdf_generator.get_patient_pdf_path(patient_id)
                    if not pdf_path:
                        return {
                            "success": False,
                            "error": f"PDF report not found for patient {patient_id}",
                            "details": "Please generate the PDF report first"
                        }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Could not find PDF for patient {patient_id}",
                        "details": str(e)
                    }
            
            # Check if PDF exists
            if not os.path.exists(pdf_path):
                return {
                    "success": False,
                    "error": f"PDF file not found at path: {pdf_path}",
                    "details": "Please ensure the PDF was generated correctly"
                }
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = patient_email
            msg['Subject'] = f"Your Health Risk Assessment Report - Patient ID: {patient_id}"
            
            # Email body
            body = f"""
Dear Patient,

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
            try:
                with open(pdf_path, 'rb') as f:
                    pdf_attachment = MIMEBase('application', 'pdf')
                    pdf_attachment.set_payload(f.read())
                    encoders.encode_base64(pdf_attachment)
                    pdf_attachment.add_header(
                        'Content-Disposition',
                        'attachment',
                        filename=f"patient_report_{patient_id}.pdf"
                    )
                    msg.attach(pdf_attachment)
                print(f"✅ PDF attached: {pdf_path}")
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Could not attach PDF file: {str(e)}",
                    "details": f"PDF path: {pdf_path}"
                }
            
            # Send email
            if USE_SSL:
                server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
            else:
                server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            text = msg.as_string()
            server.sendmail(SENDER_EMAIL, patient_email, text)
            server.quit()
            
            return {
                "success": True,
                "message": f"Email sent successfully to {patient_email} via SMTP",
                "method": "SMTP",
                "messageId": f"SMTP_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "pdf_attached": os.path.basename(pdf_path)
            }
            
        except smtplib.SMTPAuthenticationError:
            return {
                "success": False,
                "error": "SMTP Authentication failed",
                "details": "Please check your email and app password. Make sure 2-factor authentication is enabled and you're using an App Password."
            }
        except smtplib.SMTPConnectError:
            return {
                "success": False,
                "error": "SMTP Connection failed",
                "details": f"Cannot connect to {SMTP_SERVER}:{SMTP_PORT}. Check your internet connection and firewall settings."
            }
        except smtplib.SMTPRecipientsRefused:
            return {
                "success": False,
                "error": "Invalid recipient email address",
                "details": f"The email address '{patient_email}' is not valid or rejected by the server."
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"SMTP Error: {str(e)}",
                "details": "Unexpected error during email sending"
            }
    
    def _send_via_nodejs(self, patient_data, patient_id, pdf_path):
        """Send email via Node.js service"""
        try:
            url = f"{self.nodejs_url}/api/email/send-patient-report"
            
            # Prepare email data
            email_data = {
                "email": patient_data.get('EMAIL', ''),
                "patientId": patient_id,
                "patientName": f"Patient {patient_id}",
                "pdfPath": pdf_path or f"./temp/patient_report_{patient_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
            }
            
            # Send request to Node.js service
            response = requests.post(url, json=email_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success', False):
                    return {
                        "success": True,
                        "message": f"Email sent successfully via Node.js service",
                        "method": "Node.js",
                        "messageId": result.get('messageId', 'Unknown')
                    }
                else:
                    return {
                        "success": False,
                        "error": result.get('error', 'Unknown error from Node.js service'),
                        "method": "Node.js"
                    }
            else:
                return {
                    "success": False,
                    "error": f"Node.js service error: {response.status_code}",
                    "details": f"Service returned status code {response.status_code}",
                    "method": "Node.js"
                }
                
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "error": "Cannot connect to Node.js email service",
                "details": f"Service not running at {self.nodejs_url}",
                "method": "Node.js"
            }
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "Node.js email service timeout",
                "details": "Service took too long to respond",
                "method": "Node.js"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Node.js service error: {str(e)}",
                "method": "Node.js"
            }
    
    def get_status(self):
        """Get comprehensive email service status"""
        smtp_status = test_email_connection()
        nodejs_status = "Available" if self.nodejs_available else "Not available"
        
        return {
            "smtp_configured": self.smtp_configured,
            "smtp_status": smtp_status,
            "nodejs_available": self.nodejs_available,
            "nodejs_status": nodejs_status,
            "nodejs_url": self.nodejs_url,
            "email_enabled": EMAIL_ENABLED
        }

# Create global instance
email_service = StreamlitEmailService()

def is_email_enabled():
    """Check if email functionality is enabled"""
    return EMAIL_CONFIG["ENABLED"] and (is_email_configured() or email_service.nodejs_available)

def get_email_status():
    """Get current email service status"""
    return email_service.get_status()

def send_patient_email_wrapper(patient_data, patient_id, pdf_path=None):
    """Wrapper function to send patient email"""
    if not is_email_enabled():
        return {
            "success": False,
            "error": "Email not configured. Please set SENDER_EMAIL and SENDER_PASSWORD environment variables.",
            "details": "For Gmail: Enable 2-factor authentication and generate an App Password"
        }
    
    return email_service.send_patient_email(patient_data, patient_id, pdf_path)
