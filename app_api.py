"""
FLASK API FOR CROP DISEASE PREDICTION
======================================

Complete REST API for disease prediction with:
- Image upload endpoint
- Real-time prediction
- JSON response
- Error handling
- Logging
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import json
import logging
from datetime import datetime
from pathlib import Path

# Import predictor
from predict_final import CropDiseasePredictor

# ============================================================================
# FLASK APPLICATION SETUP
# ============================================================================

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize predictor (global)
try:
    predictor = CropDiseasePredictor()
    logger.info("✓ Predictor initialized")
except Exception as e:
    logger.error(f"Failed to initialize predictor: {e}")
    predictor = None

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_unique_filename(filename):
    """Generate unique filename"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    name, ext = os.path.splitext(filename)
    return f"{name}_{timestamp}{ext}"

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/', methods=['GET'])
def home():
    """Homepage with API documentation"""
    return jsonify({
        'name': 'Crop Disease Prediction API',
        'version': '1.0',
        'description': 'Advanced crop disease detection using deep learning',
        'endpoints': {
            'POST /api/predict': 'Upload image for disease prediction',
            'GET /health': 'Check API health',
            'GET /classes': 'Get list of supported classes',
            'POST /batch': 'Batch prediction (multiple images)'
        },
        'supported_crops': ['Brinjal', 'Grapes'],
        'image_formats': ['jpg', 'jpeg', 'png', 'gif', 'bmp']
    })

@app.route('/health', methods=['GET'])
def health():
    """Check API health"""
    if predictor is None:
        return jsonify({
            'status': 'error',
            'message': 'Predictor not initialized'
        }), 503
    
    return jsonify({
        'status': 'healthy',
        'predictor_ready': True,
        'classes_loaded': len(predictor.class_names),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/classes', methods=['GET'])
def get_classes():
    """Get supported classes"""
    if predictor is None:
        return jsonify({'error': 'Predictor not initialized'}), 503
    
    return jsonify({
        'total_classes': len(predictor.class_names),
        'classes': predictor.class_names,
        'class_indices': {idx: name for idx, name in enumerate(predictor.class_names)}
    })

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Main prediction endpoint
    
    Expected request:
    - Form data with 'image' file
    
    Returns:
    - JSON with prediction results
    """
    if predictor is None:
        return jsonify({
            'success': False,
            'error': 'Predictor not initialized'
        }), 503
    
    try:
        # Check if file is in request
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image provided',
                'message': 'Please provide an image file with form parameter "image"'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Validate file
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file format',
                'message': f'Allowed formats: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400
        
        # Save file
        filename = get_unique_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        logger.info(f"Received image: {filename}")
        
        # Predict
        logger.info(f"Processing prediction for: {filename}")
        result = predictor.predict(filepath)
        
        # Add metadata
        result['image_filename'] = filename
        result['timestamp'] = datetime.now().isoformat()
        
        # Clean up file if needed (optional)
        # os.remove(filepath)
        
        logger.info(f"✓ Prediction complete: {result.get('status', 'unknown')}")
        
        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Error during prediction'
        }), 500

@app.route('/api/batch', methods=['POST'])
def batch_predict():
    """
    Batch prediction for multiple images
    
    Expected: JSON with list of base64 encoded images or file uploads
    """
    if predictor is None:
        return jsonify({
            'success': False,
            'error': 'Predictor not initialized'
        }), 503
    
    try:
        results = []
        
        if 'images' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No images provided'
            }), 400
        
        files = request.files.getlist('images')
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = get_unique_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Predict
                result = predictor.predict(filepath)
                result['image_filename'] = filename
                results.append(result)
        
        return jsonify({
            'success': True,
            'total_processed': len(results),
            'results': results,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Batch prediction error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history', methods=['GET'])
def history():
    """Get prediction history"""
    try:
        upload_dir = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_dir):
            return jsonify({
                'success': True,
                'total_uploads': 0,
                'files': []
            })
        
        files = os.listdir(upload_dir)
        files_info = []
        
        for filename in files:
            filepath = os.path.join(upload_dir, filename)
            if os.path.isfile(filepath):
                files_info.append({
                    'filename': filename,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                })
        
        return jsonify({
            'success': True,
            'total_uploads': len(files_info),
            'files': files_info
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Not Found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors"""
    return jsonify({
        'success': False,
        'error': 'Method Not Allowed',
        'message': 'The HTTP method is not allowed for this endpoint'
    }), 405

@app.errorhandler(413)
def payload_too_large(error):
    """Handle 413 errors"""
    return jsonify({
        'success': False,
        'error': 'Payload Too Large',
        'message': 'File size exceeds maximum allowed (50MB)'
    }), 413

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred'
    }), 500

# ============================================================================
# TESTING ENDPOINTS
# ============================================================================

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    if predictor is None:
        return jsonify({'status': 'error', 'message': 'Predictor not ready'}), 503
    
    return jsonify({
        'status': 'ok',
        'model_ready': True,
        'classes': len(predictor.class_names),
        'message': 'API is ready for predictions'
    })

# ============================================================================
# MAIN
# ============================================================================

def run_api(host='0.0.0.0', port=5000, debug=False):
    """Run Flask API"""
    logger.info("="*80)
    logger.info("Starting Crop Disease Prediction API")
    logger.info("="*80)
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Debug: {debug}")
    logger.info("="*80)
    
    app.run(host=host, port=port, debug=debug, threaded=True)

if __name__ == '__main__':
    import sys
    
    # Check arguments
    port = 5000
    debug = False
    
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    if len(sys.argv) > 2:
        debug = sys.argv[2].lower() == 'true'
    
    run_api(port=port, debug=debug)
