"""
Production-Ready Prediction Module
Crop Disease Prediction System (Grapes & Brinjal)

Features:
- Automatic crop detection
- Disease identification  
- Dynamic confidence scores
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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CropDiseasePredictorPro:
    """Professional Crop Disease Predictor with comprehensive information"""
    
    def __init__(self, model_path="crop_disease_model.h5", 
                 class_names_path="class_names.json",
                 disease_db_path="disease_database.json"):
        """
        Initialize predictor
        
        Args:
            model_path: Path to trained model
            class_names_path: Path to class names JSON
            disease_db_path: Path to disease database
        """
        self.model_path = model_path
        self.class_names_path = class_names_path
        self.disease_db_path = disease_db_path
        
        self.model = None
        self.classes = []
        self.class_indices = {}
        self.disease_database = {}
        
        self._load_model()
        self._load_class_names()
        self._load_disease_database()
        
        logger.info("✓ Predictor initialized successfully")
    
    def _load_model(self):
        """Load trained model"""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        self.model = keras.models.load_model(self.model_path)
        logger.info(f"✓ Model loaded: {self.model_path}")
    
    def _load_class_names(self):
        """Load class names and mapping"""
        if not os.path.exists(self.class_names_path):
            raise FileNotFoundError(f"Class names not found: {self.class_names_path}")
        
        with open(self.class_names_path, 'r') as f:
            data = json.load(f)
        
        # Extract classes  
        if 'classes' in data:
            self.classes = [data['classes'][str(i)] 
                           for i in range(len(data['classes']))]
        
        self.class_indices = {cls: i for i, cls in enumerate(self.classes)}
        
        logger.info(f"✓ Classes loaded: {len(self.classes)} classes")
    
    def _load_disease_database(self):
        """Load disease information database"""
        if not os.path.exists(self.disease_db_path):
            logger.warning(f"Disease database not found: {self.disease_db_path}")
            self.disease_database = {}
            return
        
        with open(self.disease_db_path, 'r') as f:
            data = json.load(f)
        
        self.disease_database = data.get('diseases', {})
        logger.info(f"✓ Disease database loaded: {len(self.disease_database)} diseases")
    
    def _preprocess_image(self, image_path, image_size=224):
        """Preprocess image for model"""
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize
        image = cv2.resize(image, (image_size, image_size))
        
        # Normalize
        image = image / 255.0
        
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        
        return image
    
    def predict(self, image_path):
        """
        Make prediction on image with comprehensive information
        
        Args:
            image_path: Path to image
        
        Returns:
            Comprehensive prediction result
        """
        # Preprocess image
        image = self._preprocess_image(image_path)
        
        # Make prediction
        predictions = self.model.predict(image, verbose=0)
        
        # Get top prediction
        predicted_idx = np.argmax(predictions[0])
        predicted_class = self.classes[predicted_idx]
        confidence_score = float(predictions[0][predicted_idx])
        
        # Get disease info
        disease_info = self.disease_database.get(predicted_class, {})
        
        # Build result
        result = {
            'success': True,
            'crop': disease_info.get('crop', 'Unknown'),
            'predicted_class': predicted_class,
            'status': disease_info.get('status', 'Unknown'),
            'disease': disease_info.get('disease_name', predicted_class),
            'confidence': f"{confidence_score * 100:.2f}%",
            'confidence_score': confidence_score,
            'severity': disease_info.get('severity', 'Unknown'),
            'symptoms': disease_info.get('symptoms', []),
            'causes': disease_info.get('causes', []),
            'recommended_medicines': disease_info.get('recommended_medicines', []),
            'organic_solutions': disease_info.get('organic_solutions', []),
            'prevention_tips': disease_info.get('prevention_tips', []),
            'farmer_advice': disease_info.get('farmer_advice', ''),
            'message': disease_info.get('message', ''),
            'all_predictions': self._format_top_predictions(predictions[0])
        }
        
        return result
    
    def _format_top_predictions(self, predictions, top_n=5):
        """Format top N predictions"""
        formatted = []
        for idx, score in enumerate(predictions):
            formatted.append({
                'class': self.classes[idx],
                'confidence': f"{float(score) * 100:.2f}%",
                'score': float(score)
            })
        
        formatted.sort(key=lambda x: x['score'], reverse=True)
        return formatted[:top_n]
    
    def predict_batch(self, image_paths):
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


def predict_image(image_path):
    """Utility function for single prediction"""
    predictor = CropDiseasePredictorPro()
    return predictor.predict(image_path)


def print_result(result):
    """Pretty print prediction result"""
    if not result.get('success', False):
        print(f"\n❌ Error: {result.get('error', 'Unknown error')}\n")
        return
    
    print("\n" + "="*70)
    print("CROP DISEASE ANALYSIS REPORT")
    print("="*70)
    print(f"Crop Type:      {result['crop']}")
    print(f"Status:         {result['status']}")
    print(f"Disease:        {result['disease']}")
    print(f"Severity:       {result['severity']}")
    print(f"Confidence:     {result['confidence']}")
    print("-"*70)
    
    if result['status'] == 'Healthy':
        print(f"\n✓ {result['message']}\n")
    else:
        print(f"\n📋 SYMPTOMS:")
        for symptom in result['symptoms']:
            print(f"   • {symptom}")
        
        print(f"\n🔍 CAUSES:")
        for cause in result['causes']:
            print(f"   • {cause}")
        
        if result['recommended_medicines']:
            print(f"\n💊 RECOMMENDED MEDICINES:")
            for med in result['recommended_medicines']:
                print(f"   • {med['name']}")
                print(f"     Quantity: {med.get('quantity', 'N/A')}")
                print(f"     Usage: {med.get('usage', 'N/A')}")
        
        if result['organic_solutions']:
            print(f"\n🌿 ORGANIC SOLUTIONS:")
            for solution in result['organic_solutions']:
                print(f"   • {solution}")
        
        print(f"\n🛡️  PREVENTION TIPS:")
        for tip in result['prevention_tips']:
            print(f"   • {tip}")
        
        print(f"\n👨‍🌾 FARMER ADVICE:")
        print(f"   {result['farmer_advice']}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python predict.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    try:
        result = predict_image(image_path)
        print_result(result)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        sys.exit(1)
