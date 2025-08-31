# 📧 **Email Setup Guide**

## ✅ **Fix Email Sending Issues**

Your email service is currently not configured, which is why you're getting the "500 error" when trying to send PDFs. Follow this guide to set up a working email service.

## 🎯 **Quick Setup Options**

### **Option 1: Gmail SMTP (Recommended)**

This is the easiest and most reliable option.

#### **Step 1: Enable 2-Factor Authentication**
1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification
4. Follow the setup process

#### **Step 2: Generate App Password**
1. Go to Google Account settings
2. Navigate to Security → 2-Step Verification
3. Click "App passwords"
4. Select "Mail" and "Windows Computer"
5. Copy the 16-character password

#### **Step 3: Set Environment Variables**
Open Command Prompt or PowerShell and run:

```bash
# Set your Gmail credentials
set SENDER_EMAIL=your-email@gmail.com
set SENDER_PASSWORD=your-16-character-app-password

# Optional: Set SMTP settings (Gmail defaults)
set SMTP_SERVER=smtp.gmail.com
set SMTP_PORT=587
```

#### **Step 4: Test Email Service**
1. Open your dashboard
2. Go to "📊 Dashboard" tab
3. Expand "⚙️ Email Configuration"
4. Click "🔍 Test Email Connection"
5. You should see "✅ Email connection successful!"

### **Option 2: Other Email Providers**

#### **Outlook/Hotmail**
```bash
set SENDER_EMAIL=your-email@outlook.com
set SENDER_PASSWORD=your-password
set SMTP_SERVER=smtp-mail.outlook.com
set SMTP_PORT=587
```

#### **Yahoo Mail**
```bash
set SENDER_EMAIL=your-email@yahoo.com
set SENDER_PASSWORD=your-app-password
set SMTP_SERVER=smtp.mail.yahoo.com
set SMTP_PORT=587
```

#### **Custom SMTP Server**
```bash
set SENDER_EMAIL=your-email@yourdomain.com
set SENDER_PASSWORD=your-password
set SMTP_SERVER=your-smtp-server.com
set SMTP_PORT=587
```

## 🔧 **Permanent Configuration**

### **Windows Environment Variables**
1. Press `Win + R`, type `sysdm.cpl`, press Enter
2. Click "Environment Variables"
3. Under "User variables", click "New"
4. Add each variable:
   - Variable name: `SENDER_EMAIL`
   - Variable value: `your-email@gmail.com`
5. Repeat for `SENDER_PASSWORD`, `SMTP_SERVER`, `SMTP_PORT`

### **Create .env File**
Create a file named `.env` in your project root:

```env
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=your-16-character-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_ENABLED=true
```

## 🧪 **Testing Your Setup**

### **1. Test Email Connection**
1. Open your dashboard
2. Go to "📊 Dashboard" tab
3. Expand "⚙️ Email Configuration"
4. Click "🔍 Test Email Connection"

### **2. Test with Dummy Email**
1. Add a new patient with email: `test@example.com`
2. Generate PDF for the patient
3. Click "📧 Send" button
4. Check if email is sent successfully

### **3. Check Email Delivery**
- Check the recipient's inbox (including spam folder)
- Verify PDF attachment is included
- Confirm email content is correct

## 🚨 **Common Issues & Solutions**

### **Authentication Failed**
**Error:** "SMTP Authentication failed"
**Solution:**
- Ensure 2-factor authentication is enabled
- Use App Password, not regular password
- Check email and password are correct

### **Connection Failed**
**Error:** "SMTP Connection failed"
**Solution:**
- Check internet connection
- Verify SMTP server and port
- Check firewall settings
- Try different port (465 for SSL, 587 for TLS)

### **Invalid Recipient**
**Error:** "Invalid recipient email address"
**Solution:**
- Check email format is valid
- Ensure recipient email exists
- Try with a different email address

### **Service Not Configured**
**Error:** "Email not configured"
**Solution:**
- Set environment variables
- Restart your application
- Check variable names are correct

## 📋 **Email Service Features**

### **What Gets Sent**
- **Subject:** "Your Health Risk Assessment Report - Patient ID: [ID]"
- **Body:** Professional healthcare message with next steps
- **Attachment:** Patient's PDF report from `temp/` folder
- **From:** Your configured email address

### **Email Content**
```
Dear Patient,

We are sending you your personalized Health Risk Assessment Report based on your recent medical evaluation.

Your detailed report is attached to this email as a PDF document. Please review it carefully and discuss the findings with your healthcare provider.

Important Next Steps:
1. Schedule an appointment with your primary care physician
2. Review your current medications with your pharmacist
3. Implement the lifestyle changes recommended in the report
4. Monitor your symptoms and report any changes

If you have any questions or concerns, please contact your healthcare provider immediately.

Best regards,
Your Healthcare Team

---
This is an automated message. Please do not reply to this email.
For medical emergencies, call 911 or your local emergency number.
```

## 🔒 **Security Best Practices**

### **Email Security**
- ✅ Use App Passwords instead of regular passwords
- ✅ Enable 2-factor authentication
- ✅ Use secure SMTP ports (587 or 465)
- ✅ Keep credentials secure and private
- ❌ Don't share credentials in code
- ❌ Don't use weak passwords

### **Data Protection**
- ✅ PDFs are generated locally
- ✅ Emails sent directly to patients
- ✅ No data stored in external services
- ✅ Secure SMTP connections

## 🎯 **Success Indicators**

### **✅ Email Working Correctly When:**
- Connection test shows "✅ Email connection successful!"
- Send buttons are enabled for patients with emails
- Email sending shows success messages
- PDFs are delivered to recipient inboxes
- No more "500 error" messages

### **📊 Expected Results:**
- **Connection Test:** Successful SMTP connection
- **Email Sending:** Immediate success feedback
- **PDF Delivery:** Attachments received correctly
- **Error Handling:** Clear, specific error messages
- **User Experience:** Seamless email workflow

## 🚀 **Next Steps After Setup**

### **1. Test with Real Patients**
1. Add a new patient with a real email address
2. Generate their PDF report
3. Send the report via email
4. Verify delivery and content

### **2. Monitor Email Delivery**
- Check spam folders
- Verify PDF attachments
- Confirm email content quality
- Test with different email providers

### **3. Configure Bulk Operations**
- Test bulk PDF generation
- Test bulk email sending
- Monitor system performance
- Handle large patient lists

## 📞 **Support**

### **If You Need Help:**
1. **Check Error Messages:** Look for specific error details
2. **Test Connection:** Use the built-in connection tester
3. **Verify Credentials:** Double-check email and password
4. **Check Logs:** Review any error logs in the terminal

### **Common Error Messages:**
- **"Email not configured"** → Set environment variables
- **"Authentication failed"** → Use App Password
- **"Connection failed"** → Check internet and firewall
- **"Invalid recipient"** → Check email format

**Your email service will work perfectly once configured!** 📧✅
