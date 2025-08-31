const express = require('express');
const router = express.Router();
const emailService = require('../utils/emailService');
const pdfGenerator = require('../utils/pdfGenerator');
const fs = require('fs-extra');
const path = require('path');

/**
 * @route   GET /api/email/status
 * @desc    Get email service status
 * @access  Public
 */
router.get('/status', async (req, res) => {
    try {
        const status = emailService.getStatus();
        const storageStats = await pdfGenerator.getStorageStats();
        
        res.json({
            success: true,
            emailService: status,
            storage: storageStats,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('❌ Error getting email status:', error.message);
        res.status(500).json({
            success: false,
            error: 'Failed to get email service status',
            details: error.message
        });
    }
});

/**
 * @route   POST /api/email/send-invoice
 * @desc    Send invoice email with PDF attachment (simulation)
 * @access  Public
 */
router.post('/send-invoice', async (req, res) => {
    try {
        const { email, patientId, patientData } = req.body;

        // Validate required fields
        if (!email) {
            return res.status(400).json({
                success: false,
                error: 'Email address is required'
            });
        }

        if (!patientId) {
            return res.status(400).json({
                success: false,
                error: 'Patient ID is required'
            });
        }

        console.log(`📧 Sending invoice email to: ${email} for patient: ${patientId}`);

        // Generate or copy PDF
        let pdfPath;
        try {
            // First, try to copy the existing sample PDF
            const samplePdfPath = path.join(__dirname, '..', 'patient_report_004.pdf');
            if (await fs.pathExists(samplePdfPath)) {
                pdfPath = await pdfGenerator.copyExistingPdf(samplePdfPath, patientId);
            } else {
                // Generate a sample PDF if the existing one doesn't exist
                pdfPath = await pdfGenerator.generateSamplePdf(patientId, patientData);
            }
        } catch (error) {
            console.error('❌ PDF generation/copy failed:', error.message);
            return res.status(500).json({
                success: false,
                error: 'Failed to generate PDF',
                details: error.message
            });
        }

        // Send email with PDF attachment
        const result = await emailService.sendEmailWithPdfFromFile(
            email,
            'Your Invoice',
            'Hello, please find attached your invoice.',
            pdfPath,
            `patient_risk_assessment_${patientId}.pdf`
        );

        res.json({
            success: true,
            message: 'Email sent successfully',
            data: result,
            pdfPath: pdfPath
        });

    } catch (error) {
        console.error('❌ Error sending invoice email:', error.message);
        res.status(500).json({
            success: false,
            error: 'Failed to send invoice email',
            details: error.message
        });
    }
});

/**
 * @route   POST /api/email/send-patient-report
 * @desc    Send patient risk assessment report
 * @access  Public
 */
router.post('/send-patient-report', async (req, res) => {
    try {
        const { email, patientId, patientName, pdfPath } = req.body;

        // Validate required fields
        if (!email || !patientId) {
            return res.status(400).json({
                success: false,
                error: 'Email address and Patient ID are required'
            });
        }

        console.log(`📧 Sending patient report to: ${email} for patient: ${patientId}`);

        // Send patient risk assessment email
        const result = await emailService.sendPatientRiskAssessment(
            email,
            patientName,
            patientId,
            pdfPath
        );

        res.json({
            success: true,
            message: 'Patient report sent successfully',
            data: result
        });

    } catch (error) {
        console.error('❌ Error sending patient report:', error.message);
        res.status(500).json({
            success: false,
            error: 'Failed to send patient report',
            details: error.message
        });
    }
});

/**
 * @route   POST /api/email/send-bulk-reports
 * @desc    Send bulk patient risk assessment reports
 * @access  Public
 */
router.post('/send-bulk-reports', async (req, res) => {
    try {
        const { patients } = req.body;

        // Validate required fields
        if (!patients || !Array.isArray(patients)) {
            return res.status(400).json({
                success: false,
                error: 'Patients array is required'
            });
        }

        console.log(`📧 Sending bulk reports to ${patients.length} patients`);

        // Send bulk patient reports
        const results = await emailService.sendBulkPatientReports(patients);

        res.json({
            success: true,
            message: 'Bulk reports sent successfully',
            data: results
        });

    } catch (error) {
        console.error('❌ Error sending bulk reports:', error.message);
        res.status(500).json({
            success: false,
            error: 'Failed to send bulk reports',
            details: error.message
        });
    }
});

/**
 * @route   POST /api/email/test-connection
 * @desc    Test email service connection
 * @access  Public
 */
router.post('/test-connection', async (req, res) => {
    try {
        console.log('🔍 Testing email service connection...');
        
        const isConnected = await emailService.verifyConnection();
        
        res.json({
            success: true,
            message: 'Email service connection test successful',
            connected: isConnected
        });

    } catch (error) {
        console.error('❌ Email connection test failed:', error.message);
        res.status(500).json({
            success: false,
            error: 'Email service connection test failed',
            details: error.message
        });
    }
});

/**
 * @route   GET /api/email/pdf-files
 * @desc    List all PDF files in storage
 * @access  Public
 */
router.get('/pdf-files', async (req, res) => {
    try {
        const pdfFiles = await pdfGenerator.listPdfFiles();
        
        res.json({
            success: true,
            data: pdfFiles
        });

    } catch (error) {
        console.error('❌ Error listing PDF files:', error.message);
        res.status(500).json({
            success: false,
            error: 'Failed to list PDF files',
            details: error.message
        });
    }
});

/**
 * @route   DELETE /api/email/pdf-files/:filename
 * @desc    Delete a PDF file
 * @access  Public
 */
router.delete('/pdf-files/:filename', async (req, res) => {
    try {
        const { filename } = req.params;
        const filePath = path.join(pdfGenerator.pdfStoragePath, filename);
        
        const deleted = await pdfGenerator.deletePdf(filePath);
        
        if (deleted) {
            res.json({
                success: true,
                message: 'PDF file deleted successfully'
            });
        } else {
            res.status(404).json({
                success: false,
                error: 'PDF file not found'
            });
        }

    } catch (error) {
        console.error('❌ Error deleting PDF file:', error.message);
        res.status(500).json({
            success: false,
            error: 'Failed to delete PDF file',
            details: error.message
        });
    }
});

module.exports = router;
