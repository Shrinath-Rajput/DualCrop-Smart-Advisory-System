"""
IMPROVED PREDICTION MODULE
Crop Disease Prediction System (Grapes & Brinjal)

Two-Stage Prediction System:
1. Crop Detection (identify if Grapes or Brinjal)
2. Disease Detection (predict disease for that crop only)

Features:
- High confidence predictions (>70% threshold)
- Proper uncertainty handling
- Crop-specific disease prediction
- Comprehensive disease information
- Medicine recommendations
- Treatment plans
"""

import os
import json
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovedCropDiseasePredictor:
    """Professional Two-Stage Crop Disease Predictor"""
    
    # Confidence threshold
    CONFIDENCE_THRESHOLD = 0.70  # 70% minimum confidence
    
    # Model and class paths
    GRAPES_MODEL_PATH = "models/grapes_disease_model.h5"
    BRINJAL_MODEL_PATH = "models/brinjal_disease_model.h5"
    GRAPES_CLASSES_PATH = "models/grapes_classes.json"
    BRINJAL_CLASSES_PATH = "models/brinjal_classes.json"
    DISEASE_DB_PATH = "disease_database.json"
    
    def __init__(self):
        """Initialize predictor with crop-specific models"""
        self.grapes_model = None
        self.brinjal_model = None
        self.grapes_classes = []
        self.brinjal_classes = []
        self.disease_database = {}
        
        self._load_models()
        self._load_class_mappings()
        self._load_disease_database()
        
        logger.info("✓ Two-stage predictor initialized successfully")
    
    def _load_models(self):
        """Load both crop-specific models"""
        
        if not os.path.exists(self.GRAPES_MODEL_PATH):
            raise FileNotFoundError(f"Grapes model not found: {self.GRAPES_MODEL_PATH}")
        
        if not os.path.exists(self.BRINJAL_MODEL_PATH):
            raise FileNotFoundError(f"Brinjal model not found: {self.BRINJAL_MODEL_PATH}")
        
        self.grapes_model = keras.models.load_model(self.GRAPES_MODEL_PATH)
        logger.info(f"✓ Grapes model loaded: {self.GRAPES_MODEL_PATH}")
        
        self.brinjal_model = keras.models.load_model(self.BRINJAL_MODEL_PATH)
        logger.info(f"✓ Brinjal model loaded: {self.BRINJAL_MODEL_PATH}")
    
    def _load_class_mappings(self):
        """Load class mappings for both crops"""
        
        if not os.path.exists(self.GRAPES_CLASSES_PATH):
            raise FileNotFoundError(f"Grapes classes not found: {self.GRAPES_CLASSES_PATH}")
        
        if not os.path.exists(self.BRINJAL_CLASSES_PATH):
            raise FileNotFoundError(f"Brinjal classes not found: {self.BRINJAL_CLASSES_PATH}")
        
        with open(self.GRAPES_CLASSES_PATH, 'r') as f:
            grapes_data = json.load(f)
            self.grapes_classes = [grapes_data['classes'][str(i)] 
                                   for i in range(len(grapes_data['classes']))]
        
        with open(self.BRINJAL_CLASSES_PATH, 'r') as f:
            brinjal_data = json.load(f)
            self.brinjal_classes = [brinjal_data['classes'][str(i)] 
                                    for i in range(len(brinjal_data['classes']))]
        
        logger.info(f"✓ Grapes classes: {self.grapes_classes}")
        logger.info(f"✓ Brinjal classes: {self.brinjal_classes}")
    
    def _load_disease_database(self):
        """Load comprehensive disease information"""
        
        if not os.path.exists(self.DISEASE_DB_PATH):
            logger.warning(f"Disease database not found: {self.DISEASE_DB_PATH}")
            return
        
        with open(self.DISEASE_DB_PATH, 'r') as f:
            data = json.load(f)
        
        self.disease_database = data.get('diseases', {})
        logger.info(f"✓ Disease database loaded: {len(self.disease_database)} diseases")
    
    def _preprocess_image(self, image_path: str, image_size: int = 224) -> np.ndarray:
        """Preprocess image for prediction"""
        
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert BGR to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize
        image = cv2.resize(image, (image_size, image_size))
        
        # Normalize to [0, 1]
        image = image / 255.0
        
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        
        return image
    
    def _detect_crop_type(self, image_array: np.ndarray) -> Tuple[str, float]:
        """
        Detect crop type using color and texture analysis
        Falls back to prediction if unclear
        """
        
        # Extract image from batch
        img = image_array[0]
        
        # Convert to HSV for color analysis
        img_bgr = (img * 255).astype(np.uint8)
        img_bgr = cv2.cvtColor(img_bgr, cv2.COLOR_RGB2BGR)
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        
        # Analyze color distribution (simplified heuristic)
        # This is a basic heuristic; actual detection relies on model predictions
        
        return None, 0.0  # Return None to use model-based detection
    
    def predict(self, image_path: str) -> Dict:
        """
        Two-stage prediction:
        1. Predict with both models
        2. Use the model with higher confidence
        3. Determine if prediction is reliable
        """
        
        try:
            # Preprocess image
            image = self._preprocess_image(image_path)
            
            # Stage 1: Get predictions from both models
            grapes_predictions = self.grapes_model.predict(image, verbose=0)[0]
            brinjal_predictions = self.brinjal_model.predict(image, verbose=0)[0]
            
            # Get best predictions from each model
            grapes_idx = np.argmax(grapes_predictions)
            grapes_confidence = float(grapes_predictions[grapes_idx])
            grapes_class = self.grapes_classes[grapes_idx]
            
            brinjal_idx = np.argmax(brinjal_predictions)
            brinjal_confidence = float(brinjal_predictions[brinjal_idx])
            brinjal_class = self.brinjal_classes[brinjal_idx]
            
            logger.info(f"Grapes prediction: {grapes_class} ({grapes_confidence:.2%})")
            logger.info(f"Brinjal prediction: {brinjal_class} ({brinjal_confidence:.2%})")
            
            # Stage 2: Determine which prediction is more reliable
            if grapes_confidence >= brinjal_confidence:
                # Use Grapes model
                crop = "Grapes"
                predicted_class = grapes_class
                confidence = grapes_confidence
                all_predictions = self._format_predictions(grapes_predictions, self.grapes_classes)
            else:
                # Use Brinjal model
                crop = "Brinjal"
                predicted_class = brinjal_class
                confidence = brinjal_confidence
                all_predictions = self._format_predictions(brinjal_predictions, self.brinjal_classes)
            
            logger.info(f"Selected: {crop} - {predicted_class} ({confidence:.2%})")
            
            # Stage 3: Check confidence threshold
            if confidence < self.CONFIDENCE_THRESHOLD:
                return {
                    'success': True,
                    'crop': crop,
                    'status': 'Uncertain',
                    'disease': 'Unknown',
                    'confidence': f"{confidence * 100:.2f}%",
                    'confidence_score': float(confidence),
                    'message': 'Prediction uncertain. Please upload a clearer image.',
                    'all_predictions': all_predictions
                }
            
            # Stage 4: Determine healthy vs diseased status
            is_healthy = self._is_healthy_class(predicted_class)
            
            # Stage 5: Get disease information
            disease_info = self._get_disease_info(crop, predicted_class, is_healthy)
            
            # Build comprehensive result
            result = {
                'success': True,
                'crop': crop,
                'predicted_class': predicted_class,
                'status': 'Healthy' if is_healthy else 'Diseased',
                'disease': disease_info.get('disease_name', 'Unknown'),
                'confidence': f"{confidence * 100:.2f}%",
                'confidence_score': float(confidence),
                'severity': disease_info.get('severity', 'None'),
                'symptoms': disease_info.get('symptoms', []),
                'causes': disease_info.get('causes', []),
                'medicine': disease_info.get('medicine', 'N/A'),
                'treatment': disease_info.get('treatment', 'N/A'),
                'prevention': disease_info.get('prevention', 'N/A'),
                'message': disease_info.get('message', ''),
                'all_predictions': all_predictions
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Error during prediction: {str(e)}'
            }
    
    def _is_healthy_class(self, class_name: str) -> bool:
        """Check if class name indicates healthy plant"""
        healthy_keywords = ['healthy', 'normal', 'good']
        return any(keyword.lower() in class_name.lower() for keyword in healthy_keywords)
    
    def _get_disease_info(self, crop: str, class_name: str, is_healthy: bool) -> Dict:
        """Get disease information from database"""
        
        # Try exact match first
        db_key = f"{crop}_{class_name}"
        if db_key in self.disease_database:
            return self.disease_database[db_key]
        
        # Try with disease suffix
        db_key = f"{crop}_Diseases_{class_name}"
        if db_key in self.disease_database:
            return self.disease_database[db_key]
        
        # Try with just crop prefix
        db_key = f"{crop}_{class_name}"
        if db_key in self.disease_database:
            return self.disease_database[db_key]
        
        # Generate default info
        if is_healthy:
            return {
                'disease_name': 'Healthy',
                'crop': crop,
                'severity': 'None',
                'status': 'Healthy',
                'medicine': 'None',
                'treatment': 'None',
                'prevention': 'Continue regular monitoring and maintenance',
                'symptoms': ['Green vibrant leaves', 'No visible spots or discoloration', 'Normal growth'],
                'causes': ['Plant is healthy'],
                'message': f'No disease detected. Your {crop} plant is healthy.'
            }
        else:
            return {
                'disease_name': class_name,
                'crop': crop,
                'severity': 'Unknown',
                'status': 'Diseased',
                'medicine': 'Consult agricultural expert',
                'treatment': 'Consult agricultural expert',
                'prevention': 'Follow standard disease prevention practices',
                'symptoms': [f'{class_name} detected on {crop}'],
                'causes': ['Disease detected'],
                'message': f'{class_name} detected on {crop} plant. Consult agricultural expert.'
            }
    
    def _format_predictions(self, predictions: np.ndarray, classes: List[str], top_n: int = 5) -> List[Dict]:
        """Format top N predictions"""
        
        formatted = []
        for idx, score in enumerate(predictions):
            formatted.append({
                'class': classes[idx],
                'confidence': f"{float(score) * 100:.2f}%",
                'score': float(score)
            })
        
        formatted.sort(key=lambda x: x['score'], reverse=True)
        return formatted[:top_n]
    
    def predict_batch(self, image_paths: List[str]) -> List[Dict]:
        """Batch predict on multiple images"""
        
        results = []
        for image_path in image_paths:
            try:
                result = self.predict(image_path)
                results.append(result)
            except Exception as e:
                results.append({
                    'success': False,
                    'error': str(e),
                    'image': image_path
                })
        
        return results


def predict_image(image_path: str) -> Dict:
    """Utility function for single prediction"""
    predictor = ImprovedCropDiseasePredictor()
    return predictor.predict(image_path)


def print_result(result: Dict) -> None:
    """Pretty print prediction result"""
    
    if not result.get('success', False):
        print(f"\n❌ Error: {result.get('message', 'Unknown error')}\n")
        return
    
    crop = result.get('crop', 'Unknown')
    status = result.get('status', 'Unknown')
    disease = result.get('disease', 'Unknown')
    confidence = result.get('confidence', 'Unknown')
    message = result.get('message', '')
    
    print("\n" + "="*70)
    print("🌾 CROP DISEASE PREDICTION REPORT")
    print("="*70)
    print(f"Crop:           {crop}")
    print(f"Status:         {status}")
    print(f"Disease:        {disease}")
    print(f"Confidence:     {confidence}")
    print("-"*70)
    
    if status == 'Healthy':
        print(f"\n✓ {message}\n")
    elif status == 'Uncertain':
        print(f"\n⚠️  {message}\n")
    else:
        print(f"\n📋 {message}")
        
        severity = result.get('severity', 'Unknown')
        if severity and severity != 'Unknown':
            print(f"Severity:       {severity}")
        
        symptoms = result.get('symptoms', [])
        if symptoms:
            print(f"\n🔍 SYMPTOMS:")
            for symptom in symptoms:
                print(f"   • {symptom}")
        
        medicine = result.get('medicine', 'N/A')
        if medicine and medicine != 'N/A':
            print(f"\n💊 MEDICINE:")
            print(f"   {medicine}")
        
        treatment = result.get('treatment', 'N/A')
        if treatment and treatment != 'N/A':
            print(f"\n🛠️  TREATMENT:")
            print(f"   {treatment}")
        
        prevention = result.get('prevention', 'N/A')
        if prevention and prevention != 'N/A':
            print(f"\n🛡️  PREVENTION:")
            print(f"   {prevention}")
    
    # Show all predictions
    all_predictions = result.get('all_predictions', [])
    if all_predictions:
        print("\n📊 ALL PREDICTIONS:")
        for pred in all_predictions:
            print(f"   {pred['class']:40s} → {pred['confidence']:>7s}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python predict_improved.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        result = predict_image(image_path)
        print_result(result)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        sys.exit(1)
