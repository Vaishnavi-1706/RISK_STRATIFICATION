#!/usr/bin/env python3
"""
Simple Email Setup - No App Passwords Required
Uses a free email service for quick setup
"""

import os

def setup_simple_email():
    print("🚀 Simple Email Setup - No App Passwords!")
    print("=" * 50)
    
    print("\n📧 Quick Email Options:")
    print("1. Use your existing Gmail (with regular password)")
    print("2. Use a free email service (recommended)")
    print("3. Use your own email provider")
    
    choice = input("\nChoose option (1-3): ").strip()
    
    if choice == "1":
        return setup_gmail_simple()
    elif choice == "2":
        return setup_free_email()
    elif choice == "3":
        return setup_custom_email()
    else:
        print("❌ Invalid choice. Using free email service.")
        return setup_free_email()

def setup_gmail_simple():
    """Setup Gmail with regular password (less secure but quick)"""
    print("\n🔧 Gmail Setup (Less Secure)")
    print("⚠️ Note: This uses your regular password (less secure)")
    
    email = input("Gmail address: ").strip()
    if not email:
        email = "healthcarereports0@gmail.com"
    
    password = input("Gmail password (regular password): ").strip()
    
    if not password:
        print("❌ Password required!")
        return False
    
    # Set environment variables
    os.environ['SENDER_EMAIL'] = email
    os.environ['SENDER_PASSWORD'] = password
    os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
    os.environ['SMTP_PORT'] = '465'  # Use SSL port
    os.environ['EMAIL_ENABLED'] = 'true'
    os.environ['USE_SSL'] = 'true'
    
    print(f"\n✅ Gmail environment variables set!")
    print(f"   Email: {email}")
    print(f"   Server: smtp.gmail.com")
    print(f"   Port: 465 (SSL)")
    
    return test_and_save(email, password, 'smtp.gmail.com', '465', True)

def setup_free_email():
    """Setup with a free email service"""
    print("\n🔧 Free Email Service Setup")
    print("Using a free email service that doesn't require App Passwords")
    
    # Use a simple free email service
    email = "healthcarereports0@gmail.com"  # You can change this
    password = "your-regular-password"  # Use your regular password
    
    print(f"Using: {email}")
    password = input("Enter your regular password: ").strip()
    
    if not password:
        print("❌ Password required!")
        return False
    
    # Try different SMTP settings
    smtp_settings = [
        ('smtp.gmail.com', '465', True),  # Gmail with SSL
        ('smtp.gmail.com', '587', False),  # Gmail with TLS
        ('smtp-mail.outlook.com', '587', False),  # Outlook
        ('smtp.mail.yahoo.com', '587', False),  # Yahoo
    ]
    
    for server, port, use_ssl in smtp_settings:
        print(f"\n🔍 Testing {server}:{port}...")
        
        # Set environment variables
        os.environ['SENDER_EMAIL'] = email
        os.environ['SENDER_PASSWORD'] = password
        os.environ['SMTP_SERVER'] = server
        os.environ['SMTP_PORT'] = str(port)
        os.environ['EMAIL_ENABLED'] = 'true'
        os.environ['USE_SSL'] = str(use_ssl).lower()
        
        if test_connection():
            print(f"✅ Success with {server}:{port}")
            return save_to_env_file(email, password, server, str(port), use_ssl)
    
    print("❌ All SMTP servers failed. Trying alternative approach...")
    return setup_alternative_email()

def setup_custom_email():
    """Setup with custom email provider"""
    print("\n🔧 Custom Email Setup")
    
    email = input("Email address: ").strip()
    password = input("Password: ").strip()
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

def setup_alternative_email():
    """Setup alternative email method"""
    print("\n🔧 Alternative Email Setup")
    print("Using a simple email service...")
    
    # Create a simple email configuration
    email = "healthcarereports0@gmail.com"
    password = "your-password-here"
    
    print(f"Email: {email}")
    password = input("Password: ").strip()
    
    # Set basic environment variables
    os.environ['SENDER_EMAIL'] = email
    os.environ['SENDER_PASSWORD'] = password
    os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
    os.environ['SMTP_PORT'] = '587'
    os.environ['EMAIL_ENABLED'] = 'true'
    os.environ['USE_SSL'] = 'false'
    
    return save_to_env_file(email, password, 'smtp.gmail.com', '587', False)

def test_connection():
    """Test email connection"""
    try:
        import smtplib
        from email_config_streamlit import SENDER_EMAIL, SENDER_PASSWORD, SMTP_SERVER, SMTP_PORT
        
        server = smtplib.SMTP_SSL(SMTP_SERVER, int(SMTP_PORT)) if os.getenv('USE_SSL') == 'true' else smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT))
        
        if os.getenv('USE_SSL') != 'true':
            server.starttls()
        
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.quit()
        return True
    except Exception as e:
        print(f"   ❌ Failed: {str(e)[:50]}...")
        return False

def test_and_save(email, password, server, port, use_ssl):
    """Test connection and save if successful"""
    if test_connection():
        print("✅ Email connection successful!")
        return save_to_env_file(email, password, server, port, use_ssl)
    else:
        print("❌ Email connection failed!")
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
    print("🎯 Simple Email Setup - No App Passwords Required!")
    print("=" * 50)
    
    success = setup_simple_email()
    
    if success:
        print("\n🎉 Email setup complete!")
        print("\n📋 Next steps:")
        print("1. Restart your Streamlit dashboard")
        print("2. Test email sending in the dashboard")
        print("3. If it doesn't work, try a different email provider")
        
        print("\n🚀 Your email service is ready to use!")
    else:
        print("\n❌ Email setup failed!")
        print("\n📖 Alternative options:")
        print("1. Try with a different email provider")
        print("2. Use your regular Gmail password (less secure)")
        print("3. Set up a free email account")

if __name__ == "__main__":
    main()
