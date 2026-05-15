"""
COMPLETE PRODUCTION-READY CROP DISEASE PREDICTION SYSTEM
=========================================================

✓ REAL MODEL INFERENCE ONLY
✓ NO FALLBACK PREDICTIONS
✓ NO FAKE CONFIDENCE SCORES  
✓ SOFTMAX CONFIDENCE FROM MODEL
✓ PROPER IMAGE PREPROCESSING (224x224, normalized /255.0)
✓ CLASS DETECTION VIA ARGMAX
✓ CROP-SPECIFIC RECOMMENDATIONS
✓ COMPREHENSIVE DISEASE INFORMATION
✓ PRODUCTION ERROR HANDLING

SUPPORTED CROPS & DISEASES:
- Brinjal: Healthy, Little Leaf, Leaf Spot, Blight
- Grapes: Healthy, Black Measles, Black Rot, Isariopsis Leaf Spot

OUTPUT FORMAT (JSON):
{
    "success": true,
    "crop": "Brinjal",
    "disease": "Little Leaf",
    "status": "Diseased",
    "confidence": 98.45,
    "severity": "High",
    "symptoms": [...],
    "medicine": "...",
    "treatment": "...",
    "organic_treatment": "...",
    "prevention": "...",
    "recommendation": "..."
}
"""

import os
import json
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
import logging
from typing import Dict, Tuple, Optional

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# PRODUCTION PREDICTION ENGINE
# ============================================================================

class CropDiseasePredictor:
    """Production-Ready Crop Disease Prediction Engine"""
    
    # ========================================================================
    # CONFIGURATION
    # ========================================================================
    
    # Model paths (try .keras first, fall back to .h5)
    MODEL_PATHS = [
        "artifacts/crop_disease_model.keras",
        "artifacts/crop_disease_model.h5",
        "artifacts/crop_disease_model_best.h5"
    ]
    
    CLASSES_PATH = "artifacts/class_names.json"
    DISEASE_DB_PATH = "disease_database.json"
    
    # Image preprocessing
    IMAGE_SIZE = 224
    NORMALIZE_FACTOR = 255.0
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 85.0
    LOW_CONFIDENCE = 70.0
    
    # ========================================================================
    # INITIALIZATION
    # ========================================================================
    
    def __init__(self):
        """Initialize prediction engine"""
        logger.info("="*90)
        logger.info("Initializing Production Crop Disease Predictor")
        logger.info("="*90)
        
        self.model = None
        self.class_names = []
        self.disease_database = {}
        
        self._load_model()
        self._load_classes()
        self._load_disease_database()
        
        logger.info("✓ Predictor ready for inference")
        logger.info("="*90)
    
    def _load_model(self) -> None:
        """Load trained TensorFlow model"""
        model_path = None
        
        # Try each model path
        for path in self.MODEL_PATHS:
            if os.path.exists(path):
                model_path = path
                break
        
        if model_path is None:
            raise FileNotFoundError(
                f"No model found. Checked:\n" + 
                "\n".join(f"  - {p}" for p in self.MODEL_PATHS) +
                f"\n\nPlease train the model: python train_complete.py"
            )
        
        try:
            self.model = keras.models.load_model(model_path)
            logger.info(f"✓ Model loaded: {model_path}")
            logger.info(f"  Input shape:  {self.model.input_shape}")
            logger.info(f"  Output shape: {self.model.output_shape}")
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")
    
    def _load_classes(self) -> None:
        """Load class names from JSON"""
        if not os.path.exists(self.CLASSES_PATH):
            raise FileNotFoundError(
                f"Class names not found: {self.CLASSES_PATH}\n"
                f"Generate via: python train_complete.py"
            )
        
        try:
            with open(self.CLASSES_PATH, 'r') as f:
                data = json.load(f)
            
            # Support multiple JSON formats
            if isinstance(data, dict) and 'classes' in data:
                classes_dict = data['classes']
            else:
                classes_dict = data
            
            # Extract classes in order
            num_classes = len(classes_dict)
            self.class_names = []
            
            for i in range(num_classes):
                if str(i) not in classes_dict:
                    raise ValueError(f"Missing class index {i}")
                self.class_names.append(classes_dict[str(i)])
            
            logger.info(f"✓ Classes loaded: {num_classes}")
            for idx, name in enumerate(self.class_names):
                logger.info(f"    [{idx}] {name}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to load classes: {str(e)}")
    
    def _load_disease_database(self) -> None:
        """Load disease information database"""
        if not os.path.exists(self.DISEASE_DB_PATH):
            logger.warning(f"⚠ Disease database not found: {self.DISEASE_DB_PATH}")
            return
        
        try:
            with open(self.DISEASE_DB_PATH, 'r') as f:
                data = json.load(f)
            self.disease_database = data.get('diseases', {})
            logger.info(f"✓ Disease database loaded: {len(self.disease_database)} entries")
        except Exception as e:
            logger.warning(f"Failed to load disease database: {str(e)}")
    
    # ========================================================================
    # IMAGE PREPROCESSING
    # ========================================================================
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for model prediction
        
        Strict requirements:
        - Read with OpenCV (BGR)
        - Convert to RGB
        - Resize to 224x224
        - Normalize with /255.0
        - Add batch dimension
        """
        # Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot read image: {image_path}")
        
        logger.debug(f"Original shape: {image.shape}")
        
        # Convert BGR → RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Resize to 224x224
        image = cv2.resize(image, (self.IMAGE_SIZE, self.IMAGE_SIZE))
        
        # Normalize [0, 1]
        image = image.astype(np.float32) / self.NORMALIZE_FACTOR
        
        # Validate normalization
        if not (np.min(image) >= 0.0 and np.max(image) <= 1.0):
            raise ValueError(f"Normalization failed: range [{np.min(image)}, {np.max(image)}]")
        
        # Add batch dimension
        image = np.expand_dims(image, axis=0)
        
        logger.debug(f"Preprocessed shape: {image.shape}, range: [{np.min(image):.2f}, {np.max(image):.2f}]")
        
        return image
    
    # ========================================================================
    # CLASS PARSING
    # ========================================================================
    
    def _extract_crop_and_disease(self, class_name: str) -> Tuple[str, str]:
        """
        Extract crop type and disease from class name
        
        Examples:
        - "Brinjal_Healthy" → ("Brinjal", "Healthy")
        - "Brinjal_Little_Leaf" → ("Brinjal", "Little Leaf")
        - "Grapes_Black_Measles" → ("Grapes", "Black Measles")
        - "Grapes_Isariopsis_Leaf_Spot" → ("Grapes", "Isariopsis Leaf Spot")
        """
        # Handle various formats
        if "_Diseases_" in class_name:
            # Old format: "Brinjal_Diseases_brinjal_little_leaf"
            parts = class_name.split("_Diseases_")
            crop = "Brinjal" if parts[0] == "Binjal" else parts[0]
            disease_raw = parts[1]
            
            # Convert underscores to proper case
            if disease_raw == "brinjal_little_leaf":
                disease = "Little Leaf"
            else:
                disease = disease_raw.replace("_", " ")
        else:
            # New format: "Brinjal_Healthy", "Grapes_Black_Rot"
            parts = class_name.split("_")
            crop = parts[0]
            disease_raw = "_".join(parts[1:])
            disease = disease_raw.replace("_", " ")
        
        return crop, disease
    
    def _is_healthy(self, class_name: str) -> bool:
        """Determine if class indicates healthy plant"""
        return "healthy" in class_name.lower()
    
    # ========================================================================
    # DISEASE INFORMATION
    # ========================================================================
    
    def _get_disease_info(self, predicted_class: str, crop: str, is_healthy: bool) -> Dict:
        """Get disease information from database"""
        # Build possible database keys
        keys_to_try = [
            predicted_class,
            f"{crop}_{predicted_class.split('_', 1)[1] if '_' in predicted_class else predicted_class}",
            f"{crop}_Healthy" if is_healthy else None
        ]
        
        for key in keys_to_try:
            if key and key in self.disease_database:
                logger.debug(f"Found disease info: {key}")
                return self.disease_database[key]
        
        logger.warning(f"Disease info not found for: {predicted_class}")
        
        # Return defaults
        if is_healthy:
            return {
                'disease_name': 'Healthy',
                'status': 'Healthy',
                'severity': 'None',
                'medicine': 'None',
                'treatment': 'Continue regular maintenance and monitoring',
                'prevention': 'Maintain proper spacing, watering, and nutrition. Regular monitoring recommended.',
                'symptoms': ['No visible disease signs', 'Vibrant green leaves', 'Normal growth pattern'],
                'message': f'Your {crop} plant is healthy.'
            }
        else:
            disease_name = predicted_class.split("_")[-1]
            return {
                'disease_name': disease_name,
                'status': 'Diseased',
                'severity': 'Medium',
                'medicine': 'Consult agricultural specialist',
                'treatment': 'Remove affected plant parts, apply fungicide, improve air circulation',
                'prevention': 'Maintain proper spacing, avoid overhead watering, sanitize tools',
                'symptoms': [f'Symptoms of {disease_name} detected'],
                'message': f'{disease_name} detected. Seek specialist advice.'
            }
    
    def _build_comprehensive_treatment(self, crop: str, disease: str, is_healthy: bool, 
                                      info: Dict) -> Dict:
        """Build comprehensive crop-specific treatment recommendations"""
        treatment = {}
        
        if is_healthy:
            treatment['overall'] = f'Your {crop} is healthy. Maintain current care practices.'
            treatment['scientific'] = 'No treatment needed'
            treatment['organic'] = 'No treatment needed'
            treatment['prevention'] = info.get('prevention', 'Regular monitoring')
            
        else:
            # BRINJAL SPECIFIC
            if crop == "Brinjal":
                if "Little" in disease and "Leaf" in disease:
                    treatment['overall'] = 'Little Leaf - Zinc deficiency disease requiring immediate supplementation'
                    treatment['scientific'] = (
                        '1. Zinc Sulfate 0.5% spray - 2-3 applications at 10-15 day intervals\n'
                        '2. Borax solution 0.2% as alternative\n'
                        '3. Imidacloprid 17.8SL 1ml/L to control whiteflies/mites\n'
                        '4. Repeat every 7-10 days for 4-5 weeks'
                    )
                    treatment['organic'] = (
                        '1. Neem oil 5% spray every 7 days for vector control\n'
                        '2. Zinc-rich compost application\n'
                        '3. Manual removal of severely affected leaves\n'
                        '4. Improved plant spacing\n'
                        '5. Companion planting with marigold'
                    )
                    
                elif "Leaf Spot" in disease:
                    treatment['overall'] = 'Leaf Spot - Fungal disease requiring fungicide treatment'
                    treatment['scientific'] = (
                        '1. Mancozeb 75% 2g/L or Copper fungicide\n'
                        '2. Apply every 7-10 days\n'
                        '3. Remove infected leaves\n'
                        '4. Improve air circulation'
                    )
                    treatment['organic'] = (
                        '1. Sulfur dust 3g/L\n'
                        '2. Copper-based organic fungicide\n'
                        '3. Manual leaf removal\n'
                        '4. Improved spacing\n'
                        '5. Avoid overhead watering'
                    )
                    
                elif "Blight" in disease:
                    treatment['overall'] = 'Blight - Serious fungal disease requiring aggressive treatment'
                    treatment['scientific'] = (
                        '1. Chlorothalonil 75% 2.5g/L or Copper fungicide\n'
                        '2. Weekly applications required\n'
                        '3. Prune affected branches\n'
                        '4. Remove infected plant material'
                    )
                    treatment['organic'] = (
                        '1. Sulfur or Bordeaux mixture\n'
                        '2. Neem oil spray\n'
                        '3. Affected plant removal\n'
                        '4. Improve drainage\n'
                        '5. Avoid overhead irrigation'
                    )
                else:
                    treatment['overall'] = f'{disease} detected on Brinjal'
                    treatment['scientific'] = info.get('treatment', 'Specialist consultation')
                    treatment['organic'] = 'Apply organic fungicide'
            
            # GRAPES SPECIFIC
            elif crop == "Grapes":
                if "Black Rot" in disease:
                    treatment['overall'] = 'Black Rot - Requires immediate fungicide treatment'
                    treatment['scientific'] = (
                        '1. Mancozeb 75% 2g/L immediately\n'
                        '2. Or Copper fungicide 2g/L\n'
                        '3. Remove infected berries and leaves\n'
                        '4. Repeat every 7-10 days\n'
                        '5. Improve drainage and air flow'
                    )
                    treatment['organic'] = (
                        '1. Sulfur dust 3%\n'
                        '2. Copper fungicide 0.5%\n'
                        '3. Remove and destroy infected parts\n'
                        '4. Prune for air circulation\n'
                        '5. Drip irrigation only'
                    )
                    treatment['fungicide'] = 'Mancozeb 75% or Copper fungicide'
                    treatment['irrigation'] = 'Drip irrigation, avoid wetting foliage'
                    
                elif "Black Measles" in disease or "Esca" in disease:
                    treatment['overall'] = 'Esca (Black Measles) - Critical. Requires professional intervention'
                    treatment['scientific'] = (
                        '1. Carbendazim 50% 1ml/L on pruning wounds\n'
                        '2. Or Propiconazole 25% EC 1ml/L\n'
                        '3. Prune only during dry season\n'
                        '4. Remove severely affected canes\n'
                        '5. Sterilize tools with bleach'
                    )
                    treatment['organic'] = (
                        '1. Remove and burn infected wood\n'
                        '2. Improve vineyard drainage\n'
                        '3. Reduce stress conditions\n'
                        '4. Avoid pruning wounds\n'
                        '5. Maintain good air flow'
                    )
                    treatment['fungicide'] = 'Carbendazim or Propiconazole'
                    treatment['irrigation'] = 'Maintain consistent moisture, apply during dormancy'
                    
                elif "Isariopsis" in disease or "Leaf" in disease:
                    treatment['overall'] = 'Leaf Blight - Moderate severity, manageable with fungicide'
                    treatment['scientific'] = (
                        '1. Mancozeb 75% 2g/L or Sulfur 3g/L\n'
                        '2. Remove infected leaves\n'
                        '3. Clean fallen leaves\n'
                        '4. Repeat every 10-14 days\n'
                        '5. Improve canopy air flow'
                    )
                    treatment['organic'] = (
                        '1. Sulfur dust 3g/L\n'
                        '2. Copper fungicide 0.5%\n'
                        '3. Manual leaf removal\n'
                        '4. Improved spacing\n'
                        '5. Avoid overhead watering'
                    )
                    treatment['fungicide'] = 'Mancozeb 75% or Sulfur'
                    treatment['irrigation'] = 'Drip irrigation, water at base'
                else:
                    treatment['overall'] = f'{disease} detected - Apply fungicide'
                    treatment['scientific'] = info.get('treatment', 'Fungicide application')
                    treatment['organic'] = 'Organic fungicide spray'
            else:
                treatment['overall'] = f'{disease} detected - Seek specialist advice'
                treatment['scientific'] = 'Professional consultation recommended'
                treatment['organic'] = 'Organic alternatives available'
        
        treatment['prevention'] = info.get('prevention', 'Regular monitoring and maintenance')
        
        return treatment
    
    # ========================================================================
    # PREDICTION
    # ========================================================================
    
    def predict(self, image_path: str) -> Dict:
        """
        PRODUCTION PREDICTION - Real model inference ONLY
        
        Returns comprehensive disease prediction with recommendations
        """
        try:
            logger.info(f"\n{'='*90}")
            logger.info(f"Predicting disease from: {image_path}")
            logger.info(f"{'='*90}")
            
            # Validate image
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Preprocess
            logger.info("Preprocessing image...")
            image_array = self._preprocess_image(image_path)
            logger.info(f"✓ Shape: {image_array.shape}")
            
            # Get predictions
            logger.info("Getting model predictions...")
            raw_predictions = self.model.predict(image_array, verbose=0)
            
            if raw_predictions is None or len(raw_predictions) == 0:
                raise RuntimeError("Model returned no predictions")
            
            predictions = raw_predictions[0]
            
            # Validate softmax
            prob_sum = np.sum(predictions)
            if not (0.98 <= prob_sum <= 1.02):
                logger.warning(f"Softmax sum: {prob_sum} (expected ~1.0)")
            
            # Get predicted class
            predicted_idx = int(np.argmax(predictions))
            predicted_class = self.class_names[predicted_idx]
            confidence = float(predictions[predicted_idx]) * 100.0
            
            logger.info(f"✓ Prediction: {predicted_class}")
            logger.info(f"✓ Confidence: {confidence:.2f}%")
            
            # Log top predictions
            logger.debug("Top 3 predictions:")
            top_indices = np.argsort(predictions)[-3:][::-1]
            for idx in top_indices:
                logger.debug(f"  {self.class_names[idx]}: {predictions[idx]*100:.2f}%")
            
            # Extract crop and disease
            crop, disease = self._extract_crop_and_disease(predicted_class)
            is_healthy = self._is_healthy(predicted_class)
            status = "Healthy" if is_healthy else "Diseased"
            
            logger.info(f"✓ Crop: {crop}")
            logger.info(f"✓ Disease: {disease}")
            logger.info(f"✓ Status: {status}")
            
            # Get disease info
            disease_info = self._get_disease_info(predicted_class, crop, is_healthy)
            
            # Build treatment
            treatment = self._build_comprehensive_treatment(
                crop, disease, is_healthy, disease_info
            )
            
            # Assemble response
            response = {
                'success': True,
                'crop': crop,
                'disease': disease,
                'status': status,
                'confidence': round(confidence, 2),
                'severity': disease_info.get('severity', 'Unknown'),
                'symptoms': disease_info.get('symptoms', []),
                'medicine': treatment.get('fungicide', disease_info.get('medicine', 'N/A')),
                'treatment': treatment.get('scientific', disease_info.get('treatment', 'N/A')),
                'organic_treatment': treatment.get('organic', 'N/A'),
                'prevention': treatment.get('prevention', 'N/A'),
                'irrigation': treatment.get('irrigation', 'N/A'),
                'recommendation': treatment.get('overall', disease_info.get('message', '')),
                'message': disease_info.get('message', ''),
                'confidence_level': 'High' if confidence >= self.HIGH_CONFIDENCE else ('Medium' if confidence >= self.LOW_CONFIDENCE else 'Low')
            }
            
            # Remove N/A values for cleaner output
            response = {k: v for k, v in response.items() if v not in ['N/A', None, []]}
            
            logger.info(f"✓ Prediction complete")
            logger.info(f"{'='*90}\n")
            
            return response
        
        except FileNotFoundError as e:
            logger.error(f"❌ File error: {str(e)}")
            return {'success': False, 'error': str(e)}
        except ValueError as e:
            logger.error(f"❌ Preprocessing error: {str(e)}")
            return {'success': False, 'error': f'Image processing failed: {str(e)}'}
        except Exception as e:
            logger.error(f"❌ Error: {str(e)}", exc_info=True)
            return {'success': False, 'error': str(e)}


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def predict_image(image_path: str) -> Dict:
    """Quick prediction"""
    try:
        predictor = CropDiseasePredictor()
        return predictor.predict(image_path)
    except Exception as e:
        return {'success': False, 'error': str(e)}


def print_prediction(result: Dict) -> None:
    """Print prediction in formatted output"""
    print("\n" + "="*90)
    print(" "*30 + "CROP DISEASE PREDICTION RESULTS")
    print("="*90)
    
    if not result.get('success'):
        print(f"\n❌ Error: {result.get('error', 'Unknown')}\n")
        return
    
    print(f"\n🌾 CROP: {result['crop']}")
    print(f"📊 STATUS: {result['status']} ({result['confidence']}% confidence)")
    print(f"🔍 DISEASE: {result.get('disease', 'N/A')}")
    print(f"⚠️  SEVERITY: {result.get('severity', 'N/A')}")
    
    if result['status'] == 'Diseased':
        if result.get('symptoms'):
            print(f"\n🦠 SYMPTOMS:")
            for s in result['symptoms']:
                print(f"   • {s}")
        
        if result.get('medicine'):
            print(f"\n💊 MEDICINE: {result['medicine']}")
        
        if result.get('treatment'):
            print(f"\n🧪 TREATMENT:\n{result['treatment']}")
        
        if result.get('organic_treatment'):
            print(f"\n🌿 ORGANIC TREATMENT:\n{result['organic_treatment']}")
        
        if result.get('irrigation'):
            print(f"\n💧 IRRIGATION: {result['irrigation']}")
    
    if result.get('prevention'):
        print(f"\n🛡️  PREVENTION:\n{result['prevention']}")
    
    print("\n" + "="*90 + "\n")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        print("Usage: python predict_final.py <image_path>")
        print("\nExample:")
        print("  python predict_final.py test_images/brinjal.jpg")
        sys.exit(0)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: {image_path} not found")
        sys.exit(1)
    
    try:
        predictor = CropDiseasePredictor()
        result = predictor.predict(image_path)
        print_prediction(result)
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
