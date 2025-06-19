from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cadquery as cq
from cadquery import importers, exporters
import os
import tempfile
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)  # Enable CORS for your Next.js frontend

# Configure upload settings
UPLOAD_FOLDER = tempfile.gettempdir()
ALLOWED_EXTENSIONS = {'stp', 'step'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "STP to STL conversion server is running"})

@app.route('/convert', methods=['POST'])
def convert_stp_to_stl():
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only .stp and .step files are allowed'}), 400
        
        # Generate unique filenames
        unique_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        
        # Create temporary file paths
        stp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{original_filename}")
        stl_filename = f"{unique_id}_{original_filename.rsplit('.', 1)[0]}.stl"
        stl_path = os.path.join(app.config['UPLOAD_FOLDER'], stl_filename)
        
        # Save the uploaded STP file
        file.save(stp_path)
        
        try:
            # Import STP file using CadQuery
            workplane = importers.importStep(stp_path)
            
            # Export as STL
            exporters.export(workplane, stl_path)
            
            # Clean up the original STP file
            os.remove(stp_path)
            
            # Return the converted STL file
            def remove_file_after_send(response):
                try:
                    os.remove(stl_path)
                except Exception:
                    pass
                return response
            
            return send_file(
                stl_path,
                as_attachment=True,
                download_name=stl_filename,
                mimetype='application/octet-stream'
            )
            
        except Exception as conversion_error:
            # Clean up files on conversion error
            if os.path.exists(stp_path):
                os.remove(stp_path)
            if os.path.exists(stl_path):
                os.remove(stl_path)
            
            return jsonify({
                'error': f'Conversion failed: {str(conversion_error)}'
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/convert-url', methods=['POST'])
def convert_stp_to_stl_return_url():
    """Alternative endpoint that returns a URL to download the converted file"""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only .stp and .step files are allowed'}), 400
        
        # Generate unique filenames
        unique_id = str(uuid.uuid4())
        original_filename = secure_filename(file.filename)
        
        # Create temporary file paths
        stp_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{unique_id}_{original_filename}")
        stl_filename = f"{unique_id}_{original_filename.rsplit('.', 1)[0]}.stl"
        stl_path = os.path.join(app.config['UPLOAD_FOLDER'], stl_filename)
        
        # Save the uploaded STP file
        file.save(stp_path)
        
        try:
            # Import STP file using CadQuery
            workplane = importers.importStep(stp_path)
            
            # Export as STL
            exporters.export(workplane, stl_path)
            
            # Clean up the original STP file
            os.remove(stp_path)
            
            # Return the download URL
            return jsonify({
                'success': True,
                'download_url': f'/download/{stl_filename}',
                'filename': stl_filename
            })
            
        except Exception as conversion_error:
            # Clean up files on conversion error
            if os.path.exists(stp_path):
                os.remove(stp_path)
            if os.path.exists(stl_path):
                os.remove(stl_path)
            
            return jsonify({
                'error': f'Conversion failed: {str(conversion_error)}'
            }), 500
            
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download endpoint for converted files"""
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        def remove_file_after_send(response):
            try:
                os.remove(file_path)
            except Exception:
                pass
            return response
        
        response = send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
        # Schedule file deletion after sending
        response.call_on_close(lambda: remove_file_after_send(response))
        
        return response
        
    except Exception as e:
        return jsonify({'error': f'Download failed: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting STP to STL conversion server...")
    print("Server will be available at: http://localhost:5000")
    print("Health check: http://localhost:5000/health")
    app.run(debug=True, host='0.0.0.0', port=5000)