#!/usr/bin/env python3
"""
Interactive Email Setup Script
Helps you configure email credentials quickly
"""

import os
import getpass

def setup_email_credentials():
    """Interactive email setup"""
    print("🔧 Email Setup Wizard")
    print("=" * 50)
    
    print("\n📧 Let's configure your email service!")
    print("This will set up environment variables for sending emails.")
    
    # Get email provider
    print("\n1. Choose your email provider:")
    print("   1. Gmail (Recommended)")
    print("   2. Outlook/Hotmail")
    print("   3. Yahoo Mail")
    print("   4. Custom SMTP")
    
    choice = input("\nEnter your choice (1-4): ").strip()
    
    # Set default values based on choice
    if choice == "1":  # Gmail
        smtp_server = "smtp.gmail.com"
        smtp_port = "587"
        provider = "Gmail"
    elif choice == "2":  # Outlook
        smtp_server = "smtp-mail.outlook.com"
        smtp_port = "587"
        provider = "Outlook"
    elif choice == "3":  # Yahoo
        smtp_server = "smtp.mail.yahoo.com"
        smtp_port = "587"
        provider = "Yahoo"
    elif choice == "4":  # Custom
        smtp_server = input("Enter SMTP server (e.g., smtp.yourdomain.com): ").strip()
        smtp_port = input("Enter SMTP port (e.g., 587): ").strip()
        provider = "Custom"
    else:
        print("❌ Invalid choice. Using Gmail defaults.")
        smtp_server = "smtp.gmail.com"
        smtp_port = "587"
        provider = "Gmail"
    
    print(f"\n✅ Using {provider} settings:")
    print(f"   Server: {smtp_server}")
    print(f"   Port: {smtp_port}")
    
    # Get email credentials
    print(f"\n2. Enter your {provider} credentials:")
    email = input("   Email address: ").strip()
    
    if provider == "Gmail":
        print("\n   📝 For Gmail, you need an App Password:")
        print("   1. Enable 2-Factor Authentication on your Google Account")
        print("   2. Go to Security → App passwords")
        print("   3. Generate a password for 'Mail'")
        print("   4. Use the 16-character password (not your regular password)")
        password = getpass.getpass("   App Password (16 characters): ")
    else:
        password = getpass.getpass("   Password: ")
    
    # Validate inputs
    if not email or not password:
        print("❌ Email and password are required!")
        return False
    
    if "@" not in email:
        print("❌ Please enter a valid email address!")
        return False
    
    # Set environment variables
    print(f"\n3. Setting environment variables...")
    
    # Set the variables
    os.environ['SENDER_EMAIL'] = email
    os.environ['SENDER_PASSWORD'] = password
    os.environ['SMTP_SERVER'] = smtp_server
    os.environ['SMTP_PORT'] = smtp_port
    os.environ['EMAIL_ENABLED'] = 'true'
    
    print("✅ Environment variables set!")
    
    # Test the configuration
    print(f"\n4. Testing email configuration...")
    
    try:
        from email_config_streamlit import test_email_connection
        result = test_email_connection()
        
        if result.get('success', False):
            print("✅ Email configuration successful!")
            print(f"   Server: {result.get('server')}")
            print(f"   Port: {result.get('port')}")
            
            # Save to .env file
            save_to_env_file(email, password, smtp_server, smtp_port)
            
            return True
        else:
            print(f"❌ Email configuration failed: {result.get('error')}")
            if result.get('details'):
                print(f"   Details: {result.get('details')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

def save_to_env_file(email, password, smtp_server, smtp_port):
    """Save credentials to .env file"""
    try:
        env_content = f"""# Email Configuration
SENDER_EMAIL={email}
SENDER_PASSWORD={password}
SMTP_SERVER={smtp_server}
SMTP_PORT={smtp_port}
EMAIL_ENABLED=true
"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("✅ Credentials saved to .env file")
        print("📝 You can now restart your application to use these settings")
        
    except Exception as e:
        print(f"⚠️ Could not save to .env file: {e}")
        print("📝 Please set the environment variables manually")

def main():
    """Main function"""
    print("🎯 Email Setup for Patient Dashboard")
    print("=" * 50)
    
    success = setup_email_credentials()
    
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
        print("1. Email address is correct")
        print("2. Password is correct")
        print("3. 2-Factor Authentication is enabled (for Gmail)")
        print("4. App Password is generated (for Gmail)")
        print("5. Internet connection is working")
        
        print("\n📚 For detailed instructions, see EMAIL_SETUP_GUIDE.md")

if __name__ == "__main__":
    main()
