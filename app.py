#!/usr/bin/env python3
"""
Risk Stratification Web Application (single-file)
- Replaced old risk.email_service with mail_utils.send_email (now supports attachments)
- Generates visually enhanced PDF reports (tables + charts) and emails them as attachments
- Endpoints:
    /                 -> dashboard (index.html expected in templates/)
    /api/data         -> patient list (json)
    /api/summary      -> summary stats (json)
    /api/health       -> health check
    /api/predict      -> predict single (POST) - emails PDF if email present
    /api/predict-all  -> predict missing (POST)
    /api/send-recommendations-email -> send recommendations email (text or PDF)
    /api/send-bulk-emails -> send emails to all patients with EMAIL + AI_RECOMMENDATIONS
    /api/update-patient-email -> update email for patient (POST)
    /api/export-patient-pdf/<patient_id> -> download PDF
    /api/send-pdf-email -> generate PDF and email as attachment (POST)
"""

import os
import io
import re
import smtplib
import traceback
from datetime import datetime

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from flask import Flask, render_template, jsonify, request, send_file

import pandas as pd
from sqlalchemy import text

# ReportLab for PDF generation
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib import colors
from reportlab.lib.units import inch

# Matplotlib for charts embedded in PDF
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt

# dotenv for env variables
from dotenv import load_dotenv
load_dotenv()

# ---------------------------
# mail_utils (embedded here; you may split into mail_utils.py)
# ---------------------------
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True") == "True"
EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", EMAIL_HOST_USER or "no-reply")

def send_email(to_email: str, subject: str, message: str, attachment_bytes: bytes = None, attachment_filename: str = None):
    """
    Send an email using SMTP. If attachment_bytes is provided, attach it with attachment_filename.
    This uses environment variables defined at the top for SMTP configuration.
    """
    if not (EMAIL_HOST and EMAIL_HOST_USER and EMAIL_HOST_PASSWORD):
        raise RuntimeError("SMTP configuration is incomplete (EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD required).")

    msg = MIMEMultipart()
    msg["From"] = f"{EMAIL_FROM_NAME} <{EMAIL_HOST_USER}>"
    msg["To"] = to_email
    msg["Subject"] = subject

    # Plain text body
    body = MIMEText(message, "plain")
    msg.attach(body)

    # Attachment if provided
    if attachment_bytes is not None and attachment_filename:
        part = MIMEApplication(attachment_bytes, Name=attachment_filename)
        part['Content-Disposition'] = f'attachment; filename="{attachment_filename}"'
        msg.attach(part)

    # Send via SMTP
    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        if EMAIL_USE_TLS:
            server.starttls()
        server.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        server.send_message(msg)

    # Simple console info; your original mail_utils had a print
    print(f"[INFO] Email sent to {to_email} (subject: {subject})")

# ---------------------------
# End mail_utils
# ---------------------------

# ---------------------------
# App & project-specific imports
# ---------------------------
# Replace with your actual risk package imports
# The app expects functions in risk.db: get_engine, ensure_prediction_columns, update_predictions_in_db, update_predictions_in_db_bulk, update_patient_email, get_patient_by_id
# and in risk.model: load_model, predict_batch
# and risk.logger: logger
# If your risk package differs, adapt these imports or provide appropriate wrappers.
try:
    from risk.db import get_engine  # expects SQLAlchemy engine provider
except Exception:
    # Provide a fallback that tries sqlite3 connect-based engine if risk.db not available
    from sqlalchemy import create_engine
    def get_engine():
        db_url = os.getenv("DATABASE_URL", "sqlite:///training.db")
        return create_engine(db_url)

try:
    from risk.model import load_model, predict_batch
except Exception:
    # Fallback stubs (VERY simple; replace with your real model loader and predictor)
    def load_model(path):
        print(f"[WARN] load_model fallback used; path={path}")
        return None

    def predict_batch(df, model):
        # Example: add dummy columns if prediction not available
        out = df.copy()
        # ensure columns exist
        out['RISK_30D'] = out.get('RISK_30D', 0).fillna(0) if isinstance(out, pd.DataFrame) else 0
        out['RISK_60D'] = 0
        out['RISK_90D'] = 0
        out['RISK_LABEL'] = 'Low Risk'
        out['TOP_3_FEATURES'] = out.get('TOP_3_FEATURES', 'N/A')
        out['AI_RECOMMENDATIONS'] = out.get('AI_RECOMMENDATIONS', 'Continue current care plan')
        return out

try:
    from risk.logger import logger
except Exception:
    import logging
    logger = logging.getLogger("risk_app")
    if not logger.handlers:
        logging.basicConfig(level=logging.INFO)

# ---------------------------
# Flask app initialization
# ---------------------------
app = Flask(__name__)

# ---------------------------
# Utilities: PDF creation (table + charts)
# ---------------------------
def _create_risk_bar_chart_png(risk30, risk60, risk90):
    """
    Returns PNG bytes for a simple bar chart of 30/60/90 day risks.
    """
    fig, ax = plt.subplots(figsize=(6, 3.5))
    labels = ['30-day', '60-day', '90-day']
    values = [risk30 if risk30 is not None else 0,
              risk60 if risk60 is not None else 0,
              risk90 if risk90 is not None else 0]
    ax.bar(labels, values)
    ax.set_ylim(0, max(100, max(values) * 1.1))
    ax.set_ylabel('Risk (%)')
    ax.set_title('Predicted Risk over Time')
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

def _create_label_pie_chart_png(risk_label):
    """
    Small pie or icon-like chart to visualize risk label emphasis.
    If label not numeric, make a one-slice pie with label in title.
    """
    labels = [risk_label if risk_label else 'Unknown']
    sizes = [1]
    fig, ax = plt.subplots(figsize=(4, 2.5))
    ax.pie(sizes, labels=labels, startangle=90, wedgeprops=dict(width=0.5))
    ax.set_title('Risk Level')
    plt.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return buf.getvalue()

def create_patient_pdf_bytes(patient: dict, include_large_table: bool = True):
    """
    Build a PDF report for a single patient and return bytes.
    - patient: dict-like with keys (DESYNPUF_ID, AGE, GENDER, EMAIL, RISK_30D, RISK_60D, RISK_90D,
      RISK_LABEL, TOP_3_FEATURES, AI_RECOMMENDATIONS, TOTAL_CLAIMS_COST)
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, alignment=TA_CENTER, spaceAfter=14)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=12, alignment=TA_LEFT, spaceAfter=8)
    normal = styles['Normal']

    # Title
    title = Paragraph("Patient Risk Assessment Report", title_style)
    elements.append(title)

    # Patient Info block
    gender_str = 'Male' if patient.get('GENDER') == 1 else 'Female'
    info_html = f"""
    <b>Patient Information</b><br/>
    <b>Patient ID:</b> {patient.get('DESYNPUF_ID', 'N/A')}<br/>
    <b>Age:</b> {patient.get('AGE', 'N/A')}<br/>
    <b>Gender:</b> {gender_str}<br/>
    <b>Email:</b> {patient.get('EMAIL', 'Not Provided')}<br/>
    <b>Total Claims Cost:</b> {patient.get('TOTAL_CLAIMS_COST', 'N/A')}<br/>
    <b>Report Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    elements.append(Paragraph(info_html, normal))
    elements.append(Spacer(1, 12))

    # Risk summary table
    risk_30 = patient.get('RISK_30D', 'N/A')
    risk_60 = patient.get('RISK_60D', 'N/A')
    risk_90 = patient.get('RISK_90D', 'N/A')
    label = patient.get('RISK_LABEL', 'N/A')
    top_feats = patient.get('TOP_3_FEATURES', 'N/A')

    table_data = [
        ['Metric', 'Value'],
        ['30-Day Risk (%)', f"{risk_30}"],
        ['60-Day Risk (%)', f"{risk_60}"],
        ['90-Day Risk (%)', f"{risk_90}"],
        ['Risk Label', str(label)],
        ['Top Features', str(top_feats)]
    ]
    table = Table(table_data, colWidths=[2.5 * inch, 3.5 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d3d3d3")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc"))
    ]))
    elements.append(table)
    elements.append(Spacer(1, 14))

    # Charts
    try:
        bar_png = _create_risk_bar_chart_png(
            risk30=(risk_30 if isinstance(risk_30, (int, float)) else (float(risk_30) if str(risk_30).replace('.', '', 1).isdigit() else 0)),
            risk60=(risk_60 if isinstance(risk_60, (int, float)) else (float(risk_60) if str(risk_60).replace('.', '', 1).isdigit() else 0)),
            risk90=(risk_90 if isinstance(risk_90, (int, float)) else (float(risk_90) if str(risk_90).replace('.', '', 1).isdigit() else 0))
        )
        pie_png = _create_label_pie_chart_png(label)
        # Put images side-by-side: reportlab doesn't have native side-by-side flow, so put one then the other
        bar_img = Image(io.BytesIO(bar_png), width=6 * inch, height=3 * inch)
        elements.append(bar_img)
        elements.append(Spacer(1, 8))
        pie_img = Image(io.BytesIO(pie_png), width=3.5 * inch, height=2.5 * inch)
        elements.append(pie_img)
        elements.append(Spacer(1, 12))
    except Exception as chart_err:
        logger.error(f"Chart generation error: {chart_err}")
        elements.append(Paragraph("Charts unavailable due to rendering error.", normal))
        elements.append(Spacer(1, 8))

    # AI Recommendations section
    recommendations = patient.get('AI_RECOMMENDATIONS', 'No recommendations available')
    elements.append(Paragraph("<b>AI-Generated Recommendations:</b>", h2_style))
    elements.append(Paragraph(str(recommendations), normal))
    elements.append(Spacer(1, 12))

    # Optional larger table: if you have extra metrics, include them
    if include_large_table and isinstance(patient.get('EXTRA_TABLE'), list):
        # patient['EXTRA_TABLE'] expected as list of rows (list of lists)
        try:
            elements.append(Paragraph("<b>Detailed Metrics:</b>", h2_style))
            big_table = Table(patient['EXTRA_TABLE'], repeatRows=1)
            big_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#efefef")),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]))
            elements.append(big_table)
            elements.append(Spacer(1, 12))
        except Exception:
            pass

    # Footer
    elements.append(Spacer(1, 16))
    elements.append(Paragraph("Generated by Risk Stratification System", styles['Italic']))

    # Build PDF
    try:
        doc.build(elements)
    except Exception as build_err:
        logger.error(f"PDF build failed: {build_err}\n{traceback.format_exc()}")
        raise

    buffer.seek(0)
    return buffer.getvalue()

# ---------------------------
# Database helpers (safer parameterized queries)
# ---------------------------
def read_patient_by_id(patient_id: str):
    engine = get_engine()
    query = text("SELECT * FROM training WHERE DESYNPUF_ID = :pid")
    try:
        df = pd.read_sql(query, engine, params={"pid": patient_id})
        return df
    except Exception as e:
        logger.error(f"DB read error for patient {patient_id}: {e}")
        return pd.DataFrame()

# ---------------------------
# Flask endpoints
# ---------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    limit = request.args.get('limit', default=10, type=int)
    engine = get_engine()
    query = text("""
        SELECT DESYNPUF_ID, AGE, GENDER, TOTAL_CLAIMS_COST, 
               RISK_30D, RISK_60D, RISK_90D, RISK_LABEL, TOP_3_FEATURES, AI_RECOMMENDATIONS, EMAIL
        FROM training
        ORDER BY RISK_30D DESC
        LIMIT :limit
    """)
    try:
        df = pd.read_sql(query, engine, params={"limit": limit})
    except Exception as e:
        logger.error(f"Failed to load data: {e}")
        return jsonify({'error': 'Failed to load data'}), 500

    if df.empty:
        return jsonify({'data': []})

    def row_to_dict(row):
        gender_val = row.get('GENDER')
        if pd.isna(gender_val):
            gender = 'Unknown'
        else:
            gender = 'Male' if int(gender_val) == 1 else 'Female'
        return {
            'patient_id': str(row.get('DESYNPUF_ID')),
            'age': int(row.get('AGE')) if pd.notna(row.get('AGE')) else None,
            'gender': gender,
            'claims_cost': float(row.get('TOTAL_CLAIMS_COST')) if pd.notna(row.get('TOTAL_CLAIMS_COST')) else 0.0,
            'risk_30d': float(row.get('RISK_30D')) if pd.notna(row.get('RISK_30D')) else None,
            'risk_60d': float(row.get('RISK_60D')) if pd.notna(row.get('RISK_60D')) else None,
            'risk_90d': float(row.get('RISK_90D')) if pd.notna(row.get('RISK_90D')) else None,
            'risk_label': str(row.get('RISK_LABEL')) if pd.notna(row.get('RISK_LABEL')) else 'Unknown',
            'top_features': str(row.get('TOP_3_FEATURES')) if pd.notna(row.get('TOP_3_FEATURES')) else 'N/A',
            'ai_recommendations': str(row.get('AI_RECOMMENDATIONS')) if pd.notna(row.get('AI_RECOMMENDATIONS')) else 'N/A',
            'email': str(row.get('EMAIL')) if pd.notna(row.get('EMAIL')) else ''
        }

    data = [row_to_dict(r) for _, r in df.iterrows()]
    return jsonify({'data': data})

@app.route('/api/summary')
def api_summary():
    engine = get_engine()
    query = text("""
        SELECT 
            COUNT(*) as total_patients,
            AVG(RISK_30D) as avg_risk_30d,
            AVG(RISK_60D) as avg_risk_60d,
            AVG(RISK_90D) as avg_risk_90d,
            COUNT(CASE WHEN RISK_LABEL = 'Very High Risk' THEN 1 END) as very_high_risk,
            COUNT(CASE WHEN RISK_LABEL = 'High Risk' THEN 1 END) as high_risk,
            COUNT(CASE WHEN RISK_LABEL = 'Moderate Risk' THEN 1 END) as moderate_risk,
            COUNT(CASE WHEN RISK_LABEL = 'Low Risk' THEN 1 END) as low_risk,
            COUNT(CASE WHEN RISK_LABEL = 'Very Low Risk' THEN 1 END) as very_low_risk
        FROM training
    """)
    try:
        df = pd.read_sql(query, engine)
        if df.empty:
            return jsonify({})
        return jsonify(df.iloc[0].to_dict())
    except Exception as e:
        logger.error(f"Summary query failed: {e}")
        return jsonify({})

@app.route('/api/health')
def api_health():
    # Simple DB check
    try:
        engine = get_engine()
        # Keep a cheap query
        _ = engine.execute(text("SELECT 1")).fetchone()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({'status': 'unhealthy', 'database': 'disconnected'}), 500

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    Predict for a single patient. If email exists, generate a PDF and send it as an attachment.
    Handles new patients (DESYNPUF_ID starts with 'NEW_') by inserting them into DB if needed.
    """
    try:
        data = request.json or {}
        desynpuf_id = data.get('DESYNPUF_ID')
        engine = get_engine()

        # New patient flow
        if desynpuf_id and str(desynpuf_id).startswith('NEW_'):
            try:
                # Ensure prediction columns exist if helper exists
                try:
                    from risk.db import ensure_prediction_columns
                    ensure_prediction_columns("trainingk")
                except Exception:
                    # non-fatal
                    pass

                # Save provided data as a new row
                # Convert to DataFrame and append
                new_df = pd.DataFrame([data])
                new_df.to_sql('training', engine, if_exists='append', index=False)
                logger.info(f"Inserted new patient {desynpuf_id} into database.")

                # Predict
                model = load_model("models/risk_model.pkl")
                preds = predict_batch(new_df, model)
                # Update DB with predictions (if helper exists)
                try:
                    from risk.db import update_predictions_in_db
                    update_predictions_in_db(preds, "trainingk")
                except Exception:
                    logger.warning("update_predictions_in_db not available or failed; predictions may not be persisted.")

                pred_record = preds.iloc[0].to_dict()

                # Prepare patient dict for PDF/email
                patient_dict = {**data, **pred_record}
                pdf_bytes = create_patient_pdf_bytes(patient_dict)
                attachment_name = f"patient_report_{desynpuf_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

                # Send email if email present
                email_addr = data.get('EMAIL')
                if email_addr:
                    message_body = (
                        f"Hello,\n\nPlease find attached the risk prediction report for patient {desynpuf_id}.\n\n"
                        f"Summary:\n30-day: {pred_record.get('RISK_30D')}\n60-day: {pred_record.get('RISK_60D')}\n90-day: {pred_record.get('RISK_90D')}\n"
                        f"Label: {pred_record.get('RISK_LABEL')}\n\nRegards,\nRisk Stratification System"
                    )
                    send_email(email_addr, "Patient Risk Prediction Report", message_body, attachment_bytes=pdf_bytes, attachment_filename=attachment_name)

                return jsonify({'success': True, 'predictions': pred_record, 'message': 'New patient predicted and emailed (if address provided).'})
            except Exception as e:
                logger.error(f"New patient prediction error: {e}\n{traceback.format_exc()}")
                return jsonify({'error': str(e)}), 500

        # Existing patient flow
        if not desynpuf_id:
            return jsonify({'error': 'DESYNPUF_ID is required for existing patient prediction'}), 400

        # Load existing patient row
        query = text("SELECT * FROM training WHERE DESYNPUF_ID = :pid")
        patient_df = pd.read_sql(query, engine, params={"pid": desynpuf_id})
        if patient_df.empty:
            return jsonify({'error': f'Patient {desynpuf_id} not found'}), 404

        # Predict using model
        model = load_model("models/risk_model_20250901_195429.pkl")
        preds = predict_batch(patient_df, model)

        # Attempt to persist predictions
        try:
            from risk.db import update_predictions_in_db
            update_predictions_in_db(preds, "trainingk")
        except Exception:
            logger.warning("update_predictions_in_db not available or failed; predictions may not be persisted.")

        pred_record = preds.iloc[0].to_dict()

        # Build PDF and send as attachment if patient has EMAIL
        patient_dict = patient_df.iloc[0].to_dict()
        patient_dict.update(pred_record)  # merge predictions into patient dict
        pdf_bytes = create_patient_pdf_bytes(patient_dict)
        attachment_name = f"patient_report_{desynpuf_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        patient_email = patient_dict.get('EMAIL')
        if patient_email:
            message_body = (
                f"Hello,\n\nPlease find attached the risk prediction report for patient {desynpuf_id}.\n\n"
                f"Summary:\n30-day: {pred_record.get('RISK_30D')}\n60-day: {pred_record.get('RISK_60D')}\n90-day: {pred_record.get('RISK_90D')}\n"
                f"Label: {pred_record.get('RISK_LABEL')}\n\nRegards,\nRisk Stratification System"
            )
            try:
                send_email(patient_email, "Patient Risk Prediction Report", message_body, attachment_bytes=pdf_bytes, attachment_filename=attachment_name)
            except Exception as mail_err:
                logger.error(f"Failed to send prediction email to {patient_email}: {mail_err}")

        return jsonify({'success': True, 'predictions': pred_record, 'message': f'Predicted for {desynpuf_id} (email sent if address present).'})
    except Exception as e:
        logger.error(f"Prediction endpoint error: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/predict-all', methods=['POST'])
def api_predict_all():
    """
    Predict for all patients missing predictions.
    This endpoint does NOT email attachments by default to avoid sending mass attachments unfiltered.
    """
    try:
        engine = get_engine()
        query = text("""
            SELECT * FROM training
            WHERE RISK_30D IS NULL OR RISK_60D IS NULL OR RISK_90D IS NULL
            OR RISK_LABEL IS NULL OR TOP_3_FEATURES IS NULL
        """)
        df = pd.read_sql(query, engine)
        if df.empty:
            return jsonify({'message': 'All patients already have predictions'})

        model = load_model("models/risk_model_20250901_195429.pkl")
        preds = predict_batch(df, model)
        try:
            from risk.db import update_predictions_in_db_bulk
            update_predictions_in_db_bulk(preds, "trainingk")
        except Exception:
            logger.warning("update_predictions_in_db_bulk not available; bulk predictions not persisted.")

        return jsonify({'success': True, 'message': f'Predictions processed for {len(preds)} patients', 'patients_processed': len(preds)})
    except Exception as e:
        logger.error(f"Bulk predict failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-recommendations-email', methods=['POST'])
def api_send_recommendations_email():
    """
    Send recommendations email to a specific patient.
    If 'as_pdf' boolean is provided and true, send the PDF attachment (preferred).
    """
    try:
        data = request.json or {}
        patient_id = data.get('patient_id')
        as_pdf = bool(data.get('as_pdf', True))
        if not patient_id:
            return jsonify({'error': 'patient_id required'}), 400

        df = read_patient_by_id(patient_id)
        if df.empty:
            return jsonify({'error': f'Patient {patient_id} not found'}), 404
        patient = df.iloc[0].to_dict()
        email = patient.get('EMAIL')
        if not email:
            return jsonify({'error': 'Patient has no email address'}), 400

        # Build message and optionally PDF
        message_body = (
            f"Hello,\n\nThis message contains recommendations for patient {patient_id}.\n\n"
            f"AI Recommendations:\n{patient.get('AI_RECOMMENDATIONS', 'N/A')}\n\nRegards,\nRisk Stratification System"
        )

        if as_pdf:
            pdf_bytes = create_patient_pdf_bytes(patient)
            filename = f"patient_report_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            send_email(email, "Patient Recommendations (PDF)", message_body, attachment_bytes=pdf_bytes, attachment_filename=filename)
            return jsonify({'success': True, 'message': f'PDF recommendations sent to {email}'})
        else:
            send_email(email, "Patient Recommendations", message_body)
            return jsonify({'success': True, 'message': f'Plain-text recommendations sent to {email}'})
    except Exception as e:
        logger.error(f"send_recommendations_email error: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-bulk-emails', methods=['POST'])
def api_send_bulk_emails():
    """
    Send recommendation emails (PDF attachments) to all patients that have EMAIL and AI_RECOMMENDATIONS.
    WARNING: This will generate and send many attachments — use with care.
    Payload can include {"only_high_risk": true} to restrict.
    """
    try:
        data = request.json or {}
        only_high_risk = bool(data.get('only_high_risk', False))
        engine = get_engine()
        if only_high_risk:
            query = text("SELECT * FROM training WHERE RISK_LABEL IN ('Very High Risk','High Risk') AND EMAIL IS NOT NULL AND AI_RECOMMENDATIONS IS NOT NULL")
        else:
            query = text("SELECT * FROM training WHERE EMAIL IS NOT NULL AND AI_RECOMMENDATIONS IS NOT NULL")
        df = pd.read_sql(query, engine)
        if df.empty:
            return jsonify({'message': 'No patients matched criteria'})

        success = 0
        total = len(df)
        for _, row in df.iterrows():
            try:
                patient = row.to_dict()
                email = patient.get('EMAIL')
                if not email:
                    continue
                pdf_bytes = create_patient_pdf_bytes(patient)
                filename = f"patient_report_{patient.get('DESYNPUF_ID')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                message_body = f"Hello,\n\nAttached is the patient risk report for {patient.get('DESYNPUF_ID')}.\n\nRegards,\nRisk Stratification System"
                send_email(email, "Patient Risk Report", message_body, attachment_bytes=pdf_bytes, attachment_filename=filename)
                success += 1
            except Exception as e:
                logger.error(f"Failed to send to {row.get('DESYNPUF_ID')} ({row.get('EMAIL')}): {e}")
                continue

        return jsonify({'success': True, 'message': f'Emails sent to {success}/{total} patients', 'emails_sent': success, 'total': total})
    except Exception as e:
        logger.error(f"Bulk send failed: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/update-patient-email', methods=['POST'])
def api_update_patient_email():
    try:
        data = request.json or {}
        patient_id = data.get('patient_id')
        email = data.get('email')
        if not patient_id or not email:
            return jsonify({'error': 'patient_id and email required'}), 400
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return jsonify({'error': 'invalid email format'}), 400

        try:
            from risk.db import update_patient_email
            success = update_patient_email(patient_id, email)
        except Exception:
            # fallback SQL update
            try:
                engine = get_engine()
                engine.execute(text("UPDATE risk_score SET EMAIL = :email WHERE DESYNPUF_ID = :pid"), {"email": email, "pid": patient_id})
                success = True
            except Exception as up_err:
                logger.error(f"Failed to update email in DB fallback: {up_err}")
                success = False

        if success:
            return jsonify({'success': True, 'message': f'Email updated for {patient_id}'})
        return jsonify({'success': False, 'error': 'failed to update email'}), 500
    except Exception as e:
        logger.error(f"update_patient_email endpoint error: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/export-patient-pdf/<patient_id>')
def api_export_patient_pdf(patient_id):
    try:
        df = read_patient_by_id(patient_id)
        if df.empty:
            return jsonify({'error': f'Patient {patient_id} not found'}), 404
        patient = df.iloc[0].to_dict()
        pdf_bytes = create_patient_pdf_bytes(patient)
        filename = f"patient_recommendations_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        return send_file(io.BytesIO(pdf_bytes), as_attachment=True, download_name=filename, mimetype='application/pdf')
    except Exception as e:
        logger.error(f"export PDF error: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/send-pdf-email', methods=['POST'])
def api_send_pdf_email():
    try:
        data = request.json or {}
        patient_id = data.get('patient_id')
        if not patient_id:
            return jsonify({'error': 'patient_id required'}), 400
        df = read_patient_by_id(patient_id)
        if df.empty:
            return jsonify({'error': f'Patient {patient_id} not found'}), 404
        patient = df.iloc[0].to_dict()
        email = patient.get('EMAIL')
        if not email:
            return jsonify({'error': 'Patient has no email'}), 400
        pdf_bytes = create_patient_pdf_bytes(patient)
        filename = f"patient_report_{patient_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        message_body = f"Hello,\n\nAttached is the patient risk assessment report for {patient_id}.\n\nRegards,\nRisk Stratification System"
        send_email(email, "Patient Risk Assessment Report", message_body, attachment_bytes=pdf_bytes, attachment_filename=filename)
        return jsonify({'success': True, 'message': f'PDF sent to {email}'})
    except Exception as e:
        logger.error(f"send_pdf_email endpoint error: {e}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

# ---------------------------
# App run
# ---------------------------
if __name__ == '__main__':
    # ensure templates directory
    os.makedirs('templates', exist_ok=True)
    # Print endpoints for convenience
    print("🚀 Starting Risk Stratification Web App...")
    print("📊 Dashboard: http://localhost:5000")
    print("API endpoints:")
    print(" - /api/data")
    print(" - /api/summary")
    print(" - /api/health")
    print(" - /api/predict (POST)")
    print(" - /api/predict-all (POST)")
    print(" - /api/send-recommendations-email (POST)")
    print(" - /api/send-bulk-emails (POST)")
    print(" - /api/update-patient-email (POST)")
    print(" - /api/export-patient-pdf/<patient_id>")
    print(" - /api/send-pdf-email (POST)")

    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 5000)), debug=True)