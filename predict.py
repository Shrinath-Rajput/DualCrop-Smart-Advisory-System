"""
CROP DISEASE PREDICTION MODULE
Professional disease prediction using trained TensorFlow model

Features:
- Real model predictions (not fallback)
- Proper image preprocessing
- Actual softmax confidence scores
- Healthy detection only when model predicts healthy
- 70% confidence threshold for uncertainty
"""

import os
import json
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CropDiseasePredictor:
    """Professional Crop Disease Prediction System"""
    
    # Paths to model and resources
    MODEL_PATH = "artifacts/crop_disease_model.h5"
    CLASSES_PATH = "artifacts/class_names.json"
    DISEASE_DB_PATH = "disease_database.json"
    
    # Confidence threshold - if below this, ask for clearer image
    CONFIDENCE_THRESHOLD = 0.70
    
    def __init__(self):
        """Initialize predictor with trained model"""
        self.model = None
        self.class_names = []
        self.disease_database = {}
        self.healthy_keywords = ['healthy', 'normal', 'good']
        
        logger.info("Initializing predictor...")
        self._load_model()
        self._load_classes()
        self._load_disease_database()
        logger.info("✓ Predictor ready")
    
    def _load_model(self):
        """Load trained TensorFlow model"""
        if not os.path.exists(self.MODEL_PATH):
            raise FileNotFoundError(
                f"Model not found at {self.MODEL_PATH}\n"
                f"Please train the model first using: python train_improved.py"
            )
        
        try:
            self.model = keras.models.load_model(self.MODEL_PATH)
            logger.info(f"✓ Model loaded: {self.MODEL_PATH}")
        except Exception as e:
            raise Exception(f"Failed to load model: {str(e)}")
    
    def _load_classes(self):
        """Load class names from JSON"""
        if not os.path.exists(self.CLASSES_PATH):
            raise FileNotFoundError(
                f"Class names not found at {self.CLASSES_PATH}\n"
                f"Please ensure class_names.json exists in artifacts/"
            )
        
        try:
            with open(self.CLASSES_PATH, 'r') as f:
                data = json.load(f)
            
            # Handle both format: {"0": "class", "1": "class"} and {"classes": {"0": "class"}}
            if 'classes' in data:
                classes_dict = data['classes']
            else:
                classes_dict = data
            
            # Sort by index and extract class names
            self.class_names = [classes_dict[str(i)] for i in range(len(classes_dict))]
            logger.info(f"✓ Classes loaded: {self.class_names}")
        except Exception as e:
            raise Exception(f"Failed to load classes: {str(e)}")
    
    def _load_disease_database(self):
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
    
    def _preprocess_image(self, image_path: str, target_size: int = 224) -> np.ndarray:
        """
        Preprocess image for model prediction
        
        Steps:
        1. Read image using OpenCV
        2. Convert BGR to RGB
        3. Resize to model input size (224x224)
        4. Normalize to [0, 1] range
        5. Add batch dimension
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert BGR to RGB (OpenCV uses BGR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize to model input size
        image = cv2.resize(image, (target_size, target_size))
        
        # Normalize to [0, 1]
        image = image.astype(np.float32) / 255.0
        
        # Add batch dimension [H,W,C] -> [1,H,W,C]
        image = np.expand_dims(image, axis=0)
        
        return image
    
    def _extract_crop_and_disease(self, class_name: str) -> tuple:
        """
        Extract crop type and disease from class name
        
        Examples:
        - "Grapes_Diseases_Black Rot" -> ("Grapes", "Black Rot")
        - "Brinjal_Diseases_brinjal_little_leaf" -> ("Brinjal", "brinjal_little_leaf")
        - "Grapes_Diseases_Healthy" -> ("Grapes", "Healthy")
        """
        parts = class_name.split('_')
        
        if len(parts) < 2:
            return "Unknown", class_name
        
        crop = parts[0]  # First part is crop type
        
        # Everything after "Diseases_" is the disease name
        if "Diseases" in class_name:
            disease = class_name.split("Diseases_", 1)[1]
        else:
            disease = "_".join(parts[1:])
        
        return crop, disease
    
    def _is_healthy(self, class_name: str) -> bool:
        """
        Check if predicted class indicates healthy plant
        
        Returns True ONLY if the model predicts a healthy class
        """
        class_lower = class_name.lower()
        return any(keyword in class_lower for keyword in self.healthy_keywords)
    
    def _get_disease_info(self, class_name: str, crop: str, is_healthy: bool) -> Dict:
        """Get disease information from database"""
        
        # Try different key formats
        possible_keys = [
            f"{crop}_{class_name}",
            f"{crop}_Diseases_{class_name}",
            class_name
        ]
        
        for key in possible_keys:
            if key in self.disease_database:
                return self.disease_database[key]
        
        # Generate default response if not in database
        if is_healthy:
            return {
                'disease_name': 'Healthy',
                'crop': crop,
                'status': 'Healthy',
                'severity': 'None',
                'medicine': 'None',
                'treatment': 'Continue regular care',
                'prevention': 'Monitor plant regularly',
                'symptoms': ['No disease signs', 'Plant appears healthy'],
                'causes': ['Plant is healthy'],
                'message': f'Your {crop} plant appears to be healthy.'
            }
        else:
            return {
                'disease_name': class_name,
                'crop': crop,
                'status': 'Diseased',
                'severity': 'Unknown',
                'medicine': 'Consult agricultural expert',
                'treatment': 'Seek expert advice',
                'prevention': 'Follow disease control practices',
                'symptoms': [f'Possible {class_name}'],
                'causes': ['Disease detected by model'],
                'message': f'{class_name} detected. Consult agricultural expert for treatment.'
            }
    
    def predict(self, image_path: str) -> Dict:
        """
        Predict disease from image
        
        Returns:
        - Dictionary with crop, disease, status, confidence, and treatment info
        """
        try:
            # Preprocess image
            image_array = self._preprocess_image(image_path)
            
            # Get model prediction (softmax probabilities)
            predictions = self.model.predict(image_array, verbose=0)[0]
            
            # Get predicted class index
            predicted_idx = np.argmax(predictions)
            predicted_class = self.class_names[predicted_idx]
            
            # Get confidence score (softmax probability)
            confidence = float(predictions[predicted_idx])
            confidence_percent = confidence * 100
            
            # Extract crop and disease from class name
            crop, disease = self._extract_crop_and_disease(predicted_class)
            
            # Determine if prediction is healthy
            is_healthy = self._is_healthy(predicted_class)
            
            logger.info(f"Prediction: {predicted_class} ({confidence_percent:.2f}%)")
            
            # Check confidence threshold
            if confidence < self.CONFIDENCE_THRESHOLD:
                return {
                    'success': True,
                    'crop': crop,
                    'disease': 'Uncertain',
                    'status': 'Uncertain',
                    'confidence': f"{confidence_percent:.2f}%",
                    'confidence_score': confidence,
                    'message': 'Prediction uncertain. Please upload a clearer image with better lighting.',
                    'predicted_class': predicted_class
                }
            
            # Get disease information from database
            disease_info = self._get_disease_info(predicted_class, crop, is_healthy)
            
            # Build comprehensive result
            result = {
                'success': True,
                'crop': crop,
                'disease': disease,
                'status': 'Healthy' if is_healthy else 'Diseased',
                'confidence': f"{confidence_percent:.2f}%",
                'confidence_score': confidence,
                'predicted_class': predicted_class,
                'message': disease_info.get('message', ''),
                'severity': disease_info.get('severity', 'Unknown'),
                'symptoms': disease_info.get('symptoms', []),
                'causes': disease_info.get('causes', []),
                'medicine': disease_info.get('medicine', 'N/A'),
                'treatment': disease_info.get('treatment', 'N/A'),
                'prevention': disease_info.get('prevention', 'N/A')
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Error during prediction: {str(e)}'
            }
    
def predict_image(image_path: str) -> Dict:
    """Quick function to predict single image"""
    predictor = CropDiseasePredictor()
    return predictor.predict(image_path)


def print_prediction(result: Dict) -> None:
    """Print prediction result in readable format"""
    print("\n" + "="*70)
    print("🌾 CROP DISEASE PREDICTION")
    print("="*70)
    
    if not result.get('success', False):
        print(f"❌ Error: {result.get('message', 'Unknown error')}")
        print("="*70 + "\n")
        return
    
    print(f"Crop:           {result.get('crop', 'Unknown')}")
    print(f"Status:         {result.get('status', 'Unknown')}")
    print(f"Disease:        {result.get('disease', 'Unknown')}")
    print(f"Confidence:     {result.get('confidence', 'Unknown')}")
    print(f"Severity:       {result.get('severity', 'Unknown')}")
    print(f"\nMessage:        {result.get('message', '')}")
    
    if result.get('symptoms'):
        print(f"\nSymptoms:")
        for symptom in result['symptoms']:
            print(f"  • {symptom}")
    
    if result.get('treatment') and result['treatment'] != 'None':
        print(f"\nTreatment:      {result['treatment']}")
    
    if result.get('prevention') and result['prevention'] != 'None':
        print(f"Prevention:     {result['prevention']}")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    predictor = CropDiseasePredictor()
    result = predictor.predict(image_path)
    print_prediction(result)
