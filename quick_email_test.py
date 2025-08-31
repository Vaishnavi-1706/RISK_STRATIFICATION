#!/usr/bin/env python3
"""
Quick Email Test Script
Tests email configuration and sends a test email
"""

import os
from email_config_streamlit import test_email_connection, send_patient_email_wrapper

def quick_email_test():
    """Quick test of email configuration and sending"""
    print("🚀 Quick Email Test")
    print("=" * 40)
    
    # Test 1: Check configuration
    print("\n1. Testing email configuration...")
    result = test_email_connection()
    
    if result.get('success', False):
        print("✅ Email configuration successful!")
        print(f"   Server: {result.get('server')}")
        print(f"   Port: {result.get('port')}")
    else:
        print(f"❌ Email configuration failed: {result.get('error')}")
        if result.get('details'):
            print(f"   Details: {result.get('details')}")
        print("\n📖 Please follow GMAIL_SETUP_GUIDE.md to configure your email")
        return False
    
    # Test 2: Send test email
    print("\n2. Sending test email...")
    
    test_patient_data = {
        'EMAIL': 'test@example.com',
        'DESYNPUF_ID': 'TEST001'
    }
    
    print("   Sending to: test@example.com")
    email_result = send_patient_email_wrapper(test_patient_data, 'TEST001')
    
    if email_result.get('success', False):
        print("✅ Test email sent successfully!")
        print(f"   Method: {email_result.get('method', 'Unknown')}")
        print(f"   Message ID: {email_result.get('messageId', 'Unknown')}")
        if email_result.get('pdf_attached'):
            print(f"   PDF attached: {email_result.get('pdf_attached')}")
    else:
        print(f"❌ Test email failed: {email_result.get('error')}")
        if email_result.get('details'):
            print(f"   Details: {email_result.get('details')}")
        return False
    
    print("\n🎉 Email service is working perfectly!")
    print("📧 You can now send PDF reports to patients in your dashboard!")
    
    return True

if __name__ == "__main__":
    success = quick_email_test()
    
    if success:
        print("\n✅ All tests passed! Your email service is ready.")
    else:
        print("\n❌ Email setup needs attention. Please check the configuration.")
