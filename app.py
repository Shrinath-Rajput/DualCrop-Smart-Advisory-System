"""
Flask Web Application - Crop Disease Prediction System
Complete production-ready web application with UI

Using the improved two-stage prediction system
"""

import os
import json
import logging
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from predict_improved import ImprovedCropDiseasePredictor
from datetime import datetime
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize predictor globally
try:
    predictor = ImprovedCropDiseasePredictor()
    PREDICTOR_READY = True
    logger.info("✓ Two-stage predictor initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize predictor: {e}")
    logger.error(f"Make sure to run train_improved.py first to generate models")
    PREDICTOR_READY = False

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html', model_ready=PREDICTOR_READY)


@app.route('/api/predict', methods=['POST'])
def predict():
    """API endpoint for disease prediction"""
    try:
        if not PREDICTOR_READY:
            return jsonify({
                'success': False,
                'error': 'Model not loaded. Please train the model first.'
            }), 503
        
        if 'image' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No image file provided'
            }), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, BMP'
            }), 400
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], timestamp + filename)
        file.save(filepath)
        
        logger.info(f"File saved: {filepath}")
        
        # Make prediction
        result = predictor.predict(filepath)
        
        # Add file path to result
        result['image_path'] = f'/uploads/{os.path.basename(filepath)}'
        result['timestamp'] = datetime.now().isoformat()
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Error during prediction: {str(e)}'
        }), 500


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/api/info')
def model_info():
    """Get model information"""
    if not PREDICTOR_READY:
        return jsonify({
            'ready': False,
            'error': 'Model not loaded'
        }), 503
    
    try:
        classes = predictor.classes
        return jsonify({
            'ready': True,
            'num_classes': len(classes),
            'classes': classes,
            'model_path': predictor.model_path
        }), 200
    except Exception as e:
        logger.error(f"Info error: {str(e)}")
        return jsonify({
            'ready': False,
            'error': str(e)
        }), 500


@app.route('/api/history')
def get_history():
    """Get training history"""
    try:
        if os.path.exists('training_history.json'):
            with open('training_history.json', 'r') as f:
                history = json.load(f)
            return jsonify(history), 200
        else:
            return jsonify({'error': 'Training history not found'}), 404
    except Exception as e:
        logger.error(f"History error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/disease-db')
def disease_database():
    """Get disease database"""
    try:
        if os.path.exists('disease_database.json'):
            with open('disease_database.json', 'r') as f:
                db = json.load(f)
            return jsonify(db), 200
        else:
            return jsonify({'error': 'Disease database not found'}), 404
    except Exception as e:
        logger.error(f"DB error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_ready': PREDICTOR_READY,
        'timestamp': datetime.now().isoformat()
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    os.makedirs('templates', exist_ok=True)
    
    logger.info("="*70)
    logger.info("CROP DISEASE PREDICTION SYSTEM - WEB APPLICATION")
    logger.info("="*70)
    logger.info(f"Model Status: {'✓ Ready' if PREDICTOR_READY else '✗ Not Ready'}")
    logger.info(f"Upload Folder: {app.config['UPLOAD_FOLDER']}")
    logger.info("Running on http://0.0.0.0:5000")
    logger.info("="*70)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
