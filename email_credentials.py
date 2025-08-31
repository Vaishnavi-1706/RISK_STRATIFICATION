#!/usr/bin/env python3
"""
Email Credentials Configuration
Set your email credentials here for the patient dashboard
"""

import os

# =============================================================================
# EMAIL CREDENTIALS - UPDATE THESE WITH YOUR ACTUAL CREDENTIALS
# =============================================================================

# Your Gmail address
SENDER_EMAIL = "stratificationcts@gmail.com"

# Your Gmail App Password (16 characters)
# To get this:
# 1. Go to https://myaccount.google.com/
# 2. Enable 2-Factor Authentication
# 3. Generate a password for 'Mail'
# 4. Use the 16-character password (NOT your regular password)
# Example: "abcd efgh ijkl mnop" (16 characters with spaces)
SENDER_PASSWORD = "onopeqnptrjxvdif"

# SMTP Settings (usually don't need to change these)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def setup_email_environment():
    """Set email environment variables"""
    os.environ['SENDER_EMAIL'] = SENDER_EMAIL
    os.environ['SENDER_PASSWORD'] = SENDER_PASSWORD
    os.environ['SMTP_SERVER'] = SMTP_SERVER
    os.environ['SMTP_PORT'] = str(SMTP_PORT)
    os.environ['EMAIL_ENABLED'] = 'true'
    os.environ['USE_SSL'] = 'false'
    
    print(f"✅ Email environment configured:")
    print(f"   Email: {SENDER_EMAIL}")
    print(f"   Server: {SMTP_SERVER}")
    print(f"   Port: {SMTP_PORT}")

def test_configuration():
    """Test if credentials are properly configured"""
    if SENDER_PASSWORD == "your-16-character-app-password-here":
        print("❌ Please edit this file and set your actual Gmail App Password!")
        return False
    else:
        print("✅ Email credentials are configured")
        return True

if __name__ == "__main__":
    setup_email_environment()
    test_configuration()
