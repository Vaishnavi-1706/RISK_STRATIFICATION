#!/usr/bin/env python3
"""
Quick Email Setup - Simple Environment Variable Setup
"""

import os

def setup_email():
    print("🔧 Quick Email Setup")
    print("=" * 50)
    
    print("\n📧 To fix your email issue, you need a real Gmail App Password.")
    print("\n🔐 Here's how to get it:")
    print("1. Go to: https://myaccount.google.com/")
    print("2. Sign in with: healthcarereports0@gmail.com")
    print("3. Go to Security → 2-Step Verification → Get started")
    print("4. Enable 2-Factor Authentication")
    print("5. Go to Security → App passwords")
    print("6. Select 'Mail' → Generate")
    print("7. Copy the 16-character password")
    
    print("\n📝 Once you have your App Password, enter it below:")
    
    # Get the real App Password
    password = input("\nEnter your real Gmail App Password (16 characters): ").strip()
    
    if not password or len(password) < 16:
        print("❌ Please enter a valid 16-character App Password!")
        return False
    
    # Set environment variables
    os.environ['SENDER_EMAIL'] = 'healthcarereports0@gmail.com'
    os.environ['SENDER_PASSWORD'] = password
    os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
    os.environ['SMTP_PORT'] = '587'
    os.environ['EMAIL_ENABLED'] = 'true'
    
    print("\n✅ Environment variables set!")
    print(f"   Email: healthcarereports0@gmail.com")
    print(f"   Server: smtp.gmail.com")
    print(f"   Port: 587")
    
    # Test the connection
    print("\n🔍 Testing email connection...")
    
    try:
        from email_config_streamlit import test_email_connection
        result = test_email_connection()
        
        if result.get('success', False):
            print("✅ Email connection successful!")
            print("🎉 Your email service is now working!")
            
            # Save to .env file
            save_to_env_file(password)
            
            return True
        else:
            print(f"❌ Email connection failed: {result.get('error')}")
            if result.get('details'):
                print(f"   Details: {result.get('details')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

def save_to_env_file(password):
    """Save credentials to .env file"""
    try:
        env_content = f"""# Email Configuration
SENDER_EMAIL=healthcarereports0@gmail.com
SENDER_PASSWORD={password}
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ENABLED=true
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Credentials saved to .env file")
        print("📝 You can now restart your application to use these settings")
        
    except Exception as e:
        print(f"⚠️ Could not save to .env file: {e}")

def main():
    print("🎯 Quick Email Setup for Patient Dashboard")
    print("=" * 50)
    
    success = setup_email()
    
    if success:
        print("\n🎉 Email setup complete!")
        print("\n📋 Next steps:")
        print("1. Restart your Streamlit dashboard")
        print("2. Go to '📊 Dashboard' tab")
        print("3. Expand '⚙️ Email Configuration'")
        print("4. Click '🔍 Test Email Connection'")
        print("5. Try sending a test email to a patient")
        
        print("\n🚀 Your email service is ready to use!")
    else:
        print("\n❌ Email setup failed!")
        print("\n📖 Please check:")
        print("1. You entered a real Gmail App Password (16 characters)")
        print("2. 2-Factor Authentication is enabled on your Google Account")
        print("3. The App Password was generated for 'Mail'")
        print("4. Your internet connection is working")

if __name__ == "__main__":
    main()
