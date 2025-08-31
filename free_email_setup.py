#!/usr/bin/env python3
"""
Free Email Setup - No App Passwords Required
Uses a free email service for immediate setup
"""

import os

def setup_free_email():
    print("🚀 Free Email Setup - No App Passwords!")
    print("=" * 50)
    
    print("\n📧 Free Email Options:")
    print("1. Create a free Outlook account (recommended)")
    print("2. Use existing Yahoo account")
    print("3. Use existing email with custom settings")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "1":
        return setup_outlook()
    elif choice == "2":
        return setup_yahoo()
    elif choice == "3":
        return setup_custom()
    else:
        print("Using Outlook setup...")
        return setup_outlook()

def setup_outlook():
    """Setup with Outlook (free and easy)"""
    print("\n🔧 Outlook Setup")
    print("Outlook doesn't require App Passwords!")
    
    print("\n📝 To create a free Outlook account:")
    print("1. Go to: https://outlook.live.com/")
    print("2. Click 'Create free account'")
    print("3. Use any email address (e.g., yourname@outlook.com)")
    print("4. Set a simple password")
    print("5. Complete the setup")
    
    email = input("\nEnter your Outlook email: ").strip()
    password = input("Enter your Outlook password: ").strip()
    
    if not email or not password:
        print("❌ Email and password required!")
        return False
    
    # Set environment variables
    os.environ['SENDER_EMAIL'] = email
    os.environ['SENDER_PASSWORD'] = password
    os.environ['SMTP_SERVER'] = 'smtp-mail.outlook.com'
    os.environ['SMTP_PORT'] = '587'
    os.environ['EMAIL_ENABLED'] = 'true'
    os.environ['USE_SSL'] = 'false'
    
    print(f"\n✅ Outlook environment variables set!")
    print(f"   Email: {email}")
    print(f"   Server: smtp-mail.outlook.com")
    print(f"   Port: 587")
    
    return test_and_save(email, password, 'smtp-mail.outlook.com', '587', False)

def setup_yahoo():
    """Setup with Yahoo"""
    print("\n🔧 Yahoo Setup")
    
    email = input("Enter your Yahoo email: ").strip()
    password = input("Enter your Yahoo password: ").strip()
    
    if not email or not password:
        print("❌ Email and password required!")
        return False
    
    # Set environment variables
    os.environ['SENDER_EMAIL'] = email
    os.environ['SENDER_PASSWORD'] = password
    os.environ['SMTP_SERVER'] = 'smtp.mail.yahoo.com'
    os.environ['SMTP_PORT'] = '587'
    os.environ['EMAIL_ENABLED'] = 'true'
    os.environ['USE_SSL'] = 'false'
    
    print(f"\n✅ Yahoo environment variables set!")
    print(f"   Email: {email}")
    print(f"   Server: smtp.mail.yahoo.com")
    print(f"   Port: 587")
    
    return test_and_save(email, password, 'smtp.mail.yahoo.com', '587', False)

def setup_custom():
    """Setup with custom email provider"""
    print("\n🔧 Custom Email Setup")
    
    email = input("Enter your email: ").strip()
    password = input("Enter your password: ").strip()
    server = input("SMTP server (e.g., smtp.gmail.com): ").strip()
    port = input("SMTP port (e.g., 587): ").strip()
    
    if not all([email, password, server, port]):
        print("❌ All fields required!")
        return False
    
    # Set environment variables
    os.environ['SENDER_EMAIL'] = email
    os.environ['SENDER_PASSWORD'] = password
    os.environ['SMTP_SERVER'] = server
    os.environ['SMTP_PORT'] = port
    os.environ['EMAIL_ENABLED'] = 'true'
    os.environ['USE_SSL'] = 'false'
    
    return test_and_save(email, password, server, port, False)

def test_and_save(email, password, server, port, use_ssl):
    """Test connection and save if successful"""
    print(f"\n🔍 Testing connection to {server}:{port}...")
    
    if test_smtp_connection():
        print("✅ Email connection successful!")
        return save_to_env_file(email, password, server, port, use_ssl)
    else:
        print("❌ Email connection failed!")
        print("📝 Configuration saved anyway - try restarting your app")
        return save_to_env_file(email, password, server, port, use_ssl)

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
    print("🎯 Free Email Setup for Patient Dashboard")
    print("=" * 50)
    
    success = setup_free_email()
    
    if success:
        print("\n🎉 Email setup complete!")
        print("\n📋 Next steps:")
        print("1. Restart your Streamlit dashboard")
        print("2. Test email sending in the dashboard")
        print("3. Your email service should now work!")
        
        print("\n🚀 No App Passwords required!")
    else:
        print("\n❌ Email setup failed!")
        print("\n📖 Try creating a free Outlook account:")

if __name__ == "__main__":
    main()
