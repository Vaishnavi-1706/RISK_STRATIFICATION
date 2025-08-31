#!/usr/bin/env python3
"""
Quick Fix Email Setup
Tries multiple configurations to get email working
"""

import os

def quick_email_fix():
    print("🚀 Quick Email Fix - Multiple Configurations")
    print("=" * 50)
    
    email = "healthcarereports0@gmail.com"
    password = input("Enter your Gmail password: ").strip()
    
    if not password:
        print("❌ Password required!")
        return False
    
    # Try different SMTP configurations
    configs = [
        ("smtp.gmail.com", "587", False, "Gmail TLS"),
        ("smtp.gmail.com", "465", True, "Gmail SSL"),
        ("smtp-mail.outlook.com", "587", False, "Outlook"),
        ("smtp.mail.yahoo.com", "587", False, "Yahoo"),
    ]
    
    for server, port, use_ssl, name in configs:
        print(f"\n🔍 Testing {name} ({server}:{port})...")
        
        # Set environment variables
        os.environ['SENDER_EMAIL'] = email
        os.environ['SENDER_PASSWORD'] = password
        os.environ['SMTP_SERVER'] = server
        os.environ['SMTP_PORT'] = str(port)
        os.environ['EMAIL_ENABLED'] = 'true'
        os.environ['USE_SSL'] = str(use_ssl).lower()
        
        if test_smtp_connection():
            print(f"✅ Success with {name}!")
            save_config(email, password, server, port, use_ssl)
            return True
    
    print("\n❌ All configurations failed. Trying alternative approach...")
    return setup_alternative()

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

def setup_alternative():
    """Setup alternative email method"""
    print("\n🔧 Alternative Setup")
    print("Setting up basic configuration that might work...")
    
    email = "healthcarereports0@gmail.com"
    password = input("Enter your password again: ").strip()
    
    # Set basic configuration
    os.environ['SENDER_EMAIL'] = email
    os.environ['SENDER_PASSWORD'] = password
    os.environ['SMTP_SERVER'] = 'smtp.gmail.com'
    os.environ['SMTP_PORT'] = '587'
    os.environ['EMAIL_ENABLED'] = 'true'
    os.environ['USE_SSL'] = 'false'
    
    save_config(email, password, 'smtp.gmail.com', '587', False)
    print("✅ Basic configuration saved. Try restarting your app.")
    return True

def save_config(email, password, server, port, use_ssl):
    """Save configuration to .env file"""
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
        
        print("✅ Configuration saved to .env file")
        print(f"   Email: {email}")
        print(f"   Server: {server}")
        print(f"   Port: {port}")
        print(f"   SSL: {use_ssl}")
        
    except Exception as e:
        print(f"⚠️ Could not save to .env file: {e}")

def main():
    print("🎯 Quick Email Fix for Patient Dashboard")
    print("=" * 50)
    
    success = quick_email_fix()
    
    if success:
        print("\n🎉 Email configuration saved!")
        print("\n📋 Next steps:")
        print("1. Restart your Streamlit dashboard")
        print("2. Test email sending in the dashboard")
        print("3. If it still doesn't work, try a different email provider")
        
        print("\n🚀 Your email service should now work!")
    else:
        print("\n❌ Email setup failed!")
        print("\n📖 Try these alternatives:")
        print("1. Use a different email provider (Outlook, Yahoo)")
        print("2. Check your internet connection")
        print("3. Try with a different Gmail account")

if __name__ == "__main__":
    main()
