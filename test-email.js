const axios = require('axios');

const BASE_URL = 'http://localhost:3000';

/**
 * Test script for the Patient Risk Assessment Email Service
 * Demonstrates all API endpoints and functionality
 */

async function testEmailService() {
    console.log('🧪 Testing Patient Risk Assessment Email Service\n');

    try {
        // Test 1: Health Check
        console.log('1️⃣ Testing Health Check...');
        const healthResponse = await axios.get(`${BASE_URL}/health`);
        console.log('✅ Health Check:', healthResponse.data);
        console.log('');

        // Test 2: Email Service Status
        console.log('2️⃣ Testing Email Service Status...');
        const statusResponse = await axios.get(`${BASE_URL}/api/email/status`);
        console.log('✅ Email Status:', statusResponse.data);
        console.log('');

        // Test 3: Test Email Connection
        console.log('3️⃣ Testing Email Connection...');
        try {
            const connectionResponse = await axios.post(`${BASE_URL}/api/email/test-connection`);
            console.log('✅ Email Connection:', connectionResponse.data);
        } catch (error) {
            console.log('❌ Email Connection Failed:', error.response?.data || error.message);
        }
        console.log('');

        // Test 4: Send Invoice Email (Test)
        console.log('4️⃣ Testing Send Invoice Email...');
        const invoiceData = {
            email: 'test@example.com',
            patientId: 'TEST001',
            patientData: {
                name: 'John Doe',
                age: 45,
                gender: 'Male',
                bmi: 25.5,
                bloodPressure: '120/80',
                glucose: 95,
                cholesterol: 180,
                risk30d: 25,
                risk60d: 30,
                risk90d: 35,
                riskLabel: 'Low Risk',
                recommendations: 'Continue preventive care routine | Annual wellness visit recommended',
                conditions: 'None reported'
            }
        };

        try {
            const invoiceResponse = await axios.post(`${BASE_URL}/api/email/send-invoice`, invoiceData);
            console.log('✅ Send Invoice:', invoiceResponse.data);
        } catch (error) {
            console.log('❌ Send Invoice Failed:', error.response?.data || error.message);
        }
        console.log('');

        // Test 5: List PDF Files
        console.log('5️⃣ Testing List PDF Files...');
        const pdfFilesResponse = await axios.get(`${BASE_URL}/api/email/pdf-files`);
        console.log('✅ PDF Files:', pdfFilesResponse.data);
        console.log('');

        // Test 6: Send Patient Report
        console.log('6️⃣ Testing Send Patient Report...');
        const patientReportData = {
            email: 'patient@example.com',
            patientId: 'PATIENT001',
            patientName: 'Jane Smith',
            pdfPath: './pdfs/patient_risk_assessment_TEST001_2024-01-01.pdf'
        };

        try {
            const patientReportResponse = await axios.post(`${BASE_URL}/api/email/send-patient-report`, patientReportData);
            console.log('✅ Send Patient Report:', patientReportResponse.data);
        } catch (error) {
            console.log('❌ Send Patient Report Failed:', error.response?.data || error.message);
        }
        console.log('');

        // Test 7: Send Bulk Reports
        console.log('7️⃣ Testing Send Bulk Reports...');
        const bulkData = {
            patients: [
                {
                    email: 'patient1@example.com',
                    name: 'Patient One',
                    id: 'PAT001',
                    pdfPath: './pdfs/patient_risk_assessment_PAT001_2024-01-01.pdf'
                },
                {
                    email: 'patient2@example.com',
                    name: 'Patient Two',
                    id: 'PAT002',
                    pdfPath: './pdfs/patient_risk_assessment_PAT002_2024-01-01.pdf'
                }
            ]
        };

        try {
            const bulkResponse = await axios.post(`${BASE_URL}/api/email/send-bulk-reports`, bulkData);
            console.log('✅ Send Bulk Reports:', bulkResponse.data);
        } catch (error) {
            console.log('❌ Send Bulk Reports Failed:', error.response?.data || error.message);
        }
        console.log('');

        console.log('🎉 All tests completed!');

    } catch (error) {
        console.error('❌ Test failed:', error.message);
        if (error.code === 'ECONNREFUSED') {
            console.log('💡 Make sure the server is running on http://localhost:3000');
            console.log('   Run: npm start');
        }
    }
}

// Run tests if this file is executed directly
if (require.main === module) {
    testEmailService();
}

module.exports = { testEmailService };
