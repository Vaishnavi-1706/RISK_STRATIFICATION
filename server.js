const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config({ path: './email_config.env' });

// Import routes
const emailRoutes = require('./routes/emailRoutes');

// Import services
const emailService = require('./utils/emailService');
const pdfGenerator = require('./utils/pdfGenerator');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Static files
app.use('/pdfs', express.static(path.join(__dirname, 'pdfs')));

// Routes
app.use('/api/email', emailRoutes);

// Health check route
app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        timestamp: new Date().toISOString(),
        service: 'Patient Risk Assessment Email Service',
        version: '1.0.0'
    });
});

// Root route with API documentation
app.get('/', (req, res) => {
    res.json({
        message: 'Patient Risk Assessment Email Service',
        version: '1.0.0',
        endpoints: {
            health: 'GET /health',
            emailStatus: 'GET /api/email/status',
            sendInvoice: 'POST /api/email/send-invoice',
            sendPatientReport: 'POST /api/email/send-patient-report',
            sendBulkReports: 'POST /api/email/send-bulk-reports',
            testConnection: 'POST /api/email/test-connection',
            listPdfFiles: 'GET /api/email/pdf-files',
            deletePdfFile: 'DELETE /api/email/pdf-files/:filename'
        },
        documentation: {
            setup: 'Configure EMAIL_USER and EMAIL_PASS in email_config.env',
            gmailSetup: 'Enable 2FA and generate App Password for Gmail',
            testEndpoint: 'POST /api/email/send-invoice with email and patientId'
        }
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('❌ Server error:', err.stack);
    res.status(500).json({
        success: false,
        error: 'Internal server error',
        message: err.message
    });
});

// 404 handler
app.use('*', (req, res) => {
    res.status(404).json({
        success: false,
        error: 'Route not found',
        availableRoutes: [
            'GET /',
            'GET /health',
            'GET /api/email/status',
            'POST /api/email/send-invoice',
            'POST /api/email/send-patient-report',
            'POST /api/email/send-bulk-reports',
            'POST /api/email/test-connection',
            'GET /api/email/pdf-files',
            'DELETE /api/email/pdf-files/:filename'
        ]
    });
});

// Start server
app.listen(PORT, async () => {
    console.log('🚀 Patient Risk Assessment Email Service starting...');
    console.log(`📡 Server running on port ${PORT}`);
    console.log(`🌐 Base URL: http://localhost:${PORT}`);
    
    // Initialize services
    try {
        // Check email service status
        const emailStatus = emailService.getStatus();
        console.log(`📧 Email Service Status: ${emailStatus.configured ? '✅ Configured' : '❌ Not Configured'}`);
        
        if (!emailStatus.configured) {
            console.log('⚠️  Please configure EMAIL_USER and EMAIL_PASS in email_config.env');
            console.log('📖 Gmail Setup Instructions:');
            console.log('   1. Enable 2-Factor Authentication on your Google account');
            console.log('   2. Generate an App Password: Google Account > Security > 2-Step Verification > App passwords');
            console.log('   3. Update email_config.env with your Gmail and App Password');
        }
        
        // Check PDF storage
        const storageStats = await pdfGenerator.getStorageStats();
        console.log(`📁 PDF Storage: ${storageStats.totalFiles} files, ${(storageStats.totalSize / 1024).toFixed(2)} KB`);
        
    } catch (error) {
        console.error('❌ Service initialization error:', error.message);
    }
    
    console.log('\n📋 Available Endpoints:');
    console.log('   GET  /health                    - Health check');
    console.log('   GET  /api/email/status          - Email service status');
    console.log('   POST /api/email/send-invoice    - Send invoice email (test)');
    console.log('   POST /api/email/send-patient-report - Send patient report');
    console.log('   POST /api/email/send-bulk-reports   - Send bulk reports');
    console.log('   POST /api/email/test-connection     - Test email connection');
    console.log('   GET  /api/email/pdf-files       - List PDF files');
    console.log('   DELETE /api/email/pdf-files/:filename - Delete PDF file');
    
    console.log('\n🎯 Quick Test:');
    console.log('   curl -X POST http://localhost:3000/api/email/send-invoice \\');
    console.log('        -H "Content-Type: application/json" \\');
    console.log('        -d \'{"email":"test@example.com","patientId":"TEST001"}\'');
    
    console.log('\n✅ Server ready!');
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down server gracefully...');
    process.exit(0);
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Server terminated');
    process.exit(0);
});

module.exports = app;
