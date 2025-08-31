const nodemailer = require('nodemailer');
const fs = require('fs-extra');
const path = require('path');

/**
 * Email Service for sending patient risk assessment PDF reports
 * Production-ready with comprehensive error handling and logging
 */
class EmailService {
    constructor() {
        this.transporter = null;
        this.isConfigured = false;
        this.initTransporter();
    }

    /**
     * Initialize the email transporter with Gmail SMTP
     */
    initTransporter() {
        try {
            // Get email configuration from environment variables
            const emailConfig = {
                host: process.env.EMAIL_HOST || 'smtp.gmail.com',
                port: parseInt(process.env.EMAIL_PORT) || 587,
                secure: false, // true for 465, false for other ports
                auth: {
                    user: process.env.EMAIL_USER,
                    pass: process.env.EMAIL_PASS
                }
            };

            // Validate email configuration
            if (!emailConfig.auth.user || !emailConfig.auth.pass) {
                console.error('❌ Email configuration missing. Please set EMAIL_USER and EMAIL_PASS environment variables.');
                this.isConfigured = false;
                return;
            }

            // Create transporter
            this.transporter = nodemailer.createTransport(emailConfig);
            this.isConfigured = true;
            console.log('✅ Email service configured successfully');

        } catch (error) {
            console.error('❌ Failed to initialize email transporter:', error.message);
            this.isConfigured = false;
        }
    }

    /**
     * Verify email configuration
     */
    async verifyConnection() {
        if (!this.isConfigured) {
            throw new Error('Email service not configured. Please check environment variables.');
        }

        try {
            await this.transporter.verify();
            return true;
        } catch (error) {
            console.error('❌ Email connection verification failed:', error.message);
            throw new Error('Email service connection failed. Please check your credentials.');
        }
    }

    /**
     * Send email with PDF attachment from file path
     * @param {string} to - Recipient email address
     * @param {string} subject - Email subject
     * @param {string} message - Email message
     * @param {string} pdfPath - Path to PDF file
     * @param {string} pdfName - Name for the PDF attachment
     */
    async sendEmailWithPdfFromFile(to, subject, message, pdfPath, pdfName) {
        try {
            // Verify connection first
            await this.verifyConnection();

            // Check if PDF file exists
            if (!await fs.pathExists(pdfPath)) {
                throw new Error(`PDF file not found: ${pdfPath}`);
            }

            // Prepare email options
            const mailOptions = {
                from: process.env.EMAIL_USER,
                to: to,
                subject: subject,
                text: message,
                attachments: [
                    {
                        filename: pdfName,
                        path: pdfPath
                    }
                ]
            };

            // Send email
            const result = await this.transporter.sendMail(mailOptions);
            console.log(`✅ Email sent successfully to ${to}. Message ID: ${result.messageId}`);
            return {
                success: true,
                messageId: result.messageId,
                recipient: to
            };

        } catch (error) {
            console.error(`❌ Failed to send email to ${to}:`, error.message);
            throw new Error(`Email sending failed: ${error.message}`);
        }
    }

    /**
     * Send email with PDF attachment from buffer
     * @param {string} to - Recipient email address
     * @param {string} subject - Email subject
     * @param {string} message - Email message
     * @param {Buffer} pdfBuffer - PDF file buffer
     * @param {string} pdfName - Name for the PDF attachment
     */
    async sendEmailWithPdfFromBuffer(to, subject, message, pdfBuffer, pdfName) {
        try {
            // Verify connection first
            await this.verifyConnection();

            // Validate PDF buffer
            if (!pdfBuffer || !Buffer.isBuffer(pdfBuffer)) {
                throw new Error('Invalid PDF buffer provided');
            }

            // Prepare email options
            const mailOptions = {
                from: process.env.EMAIL_USER,
                to: to,
                subject: subject,
                text: message,
                attachments: [
                    {
                        filename: pdfName,
                        content: pdfBuffer,
                        contentType: 'application/pdf'
                    }
                ]
            };

            // Send email
            const result = await this.transporter.sendMail(mailOptions);
            console.log(`✅ Email sent successfully to ${to}. Message ID: ${result.messageId}`);
            return {
                success: true,
                messageId: result.messageId,
                recipient: to
            };

        } catch (error) {
            console.error(`❌ Failed to send email to ${to}:`, error.message);
            throw new Error(`Email sending failed: ${error.message}`);
        }
    }

    /**
     * Send patient risk assessment report
     * @param {string} patientEmail - Patient's email address
     * @param {string} patientName - Patient's name
     * @param {string} patientId - Patient's ID
     * @param {string} pdfPath - Path to PDF report
     */
    async sendPatientRiskAssessment(patientEmail, patientName, patientId, pdfPath) {
        const subject = `Your Health Risk Assessment Report - Patient ID: ${patientId}`;
        const message = `Dear ${patientName || 'Patient'},

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
For medical emergencies, call 911 or your local emergency number.`;

        const pdfName = `patient_risk_assessment_${patientId}_${new Date().toISOString().split('T')[0]}.pdf`;

        return await this.sendEmailWithPdfFromFile(patientEmail, subject, message, pdfPath, pdfName);
    }

    /**
     * Send bulk patient risk assessment reports
     * @param {Array} patients - Array of patient objects with email, name, id, and pdfPath
     */
    async sendBulkPatientReports(patients) {
        const results = {
            successful: [],
            failed: []
        };

        for (const patient of patients) {
            try {
                const result = await this.sendPatientRiskAssessment(
                    patient.email,
                    patient.name,
                    patient.id,
                    patient.pdfPath
                );
                results.successful.push(result);
            } catch (error) {
                results.failed.push({
                    patient: patient,
                    error: error.message
                });
            }
        }

        console.log(`📧 Bulk email sending completed: ${results.successful.length} successful, ${results.failed.length} failed`);
        return results;
    }

    /**
     * Get email service status
     */
    getStatus() {
        return {
            configured: this.isConfigured,
            host: process.env.EMAIL_HOST,
            port: process.env.EMAIL_PORT,
            user: process.env.EMAIL_USER ? 'Configured' : 'Not configured'
        };
    }
}

// Create singleton instance
const emailService = new EmailService();

module.exports = emailService;
