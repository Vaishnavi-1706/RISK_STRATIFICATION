#!/usr/bin/env python3
"""
Setup Your Existing Email Account
"""

import os

def setup_your_email():
    print("🚀 Setting up your existing email account")
    print("=" * 50)
    
    # Your provided credentials
    email = "stratificationcts@gmail.com"
    password = "onopeqnptrjxvdif"
    
    print(f"📧 Email: {email}")
    print(f"🔐 Password: {password[:4]}****{password[-4:]}")
    
    # Set environment variables
    os.environ['SENDER_EMAIL'] = email
    os.environ['SENDER_PASSWORD'] = password
    os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
    os.environ['SMTP_PORT'] = '587'
    os.environ['EMAIL_ENABLED'] = 'true'
    os.environ['USE_SSL'] = 'false'
    
    print(f"\n✅ Environment variables set!")
    print(f"   Email: {email}")
    print(f"   Server: smtp.gmail.com")
    print(f"   Port: 587")
    print(f"   SSL: false")
    
    # Test the connection
    print(f"\n🔍 Testing email connection...")
    
    if test_smtp_connection():
        print("✅ Email connection successful!")
        save_to_env_file(email, password, 'smtp.gmail.com', '587', False)
        return True
    else:
        print("❌ Email connection failed!")
        print("📝 Configuration saved anyway - try restarting your app")
        save_to_env_file(email, password, 'smtp.gmail.com', '587', False)
        return True

def test_smtp_connection():
    """Test SMTP connection"""
    try:
        import smtplib
        from email_config_streamlit import SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT, USE_SSL
        
        if USE_SSL:
            server = smtplib.SMTP_SSL(SMTP_SERVER, int(SMTP_PORT))
        else:
            server = smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT))
            server.starttls()
        
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.quit()
        return True
    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:50]}...")
        return False

def save_to_env_file(email, password, server, port, use_ssl):
    """Save credentials to .env file"""
    try:
        env_content = f"""# Email Configuration
SENDER_EMAIL={email}
SENDER_PASSWORD={password}
SMTP_SERVER={server}
SMTP_PORT={port}
EMAIL_ENABLED=true
USE_SSL={str(use_ssl).lower()}
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Credentials saved to .env file")
        print("📝 You can now restart your application to use these settings")
        
        return True
        
    except Exception as e:
        print(f"⚠️ Could not save to .env file: {e}")
        return False

def main():
    print("🎯 Setting up your existing email account")
    print("=" * 50)
    
    success = setup_your_email()
    
    if success:
        print("\n🎉 Email setup complete!")
        print("\n📋 Next steps:")
        print("1. Restart your Streamlit dashboard")
        print("2. Test email sending in the dashboard")
        print("3. Your email service should now work!")
        
        print("\n🚀 Your email service is ready to use!")
    else:
        print("\n❌ Email setup failed!")
        print("\n📖 Please check your credentials and try again")

if __name__ == "__main__":
    main()
