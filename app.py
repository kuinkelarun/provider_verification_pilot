"""
Flask Provider Verification Dashboard
Main application file for Databricks-hosted provider data verification UI
"""

# Ensure the current directory is in the Python path (fix for Databricks Apps)
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, jsonify, send_file, after_this_request
import pandas as pd
import json
import tempfile
from datetime import datetime
from utils.data_formatter import parse_json_data, format_results_for_display
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize Databricks connector (if enabled)
databricks = None
databricks_enabled = os.getenv('ENABLE_DATABRICKS', 'false').lower() == 'true'

if databricks_enabled:
    try:
        from utils.databricks_connector import DatabricksConnector
        
        catalogs = os.getenv('DATABRICKS_CATALOGS', '').split(',') if os.getenv('DATABRICKS_CATALOGS') else []
        schemas = os.getenv('DATABRICKS_SCHEMAS', '').split(',') if os.getenv('DATABRICKS_SCHEMAS') else []
        
        databricks = DatabricksConnector(
            host=os.getenv('DATABRICKS_HOST'),
            token=os.getenv('DATABRICKS_TOKEN'),
            http_path=os.getenv('DATABRICKS_HTTP_PATH'),
            catalogs=catalogs,
            schemas=schemas,
            table_pattern=os.getenv('DATABRICKS_TABLE_PATTERN'),
            cache_duration=int(os.getenv('DATABRICKS_CACHE_DURATION', '5'))
        )
        print("✅ Databricks connector initialized")
    except Exception as e:
        print(f"⚠️  Databricks connector failed to initialize: {str(e)}")
        databricks_enabled = False


@app.route('/')
def index():
    """Render upload list from csv_upload_details table (landing page)."""
    # Load csv_upload_details from Databricks
    if not databricks:
        return render_template('error.html', 
                             error='Databricks connection not configured. Please check .env file.'), 500
    
    try:
        # Load csv_upload_details table
        upload_data = databricks.load_table_data('databricks_poc.default.csv_upload_details')
        
        # Sort by upload_time (most recent first)
        upload_data.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
        
        return render_template('upload_list.html', uploads=upload_data)
        
    except Exception as e:
        print(f"❌ Error loading csv_upload_details: {str(e)}")
        import traceback
        traceback.print_exc()
        return render_template('error.html', 
                             error=f'Failed to load upload history: {str(e)}'), 500


@app.route('/dashboard')
def dashboard():
    """
    Render dashboard with provider data dynamically discovered by csv_file_id.
    Searches all tables in the schema to find the one containing the csv_file_id.
    """
    try:
        csv_file_id = request.args.get('csv_file_id')
        
        if not csv_file_id:
            return render_template('error.html', 
                                 error='Missing csv_file_id parameter. Please select a file from the upload list.'), 400
        
        if not databricks:
            return render_template('error.html', 
                                 error='Databricks connection not configured.'), 500
        
        # Dynamically find which table contains this csv_file_id
        try:
            print(f"Searching for table containing csv_file_id: {csv_file_id}")
            
            # Get all tables in the schema
            all_tables = databricks.list_available_tables()
            
            target_table = None
            table_data = None
            
            # Search through tables to find one with this csv_file_id
            for table_info in all_tables:
                table_name = table_info['full_name']
                
                # Skip the csv_upload_details table itself
                if 'csv_upload_details' in table_name:
                    continue
                
                try:
                    # Try to query this table with the csv_file_id filter
                    print(f"Checking table: {table_name}")
                    data = databricks.load_table_data(table_name, csv_file_id=csv_file_id, limit=1)
                    
                    if data and len(data) > 0:
                        # Found the table with this csv_file_id!
                        target_table = table_name
                        print(f"Found data in table: {target_table}")
                        # Load all data from this table for this csv_file_id
                        table_data = databricks.load_table_data(target_table, csv_file_id=csv_file_id)
                        break
                except Exception as e:
                    # This table might not have csv_file_id column, skip it
                    continue
            
            if not target_table or not table_data:
                return render_template('error.html', 
                                     error=f'No table found containing data for csv_file_id: {csv_file_id}. Please ensure the batch has been processed and data exists in a table.'), 404
                    
        except Exception as e:
            return render_template('error.html', 
                                 error=f'Failed to search for table with csv_file_id {csv_file_id}: {str(e)}'), 500
        
        # Parse the JSON data from Databricks
        parsed_data, errors = parse_json_data(table_data)
        
        if not parsed_data:
            return render_template('error.html', 
                                 error='No valid provider data found after parsing.'), 404
        
        # Format for display
        formatted_results = format_results_for_display(parsed_data)
        
        # Calculate summary metrics
        summary = {
            'total': len(formatted_results),
            'verified': sum(1 for r in formatted_results if r.get('status') == 'verified'),
            'review': sum(1 for r in formatted_results if r.get('status') == 'needs_review'),
            'failed': sum(1 for r in formatted_results if r.get('status') == 'failed')
        }
        
        # Get unique cities for filters
        cities = sorted(set(r.get('city', '') for r in formatted_results if r.get('city')))
        
        # Create a single "file" entry for the filter dropdown
        uploaded_files = [{
            'id': f'databricks_{csv_file_id}',
            'filename': f'CSV File ID: {csv_file_id}'
        }]
        
        return render_template('dashboard.html', 
                             results=formatted_results, 
                             summary=summary,
                             uploaded_files=uploaded_files,
                             files_loaded=f'CSV File ID: {csv_file_id}',
                             cities=cities,
                             current_file_id=f'databricks_{csv_file_id}',
                             csv_file_id=csv_file_id)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return render_template('error.html', error=str(e)), 500


@app.route('/export')
def export_results():
    """Export results to CSV for current dashboard view."""
    try:
        csv_file_id = request.args.get('csv_file_id')
        
        if not csv_file_id:
            return jsonify({'error': 'Missing csv_file_id parameter'}), 400
        
        if not databricks:
            return jsonify({'error': 'Databricks connection not configured'}), 500
        
        # Dynamically find which table contains this csv_file_id (same logic as dashboard)
        try:
            all_tables = databricks.list_available_tables()
            
            target_table = None
            table_data = None
            
            for table_info in all_tables:
                table_name = table_info['full_name']
                
                if 'csv_upload_details' in table_name:
                    continue
                
                try:
                    data = databricks.load_table_data(table_name, csv_file_id=csv_file_id, limit=1)
                    if data and len(data) > 0:
                        target_table = table_name
                        table_data = databricks.load_table_data(target_table, csv_file_id=csv_file_id)
                        break
                except:
                    continue
            
            if not target_table or not table_data:
                return jsonify({'error': f'No table found containing data for csv_file_id {csv_file_id}'}), 404
        except Exception as e:
            return jsonify({'error': f'Failed to search for table: {str(e)}'}), 500
        
        # Parse and format data
        parsed_data, _ = parse_json_data(table_data)
        formatted_results = format_results_for_display(parsed_data)
        
        # Convert to DataFrame
        df = pd.DataFrame(formatted_results)
        
        # Create temporary file for export
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'providers_{csv_file_id[:20]}_{timestamp}.csv'
        
        # Use temporary directory
        temp_dir = tempfile.gettempdir()
        output_path = os.path.join(temp_dir, filename)
        
        # Export to CSV
        df.to_csv(output_path, index=False)
        
        # Cleanup: Delete temporary file after sending
        @after_this_request
        def remove_file(response):
            try:
                os.remove(output_path)
                print(f"Cleaned up temporary file: {output_path}")
            except Exception as e:
                print(f"Error removing temporary file {output_path}: {str(e)}")
            return response
        
        return send_file(output_path, 
                        as_attachment=True, 
                        download_name=filename)
    
    except Exception as e:
        return jsonify({'error': f'Export failed: {str(e)}'}), 500


# REMOVED: load_databricks_table endpoint
# This endpoint was used to download Databricks data to local storage (data_storage folder)
# No longer needed since we query Databricks directly on each dashboard load
# If you need to restore it, uncomment below:

# @app.route('/load-databricks-table', methods=['POST'])
# def load_databricks_table():
#     """Load data from a Databricks table and save to local storage."""
#     if not databricks:
#         return jsonify({'success': False, 'error': 'Databricks not configured'}), 400
#     
#     try:
#         data = request.get_json()
#         table_name = data.get('table_name')
#         
#         if not table_name:
#             return jsonify({'success': False, 'error': 'table_name required'}), 400
#         
#         # Load data from Databricks
#         print(f"Loading table: {table_name}")
#         table_data = databricks.load_table_data(table_name, limit=100000)  # Limit to 100k rows
#         
#         # Format data for dashboard
#         # Use parse_json_data since Databricks table has JSON structure with source_npi, confidence_measure, etc.
#         formatted_data, validation_errors = parse_json_data(table_data)
#         
#         if validation_errors:
#             return jsonify({
#                 'success': False,
#                 'error': 'Data validation failed',
#                 'details': validation_errors
#             }), 400
#         
#         # Generate unique file ID
#         file_id = f"databricks_{table_name.replace('.', '_')}_{int(datetime.now().timestamp())}"
#         upload_timestamp = datetime.now().isoformat()
#         
#         # Store file metadata
#         file_metadata = {
#             'file_id': file_id,
#             'filename': f"Databricks: {table_name}",
#             'source': 'databricks',
#             'table_name': table_name,
#             'uploaded_at': upload_timestamp,
#             'total_rows': len(formatted_data)
#         }
#         
#         # Save data to persistent storage
#         data_file = os.path.join(app.config['DATA_STORAGE'], f'{file_id}.json')
#         with open(data_file, 'w') as f:
#             json.dump({
#                 'metadata': file_metadata,
#                 'data': formatted_data
#             }, f)
#         
#         # Update file history
#         history_file = os.path.join(app.config['DATA_STORAGE'], 'upload_history.json')
#         history = []
#         if os.path.exists(history_file):
#             with open(history_file, 'r') as f:
#                 history = json.load(f)
#         
#         history.append(file_metadata)
#         
#         with open(history_file, 'w') as f:
#             json.dump(history, f)
#         
#         return jsonify({
#             'success': True,
#             'file_id': file_id,
#             'total_rows': len(formatted_data)
#         })
#         
#     except Exception as e:
#         print(f"Error loading Databricks table: {str(e)}")
#         return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/download-template')
def download_template():
    """Download CSV template file."""
    template_data = {
        'Provider Name': ['Dr. John Smith', 'Dr. Jane Doe'],
        'NPI': ['1234567890', '9876543210'],
        'Address': ['123 Main St', '456 Oak Ave'],
        'City': ['Boston', 'Cambridge'],
        'State': ['MA', 'MA'],
        'ZIP Code': ['02101', '02139'],
        'Specialty': ['Cardiology', 'Pediatrics'],
        'Phone': ['617-555-0100', '617-555-0200']
    }
    
    df = pd.DataFrame(template_data)
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'provider_template.csv')
    df.to_csv(output_path, index=False)
    
    return send_file(output_path, 
                    as_attachment=True, 
                    download_name='provider_data_template.csv')


@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check Databricks connection
        databricks_status = 'connected' if databricks else 'not configured'
        
        return jsonify({
            'status': 'healthy',
            'databricks': databricks_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


if __name__ == '__main__':
    # For local development
    app.run(host='0.0.0.0', port=8080, debug=True)
