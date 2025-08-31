# 🔧 Gmail App Password Setup Guide

## 📋 Quick Steps to Fix Your Email Issue

### Step 1: Enable 2-Factor Authentication on Gmail

1. **Go to your Google Account settings:**
   - Visit: https://myaccount.google.com/
   - Sign in with your Gmail account: `kalaimohanraj2005@gmail.com`

2. **Enable 2-Factor Authentication:**
   - Click on "Security" in the left sidebar
   - Find "2-Step Verification" and click "Get started"
   - Follow the setup process (usually involves your phone number)
   - Complete the verification

### Step 2: Generate an App Password

1. **Go to App Passwords:**
   - In Security settings, find "App passwords"
   - Click on "App passwords"

2. **Generate the password:**
   - Select "Mail" from the dropdown
   - Click "Generate"
   - Google will show you a 16-character password (like: `abcd efgh ijkl mnop`)
   - **Copy this password** (you won't see it again!)

### Step 3: Update Your Email Configuration

1. **Edit the email_credentials.py file:**
   - Open `email_credentials.py` in your project folder
   - Find this line:
     ```python
     SENDER_PASSWORD = "your-16-character-app-password-here"
     ```
   - Replace it with your actual App Password:
     ```python
     SENDER_PASSWORD = "abcd efgh ijkl mnop"  # Your actual 16-character password
     ```

2. **Save the file**

### Step 4: Test Your Configuration

1. **Run the configuration test:**
   ```bash
   python email_credentials.py
   ```
   - Should show: "✅ Email configuration looks good!"

2. **Test email connection:**
   ```bash
   python test_email_config.py
   ```
   - Should show: "✅ Email connection successful!"

### Step 5: Restart Your Dashboard

1. **Stop your current Streamlit dashboard** (Ctrl+C)
2. **Start it again:**
   ```bash
   streamlit run working_patient_dashboard.py --server.port 8509
   ```

### Step 6: Test Email Sending

1. **Go to your dashboard:** http://localhost:8509
2. **Navigate to:** "📊 Dashboard" tab
3. **Expand:** "⚙️ Email Configuration"
4. **Click:** "🔍 Test Email Connection"
5. **Should show:** "✅ Email connection successful!"

## 🎯 What You'll See After Setup

### ✅ Success Indicators:
- Connection test shows "✅ Email connection successful!"
- Send buttons are enabled for patients with emails
- Email sending shows success messages
- No more "500 error" messages

### 📧 Test Email Sending:
1. Add a new patient with email: `test@example.com`
2. Generate PDF for the patient
3. Click "📧 Send" button
4. Verify email is sent successfully

## 🔍 Troubleshooting

### If you get "Authentication failed":
- Make sure you're using the App Password, not your regular Gmail password
- Ensure 2-Factor Authentication is enabled
- Check that the App Password is exactly 16 characters

### If you get "Connection failed":
- Check your internet connection
- Verify the SMTP settings are correct
- Try again in a few minutes

### If you can't find App Passwords:
- Make sure 2-Factor Authentication is fully enabled
- Try refreshing the Google Account page
- Look for "App passwords" under Security settings

## 📞 Need Help?

If you're still having issues:

1. **Check the error messages** in your dashboard
2. **Verify your App Password** is correct
3. **Make sure 2-Factor Authentication** is enabled
4. **Test with a simple email** first

## 🎉 Success!

Once you complete these steps, your email service will work perfectly and you'll be able to send PDF reports to patients automatically!

---

**Next Step:** Follow the steps above, then test your email sending in the dashboard! 🚀
