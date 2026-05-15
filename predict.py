"""
CROP DISEASE PREDICTION MODULE - PRODUCTION READY
Real disease prediction using trained TensorFlow/Keras model

Features:
- Actual model predictions (no fallbacks, no random predictions)
- Proper image preprocessing (224x224, normalized with /255.0)
- Real softmax confidence scores from model
- Healthy/Diseased classification based on model output
- Intelligent crop type detection
- Comprehensive disease information from database
- Production-ready error handling
"""

import os
import json
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
import logging
from typing import Dict, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CropDiseasePredictor:
    """Production-Ready Crop Disease Prediction System"""
    
    # Paths to model and resources
    MODEL_PATH = "artifacts/crop_disease_model.h5"
    CLASSES_PATH = "artifacts/class_names.json"
    DISEASE_DB_PATH = "disease_database.json"
    
    # Image preprocessing settings
    TARGET_SIZE = 224
    NORMALIZATION_FACTOR = 255.0
    
    def __init__(self):
        """Initialize predictor with trained model and resources"""
        self.model = None
        self.class_names = []
        self.disease_database = {}
        
        logger.info("Initializing CropDiseasePredictor...")
        self._load_model()
        self._load_classes()
        self._load_disease_database()
        logger.info("✓ Predictor initialized successfully")
    
    def _load_model(self) -> None:
        """Load trained TensorFlow/Keras model from artifacts"""
        if not os.path.exists(self.MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {self.MODEL_PATH}\n"
                f"Please train the model first using: python train_improved.py"
            )
        
        try:
            self.model = keras.models.load_model(self.MODEL_PATH)
            logger.info(f"✓ Model loaded: {self.MODEL_PATH}")
            logger.info(f"  Model input shape: {self.model.input_shape}")
            logger.info(f"  Model output shape: {self.model.output_shape}")
        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")
    
    def _load_classes(self) -> None:
        """Load class names from JSON file"""
        if not os.path.exists(self.CLASSES_PATH):
            raise FileNotFoundError(
                f"Class names not found at {self.CLASSES_PATH}\n"
                f"Please ensure class_names.json exists in artifacts/"
            )
        
        try:
            with open(self.CLASSES_PATH, 'r') as f:
                data = json.load(f)
            
            # Handle both formats:
            # Format 1: {"0": "class", "1": "class", ...}
            # Format 2: {"classes": {"0": "class", "1": "class", ...}}
            if 'classes' in data:
                classes_dict = data['classes']
            else:
                classes_dict = data
            
            # Extract class names in order
            num_classes = len(classes_dict)
            self.class_names = [classes_dict[str(i)] for i in range(num_classes)]
            
            logger.info(f"✓ Classes loaded: {num_classes} classes")
            for idx, name in enumerate(self.class_names):
                logger.info(f"  [{idx}] {name}")
        except Exception as e:
            raise Exception(f"Failed to load classes: {str(e)}")
    
    def _load_disease_database(self) -> None:
        """Load disease information database"""
        if not os.path.exists(self.DISEASE_DB_PATH):
            logger.warning(f"Disease database not found: {self.DISEASE_DB_PATH}")
            return
        
        try:
            with open(self.DISEASE_DB_PATH, 'r') as f:
                data = json.load(f)
            self.disease_database = data.get('diseases', {})
            logger.info(f"✓ Disease database loaded: {len(self.disease_database)} entries")
        except Exception as e:
            logger.warning(f"Failed to load disease database: {str(e)}")
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for model prediction
        
        Steps:
        1. Read image using OpenCV
        2. Convert BGR to RGB
        3. Resize to 224x224
        4. Normalize with /255.0
        5. Add batch dimension
        
        Args:
            image_path: Path to image file
            
        Returns:
            Preprocessed image array with shape (1, 224, 224, 3)
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert BGR to RGB (OpenCV reads in BGR format)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize to model input size (224x224)
        image = cv2.resize(image, (self.TARGET_SIZE, self.TARGET_SIZE))
        
        # Normalize to [0, 1] range with /255.0
        image = image.astype(np.float32) / self.NORMALIZATION_FACTOR
        
        # Add batch dimension: (H, W, C) -> (1, H, W, C)
        image = np.expand_dims(image, axis=0)
        
        return image
    
    def _extract_crop_and_disease(self, class_name: str) -> Tuple[str, str]:
        """
        Extract crop type and disease name from class label
        
        Examples:
        - "Grapes_Diseases_Black Rot" -> ("Grapes", "Black Rot")
        - "Binjal_Diseases_brinjal_little_leaf" -> ("Binjal", "brinjal_little_leaf")
        - "Grapes_Diseases_Healthy" -> ("Grapes", "Healthy")
        
        Args:
            class_name: Full class name from model
            
        Returns:
            Tuple of (crop_type, disease_name)
        """
        parts = class_name.split('_')
        
        if len(parts) < 2:
            return "Unknown", class_name
        
        crop = parts[0]  # First part is crop type
        
        # Extract disease name after "Diseases_"
        if "Diseases" in class_name:
            disease = class_name.split("Diseases_", 1)[1]
        else:
            disease = "_".join(parts[1:])
        
        return crop, disease
    
    def _is_healthy(self, class_name: str) -> bool:
        """
        Determine if predicted class indicates healthy plant
        
        Returns True ONLY if model predicts a healthy class
        
        Args:
            class_name: Predicted class name
            
        Returns:
            True if healthy, False if diseased
        """
        return 'healthy' in class_name.lower()
    
    def _get_disease_info(self, predicted_class: str, crop: str, is_healthy: bool) -> Dict:
        """
        Get detailed disease information from database
        
        Args:
            predicted_class: Full predicted class name
            crop: Extracted crop type
            is_healthy: Whether prediction is healthy
            
        Returns:
            Dictionary with disease information
        """
        # Try different key formats in database
        possible_keys = [
            predicted_class,
            f"{crop}_Diseases_{predicted_class.split('Diseases_')[-1]}",
            f"{crop}_{'Healthy' if is_healthy else predicted_class.split('_')[-1]}"
        ]
        
        for key in possible_keys:
            if key in self.disease_database:
                return self.disease_database[key]
        
        # If not found, return safe defaults based on health status
        if is_healthy:
            return {
                'disease_name': 'Healthy',
                'status': 'Healthy',
                'severity': 'None',
                'medicine': 'None',
                'treatment': 'Continue regular maintenance and monitoring',
                'prevention': 'Monitor plant health regularly, maintain good growing conditions',
                'symptoms': ['No visible disease signs', 'Plant appears healthy'],
                'causes': ['Plant is healthy'],
                'message': f'Your {crop} plant is healthy. No disease detected.'
            }
        else:
            disease_name = predicted_class.split('Diseases_')[-1] if 'Diseases_' in predicted_class else predicted_class
            return {
                'disease_name': disease_name,
                'status': 'Diseased',
                'severity': 'Medium',
                'medicine': 'Consult agricultural expert for specific treatment',
                'treatment': 'Seek professional agricultural assistance',
                'prevention': 'Follow disease control and prevention practices',
                'symptoms': [f'Symptoms of {disease_name}'],
                'causes': ['Disease condition detected'],
                'message': f'{disease_name} detected. Consult with an agricultural expert for treatment options.'
            }
    
    def predict(self, image_path: str) -> Dict:
        """
        Predict crop disease from image using trained model
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary containing:
            - success: True/False
            - crop: Crop type (Grapes, Binjal, etc.)
            - disease: Disease name
            - status: "Healthy" or "Diseased"
            - confidence: Confidence percentage (0-100)
            - recommendation: Treatment recommendations
            - treatment: Treatment details
            - prevention: Prevention strategies
            - (additional fields from database)
        """
        try:
            # Preprocess image
            image_array = self._preprocess_image(image_path)
            logger.info(f"Image preprocessed: shape={image_array.shape}")
            
            # Get model prediction (raw softmax probabilities)
            predictions = self.model.predict(image_array, verbose=0)
            prediction_probs = predictions[0]
            
            # Get predicted class index using argmax
            predicted_idx = np.argmax(prediction_probs)
            predicted_class = self.class_names[predicted_idx]
            
            # Get real confidence score from model
            confidence = float(prediction_probs[predicted_idx])
            confidence_percent = confidence * 100
            
            logger.info(f"✓ Prediction: {predicted_class}")
            logger.info(f"  Confidence: {confidence_percent:.2f}%")
            logger.info(f"  All predictions: {[(self.class_names[i], p*100) for i, p in enumerate(prediction_probs)]}")
            
            # Extract crop type and disease name
            crop, disease = self._extract_crop_and_disease(predicted_class)
            
            # Determine health status
            is_healthy = self._is_healthy(predicted_class)
            status = "Healthy" if is_healthy else "Diseased"
            
            # Get detailed disease information
            disease_info = self._get_disease_info(predicted_class, crop, is_healthy)
            
            # Build comprehensive response
            response = {
                'success': True,
                'crop': crop,
                'disease': disease,
                'status': status,
                'confidence': round(confidence_percent, 2),
                'recommendation': disease_info.get('treatment', 'Consult agricultural expert'),
                'treatment': disease_info.get('treatment', 'N/A'),
                'prevention': disease_info.get('prevention', 'N/A'),
                'symptoms': disease_info.get('symptoms', []),
                'medicine': disease_info.get('medicine', 'N/A'),
                'severity': disease_info.get('severity', 'Unknown'),
                'message': disease_info.get('message', '')
            }
            
            logger.info(f"✓ Response prepared: {response['crop']} - {response['disease']} ({response['status']})")
            return response
        
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'message': f'Error during prediction: {str(e)}'
            }


def predict_image(image_path: str) -> Dict:
    """
    Quick function to predict disease from single image
    
    Args:
        image_path: Path to image file
        
    Returns:
        Prediction result dictionary
    """
    predictor = CropDiseasePredictor()
    return predictor.predict(image_path)


def print_prediction(result: Dict) -> None:
    """
    Print prediction result in readable format
    
    Args:
        result: Prediction result dictionary
    """
    print("\n" + "="*80)
    print(" " * 20 + "CROP DISEASE PREDICTION - RESULTS")
    print("="*80)
    
    if not result.get('success', False):
        print(f"\n❌ ERROR: {result.get('message', 'Unknown error')}")
        if result.get('error'):
            print(f"Details: {result.get('error')}")
        print("="*80 + "\n")
        return
    
    print(f"\nCrop:               {result.get('crop', 'Unknown')}")
    print(f"Status:             {result.get('status', 'Unknown')}")
    print(f"Disease:            {result.get('disease', 'Unknown')}")
    print(f"Confidence:         {result.get('confidence', 'N/A')}%")
    print(f"Severity:           {result.get('severity', 'Unknown')}")
    
    if result.get('message'):
        print(f"\nMessage:            {result.get('message', '')}")
    
    if result.get('symptoms') and len(result['symptoms']) > 0:
        print(f"\nSymptoms:")
        for symptom in result['symptoms']:
            print(f"  • {symptom}")
    
    if result.get('medicine') and result['medicine'] != 'None':
        print(f"\nMedicine:           {result['medicine']}")
    
    if result.get('treatment') and result['treatment'] != 'None':
        print(f"\nTreatment:          {result['treatment']}")
    
    if result.get('prevention') and result['prevention'] != 'None':
        print(f"\nPrevention:         {result['prevention']}")
    
    print("="*80 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path>")
        print("\nExample:")
        print("  python predict.py images/grape_disease.jpg")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    try:
        predictor = CropDiseasePredictor()
        result = predictor.predict(image_path)
        print_prediction(result)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
