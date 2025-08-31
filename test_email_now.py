#!/usr/bin/env python3
"""
Quick Email Test - Check Current Status
"""

import os
from email_config_streamlit import test_email_connection, is_email_configured

def quick_test():
    print("🔍 Quick Email Status Check")
    print("=" * 40)
    
    # Check current environment variables
    print("\n📧 Current Environment Variables:")
    print(f"   SENDER_EMAIL: {os.getenv('SENDER_EMAIL', 'Not set')}")
    print(f"   SENDER_PASSWORD: {'*' * len(os.getenv('SENDER_PASSWORD', '')) if os.getenv('SENDER_PASSWORD') else 'Not set'}")
    print(f"   SMTP_SERVER: {os.getenv('SMTP_SERVER', 'Not set')}")
    print(f"   SMTP_PORT: {os.getenv('SMTP_PORT', 'Not set')}")
    
    # Check if configured
    print(f"\n⚙️ Configuration Status:")
    configured = is_email_configured()
    print(f"   Email Configured: {'✅ Yes' if configured else '❌ No'}")
    
    if configured:
        print("\n🔍 Testing Connection...")
        result = test_email_connection()
        
        if result.get('success', False):
            print("✅ Email connection successful!")
            print(f"   Server: {result.get('server')}")
            print(f"   Port: {result.get('port')}")
        else:
            print(f"❌ Connection failed: {result.get('error')}")
            if result.get('details'):
                print(f"   Details: {result.get('details')}")
    else:
        print("\n❌ Email not configured!")
        print("📖 Please set up your Gmail App Password")

if __name__ == "__main__":
    quick_test()
