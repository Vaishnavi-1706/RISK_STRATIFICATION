#!/usr/bin/env python3
"""
Test Email Configuration
Verifies email setup and functionality
"""

import os
from email_config_streamlit import (
    get_email_config_status, 
    test_email_connection, 
    send_patient_email_wrapper
)

def test_email_configuration():
    """Test email configuration and connection"""
    print("🔍 Testing Email Configuration...")
    print("=" * 50)
    
    # Test 1: Check configuration status
    print("\n1. Configuration Status:")
    config_status = get_email_config_status()
    
    print(f"   SMTP Server: {config_status['smtp_server']}")
    print(f"   SMTP Port: {config_status['smtp_port']}")
    print(f"   Sender Email: {config_status['sender_email']}")
    print(f"   Email Enabled: {config_status['email_enabled']}")
    
    if config_status.get('error'):
        print(f"   ❌ Error: {config_status['error']}")
    else:
        print("   ✅ Configuration found")
    
    # Test 2: Test connection
    print("\n2. Connection Test:")
    connection_result = test_email_connection()
    
    if connection_result.get('success', False):
        print("   ✅ Connection successful!")
        print(f"   Server: {connection_result.get('server')}")
        print(f"   Port: {connection_result.get('port')}")
    else:
        print(f"   ❌ Connection failed: {connection_result.get('error')}")
        if connection_result.get('details'):
            print(f"   Details: {connection_result.get('details')}")
    
    # Test 3: Test email sending (if configured)
    if config_status.get('smtp_configured', False):
        print("\n3. Email Sending Test:")
        
        # Test data
        test_patient_data = {
            'EMAIL': 'test@example.com',
            'DESYNPUF_ID': 'TEST001'
        }
        
        print("   Sending test email to test@example.com...")
        result = send_patient_email_wrapper(test_patient_data, 'TEST001')
        
        if result.get('success', False):
            print("   ✅ Email sent successfully!")
            print(f"   Method: {result.get('method', 'Unknown')}")
            print(f"   Message ID: {result.get('messageId', 'Unknown')}")
        else:
            print(f"   ❌ Email sending failed: {result.get('error')}")
            if result.get('details'):
                print(f"   Details: {result.get('details')}")
    else:
        print("\n3. Email Sending Test:")
        print("   ⚠️ Skipped - Email not configured")
    
    # Test 4: Environment variables
    print("\n4. Environment Variables:")
    env_vars = ['SENDER_EMAIL', 'SENDER_PASSWORD', 'SMTP_SERVER', 'SMTP_PORT']
    
    for var in env_vars:
        value = os.getenv(var, 'Not set')
        if var == 'SENDER_PASSWORD' and value != 'Not set':
            value = '*' * len(value)  # Hide password
        print(f"   {var}: {value}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Complete!")
    
    # Summary
    if connection_result.get('success', False):
        print("✅ Email service is ready to use!")
        print("📧 You can now send PDF reports to patients.")
    else:
        print("❌ Email service needs configuration.")
        print("📖 Please follow the EMAIL_SETUP_GUIDE.md for setup instructions.")

if __name__ == "__main__":
    test_email_configuration()
