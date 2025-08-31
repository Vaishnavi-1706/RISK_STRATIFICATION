#!/usr/bin/env python3
"""
Set Email Environment Variables
Helps you set email credentials as environment variables
"""

import os

def set_email_environment():
    """Set email environment variables"""
    print("🔧 Setting Email Environment Variables")
    print("=" * 50)
    
    # Get email credentials from user
    print("\n📧 Enter your email credentials:")
    
    email = input("Gmail address: ").strip()
    if not email:
        email = "healthcarereports0@gmail.com"
        print(f"Using default: {email}")
    
    print("\n🔐 For Gmail, you need an App Password:")
    print("1. Enable 2-Factor Authentication on your Google Account")
    print("2. Go to Security → App passwords")
    print("3. Generate a password for 'Mail'")
    print("4. Use the 16-character password (NOT your regular password)")
    
    password = input("App Password (16 characters): ").strip()
    
    if not password:
        print("❌ App Password is required!")
        return False
    
    # Set environment variables
    os.environ['SENDER_EMAIL'] = email
    os.environ['SENDER_PASSWORD'] = password
    os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
    os.environ['SMTP_PORT'] = '587'
    os.environ['EMAIL_ENABLED'] = 'true'
    
    print(f"\n✅ Environment variables set!")
    print(f"   Email: {email}")
    print(f"   Server: smtp.gmail.com")
    print(f"   Port: 587")
    
    # Test the configuration
    print(f"\n🔍 Testing email connection...")
    
    try:
        from email_config_streamlit import test_email_connection
        result = test_email_connection()
        
        if result.get('success', False):
            print("✅ Email connection successful!")
            print(f"   Server: {result.get('server')}")
            print(f"   Port: {result.get('port')}")
            
            # Save to .env file
            save_to_env_file(email, password)
            
            return True
        else:
            print(f"❌ Email connection failed: {result.get('error')}")
            if result.get('details'):
                print(f"   Details: {result.get('details')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

def save_to_env_file(email, password):
    """Save credentials to .env file"""
    try:
        env_content = f"""# Email Configuration
SENDER_EMAIL={email}
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
    """Main function"""
    print("🎯 Email Environment Setup")
    print("=" * 50)
    
    success = set_email_environment()
    
    if success:
        print("\n🎉 Email environment setup complete!")
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
        print("1. Email address is correct")
        print("2. App Password is correct (16 characters)")
        print("3. 2-Factor Authentication is enabled")
        print("4. Internet connection is working")
        
        print("\n📚 For detailed instructions, see GMAIL_SETUP_GUIDE.md")

if __name__ == "__main__":
    main()
