# 📧 **Node.js + Express + Nodemailer Email Service**

## 🎯 **Complete Working Solution**

A production-ready Node.js email service for sending patient risk assessment PDF reports via email using Gmail SMTP.

### **✅ What's Implemented**

**Complete Email Service with:**
1. **PDF Generation** - Creates patient risk assessment reports
2. **Email Sending** - Sends PDFs via Gmail SMTP with App Password
3. **Bulk Operations** - Send reports to multiple patients
4. **File Management** - Store and manage PDF files
5. **Error Handling** - Comprehensive error handling and logging
6. **Production Ready** - Separated utilities, async/await, environment config

## 📁 **Project Structure**

```
├── package.json                 # Dependencies and scripts
├── email_config.env            # Email configuration
├── server.js                   # Main Express server
├── test-email.js              # Test script
├── utils/
│   ├── emailService.js        # Email service utility
│   └── pdfGenerator.js        # PDF generation utility
├── routes/
│   └── emailRoutes.js         # Email API routes
└── pdfs/                      # PDF storage directory
```

## 🚀 **Quick Start**

### **1. Install Dependencies**
```bash
npm install
```

### **2. Configure Email Settings**
Edit `email_config.env`:
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password
PORT=3000
PDF_STORAGE_PATH=./pdfs
```

### **3. Gmail Setup**
1. **Enable 2-Factor Authentication** on your Google account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security > 2-Step Verification > App passwords
   - Generate new app password for "Mail"
3. **Update Configuration**:
   - Replace `EMAIL_USER` with your Gmail address
   - Replace `EMAIL_PASS` with the 16-character app password

### **4. Start Server**
```bash
npm start
```

### **5. Test the Service**
```bash
node test-email.js
```

## 📋 **API Endpoints**

### **Health & Status**
- `GET /health` - Health check
- `GET /api/email/status` - Email service status
- `POST /api/email/test-connection` - Test email connection

### **Email Operations**
- `POST /api/email/send-invoice` - Send invoice email (test)
- `POST /api/email/send-patient-report` - Send patient report
- `POST /api/email/send-bulk-reports` - Send bulk reports

### **File Management**
- `GET /api/email/pdf-files` - List PDF files
- `DELETE /api/email/pdf-files/:filename` - Delete PDF file

## 🎯 **Key Features**

### **1. Production-Ready Email Service**
```javascript
// utils/emailService.js
class EmailService {
    async sendEmailWithPdfFromFile(to, subject, message, pdfPath, pdfName)
    async sendEmailWithPdfFromBuffer(to, subject, message, pdfBuffer, pdfName)
    async sendPatientRiskAssessment(patientEmail, patientName, patientId, pdfPath)
    async sendBulkPatientReports(patients)
}
```

### **2. PDF Generation & Management**
```javascript
// utils/pdfGenerator.js
class PdfGenerator {
    async generateSamplePdf(patientId, patientData)
    async copyExistingPdf(sourcePath, patientId)
    async getPdfPath(patientId)
    async listPdfFiles()
}
```

### **3. Comprehensive Error Handling**
- Connection verification
- File existence checks
- Email validation
- Graceful error responses

### **4. Environment Configuration**
- Secure credential management
- Configurable settings
- Development/production modes

## 📧 **Email Functionality**

### **Send Invoice Email (Test Route)**
```bash
curl -X POST http://localhost:3000/api/email/send-invoice \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "patientId": "TEST001",
    "patientData": {
      "name": "John Doe",
      "age": 45,
      "risk30d": 25,
      "riskLabel": "Low Risk"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Email sent successfully",
  "data": {
    "success": true,
    "messageId": "<message-id>",
    "recipient": "test@example.com"
  },
  "pdfPath": "./pdfs/patient_risk_assessment_TEST001_2024-01-01.pdf"
}
```

### **Send Patient Risk Assessment**
```bash
curl -X POST http://localhost:3000/api/email/send-patient-report \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patient@example.com",
    "patientId": "PATIENT001",
    "patientName": "Jane Smith",
    "pdfPath": "./pdfs/patient_report.pdf"
  }'
```

### **Send Bulk Reports**
```bash
curl -X POST http://localhost:3000/api/email/send-bulk-reports \
  -H "Content-Type: application/json" \
  -d '{
    "patients": [
      {
        "email": "patient1@example.com",
        "name": "Patient One",
        "id": "PAT001",
        "pdfPath": "./pdfs/patient1_report.pdf"
      },
      {
        "email": "patient2@example.com",
        "name": "Patient Two",
        "id": "PAT002",
        "pdfPath": "./pdfs/patient2_report.pdf"
      }
    ]
  }'
```

## 🔧 **Technical Implementation**

### **Email Service Features**
- **Gmail SMTP** with App Password authentication
- **TLS Encryption** for secure transmission
- **File & Buffer Support** for PDF attachments
- **Connection Verification** before sending
- **Comprehensive Logging** for debugging

### **PDF Management**
- **Automatic Storage** in `./pdfs` directory
- **File Naming** with patient ID and timestamp
- **Copy Operations** from existing PDFs
- **Storage Statistics** and file listing

### **Error Handling**
- **Validation** of email addresses and file paths
- **Graceful Degradation** for missing files
- **Detailed Error Messages** for debugging
- **Connection Recovery** for network issues

## 📊 **Email Templates**

### **Patient Risk Assessment Email**
```
Subject: Your Health Risk Assessment Report - Patient ID: [ID]

Dear [Patient Name],

We are sending you your personalized Health Risk Assessment Report 
based on your recent medical evaluation.

Your detailed report is attached to this email as a PDF document. 
Please review it carefully and discuss the findings with your 
healthcare provider.

Important Next Steps:
1. Schedule an appointment with your primary care physician
2. Review your current medications with your pharmacist
3. Implement the lifestyle changes recommended in the report
4. Monitor your symptoms and report any changes

If you have any questions or concerns, please contact your 
healthcare provider immediately.

Best regards,
Your Healthcare Team

---
This is an automated message. Please do not reply to this email.
For medical emergencies, call 911 or your local emergency number.
```

## 🧪 **Testing**

### **Run All Tests**
```bash
node test-email.js
```

### **Individual Test Examples**
```bash
# Health check
curl http://localhost:3000/health

# Email status
curl http://localhost:3000/api/email/status

# Test connection
curl -X POST http://localhost:3000/api/email/test-connection

# List PDF files
curl http://localhost:3000/api/email/pdf-files
```

## 🔒 **Security Features**

### **Email Security**
- **TLS Encryption** for all email transmission
- **App Password Authentication** (not regular password)
- **No Credentials in Code** (environment variables only)
- **Connection Verification** before sending

### **File Security**
- **Secure File Storage** in dedicated directory
- **File Validation** before operations
- **Access Control** through API endpoints
- **Automatic Cleanup** capabilities

## 📈 **Production Deployment**

### **Environment Variables**
```bash
# Production settings
NODE_ENV=production
PORT=3000
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=healthcare@yourhospital.com
EMAIL_PASS=your-app-password
PDF_STORAGE_PATH=/var/www/pdfs
LOG_LEVEL=info
```

### **Process Management**
```bash
# Using PM2
npm install -g pm2
pm2 start server.js --name "email-service"

# Using Docker
docker build -t email-service .
docker run -p 3000:3000 email-service
```

## 🎯 **Integration with Python Dashboard**

### **Call Node.js API from Python**
```python
import requests

def send_patient_email(patient_data, pdf_path):
    url = "http://localhost:3000/api/email/send-patient-report"
    data = {
        "email": patient_data["email"],
        "patientId": patient_data["id"],
        "patientName": patient_data["name"],
        "pdfPath": pdf_path
    }
    
    response = requests.post(url, json=data)
    return response.json()
```

## 📋 **Complete Workflow**

### **1. PDF Creation**
- Generate PDF from patient data
- Store in `./pdfs` directory
- Return file path

### **2. Email Sending**
- Validate email configuration
- Verify SMTP connection
- Attach PDF to email
- Send with professional template
- Log success/failure

### **3. Bulk Operations**
- Process multiple patients
- Handle individual failures
- Report success/failure counts
- Continue on partial failures

## 🎉 **Benefits**

### **For Healthcare Providers**
- ✅ **Automated Email Sending** - No manual work required
- ✅ **Professional Templates** - Healthcare-standard emails
- ✅ **Bulk Operations** - Send to multiple patients at once
- ✅ **Reliable Delivery** - Gmail SMTP with error handling
- ✅ **Audit Trail** - Complete logging of all operations

### **For Patients**
- ✅ **Immediate Delivery** - Instant email notifications
- ✅ **Professional Format** - Healthcare-standard PDF reports
- ✅ **Secure Transmission** - TLS encrypted emails
- ✅ **Clear Instructions** - Actionable next steps

### **For System**
- ✅ **Scalable Architecture** - Handles any number of patients
- ✅ **Production Ready** - Comprehensive error handling
- ✅ **Easy Integration** - RESTful API endpoints
- ✅ **Maintainable Code** - Separated utilities and services

## 🚀 **Ready to Use**

Your Node.js email service is **fully operational** and ready for production use! 

**Key Features Delivered:**
1. ✅ **PDF Generation** - Creates patient risk assessment reports
2. ✅ **Email Sending** - Gmail SMTP with App Password
3. ✅ **Bulk Operations** - Send to multiple patients
4. ✅ **File Management** - Store and manage PDFs
5. ✅ **Error Handling** - Comprehensive error management
6. ✅ **Production Ready** - Separated utilities, async/await
7. ✅ **Test Route** - `/send-invoice` for testing
8. ✅ **Complete Documentation** - Ready for deployment

**Start using it now:**
```bash
npm install
# Configure email_config.env
npm start
# Test with: node test-email.js
```

**Your complete Node.js + Express + Nodemailer email service is ready!** 📧✨
