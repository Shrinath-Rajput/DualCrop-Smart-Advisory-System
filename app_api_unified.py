"""
Flask API Integration for Crop Disease Prediction
==================================================

Provides REST API endpoints for disease prediction with:
- File upload handling
- JSON response format
- Comprehensive error handling
- Production-ready error codes
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from predict import CropDiseasePredictor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create upload folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize predictor globally
try:
    predictor = CropDiseasePredictor()
    PREDICTOR_READY = True
    logger.info("✓ Disease predictor initialized")
except Exception as e:
    logger.error(f"Failed to initialize predictor: {e}")
    predictor = None
    PREDICTOR_READY = False


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html', model_ready=PREDICTOR_READY)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok' if PREDICTOR_READY else 'error',
        'model_ready': PREDICTOR_READY,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/predict', methods=['POST'])
def predict():
    """Main prediction endpoint"""
    
    try:
        # Check predictor is ready
        if not PREDICTOR_READY:
            return jsonify({
                'success': False,
                'error': 'ModelNotReady',
                'message': 'Disease prediction model not initialized. Please run training first.',
                'timestamp': datetime.now().isoformat()
            }), 503
        
        # Check for file in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'NoFileProvided',
                'message': 'No file provided in request. Use multipart/form-data with "file" field.',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'EmptyFilename',
                'message': 'No file selected',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Check file extension
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'InvalidFileType',
                'message': f'File type not allowed. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"File uploaded: {filepath}")
        
        # Run prediction
        logger.info(f"Running prediction on: {filepath}")
        result = predictor.predict(filepath)
        
        # Add metadata
        result['timestamp'] = datetime.now().isoformat()
        result['file'] = filename
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
            logger.info(f"Cleaned up: {filepath}")
        except:
            pass
        
        return jsonify(result), 200 if result.get('success') else 400
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': 'InternalError',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@app.route('/api/info', methods=['GET'])
def info():
    """Get system information"""
    return jsonify({
        'system': 'Unified Crop Disease Prediction System',
        'version': '2.0.0',
        'models': {
            'classes': predictor.class_names if PREDICTOR_READY else [],
            'num_classes': len(predictor.class_names) if PREDICTOR_READY else 0,
            'model_ready': PREDICTOR_READY
        },
        'supported_crops': ['Brinjal', 'Grapes'],
        'supported_extensions': list(ALLOWED_EXTENSIONS),
        'max_file_size_mb': MAX_FILE_SIZE / (1024 * 1024),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    return jsonify({
        'success': False,
        'error': 'FileTooLarge',
        'message': f'File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024)}MB',
        'timestamp': datetime.now().isoformat()
    }), 413


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'NotFound',
        'message': 'Endpoint not found',
        'timestamp': datetime.now().isoformat()
    }), 404


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'ServerError',
        'message': 'Internal server error',
        'timestamp': datetime.now().isoformat()
    }), 500


def run_api(host='0.0.0.0', port=5000, debug=False):
    """Run Flask API server"""
    logger.info(f"Starting API server on {host}:{port}")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == '__main__':
    import sys
    
    # Check if model is ready
    if not PREDICTOR_READY:
        print("❌ Model not ready. Please train the model first:")
        print("   python train_unified.py")
        sys.exit(1)
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    run_api(port=port, debug=debug)
