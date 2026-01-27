#!/usr/bin/env python3
"""
Web API for Audience Cleaner
Handles large file uploads and processing via streaming to avoid memory issues
"""

import os
import csv
import re
import tempfile
import base64
from pathlib import Path
from flask import Flask, request, jsonify, send_file, send_from_directory

# Optional CORS support
try:
    from flask_cors import CORS
    CORS_AVAILABLE = True
except ImportError:
    CORS_AVAILABLE = False
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import uuid

app = Flask(__name__, static_folder='static')
if CORS_AVAILABLE:
    CORS(app)  # Enable CORS for cross-origin requests
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1GB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
app.config['OUTPUT_FOLDER'] = tempfile.gettempdir()

# Import cleaning functions - define inline to avoid import issues
import re

def clean_phone(phone_str):
    """Extract and clean the first phone number from a string."""
    if not phone_str or phone_str.strip() == '':
        return ''
    phones = phone_str.split(',')
    if not phones:
        return ''
    first_phone = phones[0].strip()
    cleaned = re.sub(r'[^\d]', '', first_phone)
    if len(cleaned) == 11 and cleaned.startswith('1'):
        cleaned = cleaned[1:]
    return cleaned

def extract_first_email(email_str):
    """Extract the first email from a comma-separated list."""
    if not email_str or email_str.strip() == '':
        return ''
    emails = email_str.split(',')
    if not emails:
        return ''
    return emails[0].strip()

def clean_income_range(income_str):
    """Replace commas with spaces in income range strings."""
    if not income_str or income_str.strip() == '':
        return ''
    return income_str.replace(',', ' ')

def get_primary_phone(row):
    """Get primary phone from DIRECT_NUMBER, MOBILE_PHONE, or PERSONAL_PHONE."""
    if row.get('DIRECT_NUMBER'):
        phone = clean_phone(row['DIRECT_NUMBER'])
        if phone:
            return phone
    if row.get('MOBILE_PHONE'):
        phone = clean_phone(row['MOBILE_PHONE'])
        if phone:
            return phone
    if row.get('PERSONAL_PHONE'):
        phone = clean_phone(row['PERSONAL_PHONE'])
        if phone:
            return phone
    return ''

def get_primary_email(row):
    """Get primary email from BUSINESS_EMAIL or first from PERSONAL_EMAILS."""
    # Try BUSINESS_EMAIL first
    if row.get('BUSINESS_EMAIL') and row['BUSINESS_EMAIL'].strip():
        business_email = row['BUSINESS_EMAIL'].strip()
        # Extract first email if it contains multiple emails
        return extract_first_email(business_email)
    
    # Try PERSONAL_EMAILS
    if row.get('PERSONAL_EMAILS'):
        email = extract_first_email(row['PERSONAL_EMAILS'])
        if email:
            return email
    return ''


def process_csv_streaming(input_path, output_path, preview_rows=10):
    """Process CSV file using streaming to handle large files.
    Returns (rows_processed, preview_data) where preview_data is a list of dicts."""
    output_columns = [
        'FIRST_NAME', 'LAST_NAME', 'PRIMARY_PHONE', 'PRIMARY_EMAIL',
        'Personal_Phone', 'Mobile_Phone', 'Valid_Phone', 'UUID',
        'PERSONAL_CITY', 'PERSONAL_STATE', 'AGE_RANGE', 'CHILDREN',
        'GENDER', 'HOMEOWNER', 'MARRIED', 'NET_WORTH', 'INCOME_RANGE',
        'LINKEDIN_URL'
    ]
    
    rows_processed = 0
    preview_data = []
    
    try:
        with open(input_path, 'r', encoding='utf-8', errors='replace') as infile:
            # Detect delimiter
            sample = infile.read(1024)
            infile.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(infile, delimiter=delimiter)
            
            with open(output_path, 'w', encoding='utf-8', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_columns)
                writer.writeheader()
                
                for row in reader:
                    # Get primary phone
                    primary_phone = get_primary_phone(row)
                    
                    # Get personal and mobile phones
                    personal_phone = clean_phone(row.get('PERSONAL_PHONE', ''))
                    mobile_phone = clean_phone(row.get('MOBILE_PHONE', ''))
                    
                    # Get primary email
                    primary_email = get_primary_email(row)
                    
                    # Clean income ranges
                    net_worth = clean_income_range(row.get('NET_WORTH', ''))
                    income_range = clean_income_range(row.get('INCOME_RANGE', ''))
                    
                    # Get LinkedIn URL (try common column name variations)
                    linkedin_url = (row.get('LINKEDIN_URL', '') or 
                                   row.get('LinkedIn_URL', '') or 
                                   row.get('LINKEDIN', '') or 
                                   row.get('LinkedIn', '') or 
                                   row.get('linkedin_url', '') or '').strip()
                    
                    # Build output row
                    output_row = {
                        'FIRST_NAME': row.get('FIRST_NAME', ''),
                        'LAST_NAME': row.get('LAST_NAME', ''),
                        'PRIMARY_PHONE': primary_phone,
                        'PRIMARY_EMAIL': primary_email,
                        'Personal_Phone': personal_phone,
                        'Mobile_Phone': mobile_phone,
                        'Valid_Phone': primary_phone,
                        'UUID': row.get('UUID', ''),
                        'PERSONAL_CITY': row.get('PERSONAL_CITY', ''),
                        'PERSONAL_STATE': row.get('PERSONAL_STATE', ''),
                        'AGE_RANGE': row.get('AGE_RANGE', ''),
                        'CHILDREN': row.get('CHILDREN', ''),
                        'GENDER': row.get('GENDER', ''),
                        'HOMEOWNER': row.get('HOMEOWNER', ''),
                        'MARRIED': row.get('MARRIED', ''),
                        'NET_WORTH': net_worth,
                        'INCOME_RANGE': income_range,
                        'LINKEDIN_URL': linkedin_url
                    }
                    
                    writer.writerow(output_row)
                    rows_processed += 1
                    
                    # Collect preview data (first N rows)
                    if len(preview_data) < preview_rows:
                        preview_data.append(output_row)
        
        return rows_processed, preview_data
    
    except Exception as e:
        raise Exception(f"Error processing file: {str(e)}")


@app.route('/')
def index():
    """Serve web interface or API documentation."""
    # Try to serve HTML interface if it exists
    html_path = os.path.join(os.path.dirname(__file__), 'static', 'index.html')
    if os.path.exists(html_path):
        return send_from_directory(os.path.dirname(html_path), 'index.html')
    
    # Otherwise return API documentation
    return jsonify({
        'name': 'Audience Cleaner API',
        'version': '1.0.0',
        'endpoints': {
            '/upload': {
                'method': 'POST',
                'description': 'Upload and process a CSV file',
                'parameters': {
                    'file': 'CSV file to process (multipart/form-data)'
                },
                'returns': 'Processed CSV file'
            },
            '/health': {
                'method': 'GET',
                'description': 'Check API health status'
            }
        },
        'max_file_size': '1GB',
        'note': 'Files are processed using streaming to handle large files efficiently'
    })


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'audience-cleaner-api'
    })


@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload and processing."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith('.csv'):
        return jsonify({'error': 'File must be a CSV file'}), 400
    
    # Generate unique filenames
    file_id = str(uuid.uuid4())
    input_filename = secure_filename(f"{file_id}_input.csv")
    output_filename = secure_filename(f"{file_id}_cleaned.csv")
    
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], input_filename)
    output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
    
    try:
        # Save uploaded file
        file.save(input_path)
        
        # Process the file (streaming, memory-efficient)
        rows_processed, preview_data = process_csv_streaming(input_path, output_path)
        
        # Read the processed file for download
        with open(output_path, 'rb') as f:
            file_content = f.read()
        
        # Encode file as base64 for JSON response
        file_base64 = base64.b64encode(file_content).decode('utf-8')
        
        # Clean up files
        os.remove(input_path)
        try:
            os.remove(output_path)
        except:
            pass  # File might already be removed or in use
        
        # Return JSON with preview data and file
        return jsonify({
            'success': True,
            'rows_processed': rows_processed,
            'preview': preview_data,
            'columns': [
                'FIRST_NAME', 'LAST_NAME', 'PRIMARY_PHONE', 'PRIMARY_EMAIL',
                'Personal_Phone', 'Mobile_Phone', 'Valid_Phone', 'UUID',
                'PERSONAL_CITY', 'PERSONAL_STATE', 'AGE_RANGE', 'CHILDREN',
                'GENDER', 'HOMEOWNER', 'MARRIED', 'NET_WORTH', 'INCOME_RANGE',
                'LINKEDIN_URL'
            ],
            'file_data': file_base64,
            'filename': f"cleaned_{file.filename}"
        })
    
    except RequestEntityTooLarge:
        return jsonify({'error': 'File too large. Maximum size is 1GB'}), 413
    except RequestEntityTooLarge:
        # Clean up on error
        if os.path.exists(input_path):
            os.remove(input_path)
        return jsonify({'error': 'File too large. Maximum size is 1GB'}), 413
    except Exception as e:
        # Clean up on error
        if os.path.exists(input_path):
            try:
                os.remove(input_path)
            except:
                pass
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass
        
        # Log the error for debugging (in production, you'd use proper logging)
        error_msg = str(e)
        print(f"Error processing file: {error_msg}")
        
        return jsonify({'error': f'Processing failed: {error_msg}'}), 500


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    return jsonify({'error': 'File too large. Maximum size is 1GB'}), 413


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors with JSON response."""
    return jsonify({'error': 'Internal server error. Please try again or contact support.'}), 500


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors with JSON response."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all unhandled exceptions with JSON response."""
    return jsonify({'error': f'An error occurred: {str(e)}'}), 500


if __name__ == '__main__':
    # Run the Flask app
    # Render uses PORT environment variable (defaults to 10000)
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Audience Cleaner API starting on port {port}")
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"📁 Output folder: {app.config['OUTPUT_FOLDER']}")
    print(f"💾 Max file size: 1GB")
    print(f"\nAPI Documentation: http://localhost:{port}/")
    print(f"Health check: http://localhost:{port}/health")
    print(f"Upload endpoint: http://localhost:{port}/upload")
    
    # Use 0.0.0.0 to accept connections from any IP (required for Render)
    app.run(host='0.0.0.0', port=port, debug=debug)

