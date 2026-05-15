"""
PRODUCTION-READY CROP DISEASE PREDICTION SYSTEM
================================================

REAL MODEL INFERENCE - NO FALLBACK, NO FAKE PREDICTIONS

Core Features:
✓ Real TensorFlow/Keras model prediction only
✓ Proper softmax confidence extraction
✓ argmax-based class selection
✓ 224x224 image preprocessing + normalize [0,1]
✓ Comprehensive medical/agricultural recommendations
✓ Crop-specific disease detection
✓ Severity assessment
✓ Scientific + organic treatment options
✓ Confidence percentage from actual softmax
✓ Production-grade error handling

Supported Crops & Diseases:
BRINJAL:
  - Brinjal_Healthy (no disease)
  - Brinjal_Little_Leaf (zinc deficiency/mite transmission)
  - Brinjal_Leaf_Spot (fungal)
  - Brinjal_Blight (fungal)

GRAPES:
  - Grapes_Healthy (no disease)
  - Grapes_Black_Measles (esca fungal)
  - Grapes_Black_Rot (guignardia fungal)
  - Grapes_Isariopsis_Leaf_Spot (leaf blight)
"""

import os
import json
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
import logging
from typing import Dict, Tuple, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionCropDiseasePredictor:
    """Production-grade crop disease prediction engine"""
    
    # Model paths - try new format first, fallback to h5
    MODEL_PATHS = [
        "artifacts/crop_disease_model.keras",
        "artifacts/crop_disease_model.h5",
    ]
    
    CLASSES_PATH = "artifacts/class_names.json"
    DISEASE_DB_PATH = "disease_database.json"
    
    # Image processing constants
    TARGET_SIZE = 224
    NORMALIZATION_FACTOR = 255.0
    
    # Thresholds
    CONFIDENCE_THRESHOLD = 70.0  # Warning threshold
    MINIMUM_VALID_CONFIDENCE = 10.0  # Should never be below this
    
    def __init__(self):
        """Initialize production predictor"""
        self.model = None
        self.class_names = []
        self.disease_database = {}
        
        logger.info("\n" + "="*80)
        logger.info("INITIALIZING PRODUCTION CROP DISEASE PREDICTOR")
        logger.info("="*80)
        
        self._load_model()
        self._load_classes()
        self._load_disease_database()
        
        logger.info("✓ Production predictor initialized successfully")
        logger.info("="*80 + "\n")
    
    def _load_model(self) -> None:
        """Load trained Keras model"""
        model_path = None
        
        for path in self.MODEL_PATHS:
            if os.path.exists(path):
                model_path = path
                break
        
        if not model_path:
            raise FileNotFoundError(
                f"Model not found. Checked:\n"
                f"  {', '.join(self.MODEL_PATHS)}\n"
                f"Run: python train_unified.py"
            )
        
        try:
            self.model = keras.models.load_model(model_path)
            logger.info(f"✓ Model loaded: {model_path}")
            logger.info(f"  Input shape: {self.model.input_shape}")
            logger.info(f"  Output shape: {self.model.output_shape}")
            
            if self.model is None:
                raise RuntimeError("Model loaded but is None")
                
        except Exception as e:
            raise RuntimeError(f"Failed to load model: {str(e)}")
    
    def _load_classes(self) -> None:
        """Load class names mapping"""
        if not os.path.exists(self.CLASSES_PATH):
            raise FileNotFoundError(
                f"Classes file not found: {self.CLASSES_PATH}\n"
                f"Required: artifacts/class_names.json"
            )
        
        try:
            with open(self.CLASSES_PATH, 'r') as f:
                data = json.load(f)
            
            # Handle nested format
            if isinstance(data, dict) and 'classes' in data:
                classes_dict = data['classes']
            else:
                classes_dict = data
            
            # Extract classes in order (0, 1, 2, ...)
            num_classes = len(classes_dict)
            self.class_names = []
            for i in range(num_classes):
                if str(i) not in classes_dict:
                    raise KeyError(f"Missing class index {i}")
                self.class_names.append(classes_dict[str(i)])
            
            logger.info(f"✓ Classes loaded: {num_classes} classes")
            for idx, name in enumerate(self.class_names):
                logger.info(f"    [{idx}] {name}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to load classes: {str(e)}")
    
    def _load_disease_database(self) -> None:
        """Load disease information database"""
        if not os.path.exists(self.DISEASE_DB_PATH):
            logger.warning(f"⚠ Disease database not found: {self.DISEASE_DB_PATH}")
            logger.warning("  Predictions will have limited information")
            return
        
        try:
            with open(self.DISEASE_DB_PATH, 'r') as f:
                data = json.load(f)
            
            self.disease_database = data.get('diseases', {})
            logger.info(f"✓ Disease database loaded: {len(self.disease_database)} diseases")
            
        except Exception as e:
            logger.warning(f"⚠ Failed to load disease database: {str(e)}")
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image to model-compatible format
        
        STRICT REQUIREMENTS:
        1. Read with OpenCV (BGR)
        2. Convert BGR → RGB
        3. Resize → 224x224
        4. Normalize → [0, 1] (divide by 255)
        5. Add batch dimension
        
        Returns: (1, 224, 224, 3) array
        """
        try:
            # Read image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Cannot read image: {image_path}")
            
            logger.debug(f"Original shape: {image.shape}")
            
            # Convert BGR → RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Resize to 224x224
            image = cv2.resize(image, (self.TARGET_SIZE, self.TARGET_SIZE),
                             interpolation=cv2.INTER_LINEAR)
            
            # Normalize to [0, 1]
            image = image.astype(np.float32) / self.NORMALIZATION_FACTOR
            
            # Validate
            if not (0.0 <= image.min() and image.max() <= 1.0):
                raise ValueError(f"Normalization failed: range [{image.min()}, {image.max()}]")
            
            # Add batch dimension
            image = np.expand_dims(image, axis=0)
            
            logger.debug(f"Preprocessed shape: {image.shape}, range: [{image.min():.4f}, {image.max():.4f}]")
            
            return image
            
        except Exception as e:
            raise ValueError(f"Image preprocessing failed: {str(e)}")
    
    def _parse_class_name(self, full_class_name: str) -> Tuple[str, str]:
        """
        Parse class name into crop and disease
        
        Format: "Crop_Diseases_DiseaseName"
        Examples:
        - "Brinjal_Diseases_Healthy" → ("Brinjal", "Healthy")
        - "Grapes_Diseases_Black_Rot" → ("Grapes", "Black Rot")
        - "Brinjal_Diseases_Little_Leaf" → ("Brinjal", "Little Leaf")
        """
        try:
            # Split by underscore
            parts = full_class_name.split('_')
            
            if len(parts) < 3:
                logger.warning(f"Unexpected class name format: {full_class_name}")
                return ("Unknown", full_class_name)
            
            # Extract crop (first part)
            crop = parts[0]
            
            # Extract disease (after "Diseases_")
            if "Diseases" in full_class_name:
                disease_part = full_class_name.split("Diseases_", 1)[1]
                # Convert underscores to spaces and format
                disease = disease_part.replace('_', ' ')
            else:
                disease = '_'.join(parts[1:])
            
            return crop, disease
            
        except Exception as e:
            logger.error(f"Error parsing class name: {str(e)}")
            return ("Unknown", full_class_name)
    
    def _is_healthy(self, class_name: str) -> bool:
        """Check if prediction indicates healthy plant"""
        return 'healthy' in class_name.lower()
    
    def _get_disease_info(self, crop: str, disease: str, is_healthy: bool) -> Dict:
        """
        Retrieve disease information from database
        
        Keys: "{Crop}_{Disease}" or "{Crop}_Healthy"
        """
        # Build database lookup keys
        if is_healthy:
            db_keys = [f"{crop}_Healthy", f"{crop.lower()}_healthy"]
        else:
            # Try multiple variations
            db_keys = [
                f"{crop}_{disease}",
                f"{crop}_{disease.replace(' ', '_')}",
                f"{crop}_{disease.lower()}",
                f"{crop}_{disease.replace(' ', '_').lower()}"
            ]
        
        # Find in database
        for key in db_keys:
            if key in self.disease_database:
                logger.debug(f"Found disease info: {key}")
                return self.disease_database[key]
        
        # Not found - return defaults
        logger.warning(f"Disease info not found for {crop} {disease}")
        
        if is_healthy:
            return {
                'crop': crop,
                'disease_name': 'Healthy',
                'status': 'Healthy',
                'severity': 'None',
                'medicine': 'None',
                'treatment': 'Continue regular maintenance',
                'prevention': 'Monitor plant health regularly',
                'symptoms': ['No visible disease signs'],
                'causes': ['Plant is healthy'],
                'message': f'Your {crop} plant is healthy'
            }
        else:
            return {
                'crop': crop,
                'disease_name': disease,
                'status': 'Diseased',
                'severity': 'Medium',
                'medicine': 'Consult agricultural specialist',
                'treatment': 'Isolate plant and seek professional advice',
                'prevention': 'Improve air circulation and sanitation',
                'symptoms': [f'Signs of {disease}'],
                'causes': ['Disease condition detected'],
                'message': f'{disease} detected. Seek professional advice.'
            }
    
    def _build_recommendations(self, crop: str, disease: str,
                              is_healthy: bool, disease_info: Dict) -> Dict:
        """Build comprehensive treatment recommendations"""
        
        recommendations = {
            'overall': disease_info.get('message', ''),
            'prevention': disease_info.get('prevention', ''),
            'treatment': disease_info.get('treatment', ''),
            'medicine': disease_info.get('medicine', ''),
            'severity': disease_info.get('severity', '')
        }
        
        # Brinjal-specific recommendations
        if crop == "Brinjal":
            if not is_healthy:
                if "little leaf" in disease.lower():
                    recommendations['scientific'] = (
                        "1. Apply Zinc Sulfate (0.5%) foliar spray 2-3 times (10-15 day intervals)\n"
                        "2. Imidacloprid 17.8SL (1ml/L) to control whiteflies and mites\n"
                        "3. Repeat spraying every 7-10 days for 4-5 weeks"
                    )
                    recommendations['organic'] = (
                        "1. Neem oil spray (5%) every 7 days\n"
                        "2. Zinc-rich compost/vermicompost\n"
                        "3. Manual leaf removal\n"
                        "4. Improve plant spacing\n"
                        "5. Companion planting with marigold"
                    )
                elif "leaf spot" in disease.lower():
                    recommendations['scientific'] = (
                        "1. Mancozeb 75% WP (2g/L) application\n"
                        "2. Remove infected leaves\n"
                        "3. Repeat every 10-14 days"
                    )
                    recommendations['organic'] = (
                        "1. Sulfur dust (3g/L)\n"
                        "2. Copper fungicide (0.5%)\n"
                        "3. Remove affected leaves\n"
                        "4. Improve spacing"
                    )
                elif "blight" in disease.lower():
                    recommendations['scientific'] = (
                        "1. Metalaxyl + Mancozeb fungicide\n"
                        "2. Remove severely affected parts\n"
                        "3. Improve drainage"
                    )
                    recommendations['organic'] = (
                        "1. Bordeaux mixture (1%)\n"
                        "2. Remove infected plant parts\n"
                        "3. Improve air circulation"
                    )
        
        # Grapes-specific recommendations
        elif crop == "Grapes":
            if not is_healthy:
                if "black rot" in disease.lower():
                    recommendations['scientific'] = (
                        "1. Mancozeb 75% WP (2g/L) immediately\n"
                        "2. Remove infected berries/leaves\n"
                        "3. Repeat every 7-10 days\n"
                        "4. Improve drainage"
                    )
                    recommendations['organic'] = (
                        "1. Sulfur dust (3%)\n"
                        "2. Copper fungicide (0.5%)\n"
                        "3. Remove infected parts\n"
                        "4. Prune for air circulation"
                    )
                elif "black measles" in disease.lower() or "esca" in disease.lower():
                    recommendations['scientific'] = (
                        "1. Carbendazim 50% WP (1ml/L) on pruning wounds\n"
                        "2. Prune only in dry season\n"
                        "3. Remove severely affected canes"
                    )
                    recommendations['organic'] = (
                        "1. Remove infected wood\n"
                        "2. Improve drainage\n"
                        "3. Reduce plant stress\n"
                        "4. Sanitize tools"
                    )
                elif "leaf spot" in disease.lower() or "isariopsis" in disease.lower():
                    recommendations['scientific'] = (
                        "1. Mancozeb 75% or Sulfur (3g/L)\n"
                        "2. Remove infected leaves\n"
                        "3. Clean fallen leaves\n"
                        "4. Repeat every 10-14 days"
                    )
                    recommendations['organic'] = (
                        "1. Sulfur dust (3g/L)\n"
                        "2. Copper fungicide (0.5%)\n"
                        "3. Remove infected leaves\n"
                        "4. Improve spacing"
                    )
        
        return recommendations
    
    def predict(self, image_path: str) -> Dict:
        """
        PRODUCTION PREDICTION - REAL MODEL ONLY
        
        Returns comprehensive prediction with confidence, disease info, and treatment
        """
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"PROCESSING IMAGE: {image_path}")
            logger.info(f"{'='*80}")
            
            # Validate image exists
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Step 1: Preprocess image
            logger.info("Step 1: Preprocessing image...")
            image_array = self._preprocess_image(image_path)
            logger.info(f"  ✓ Shape: {image_array.shape}")
            
            # Step 2: Get model predictions
            logger.info("Step 2: Running model inference...")
            predictions = self.model.predict(image_array, verbose=0)
            
            if predictions is None or len(predictions) == 0:
                raise RuntimeError("Model returned no predictions")
            
            prediction_probs = predictions[0]  # Get first (only) batch
            
            # Verify softmax output sums to ~1.0
            prob_sum = float(np.sum(prediction_probs))
            logger.debug(f"  Softmax sum: {prob_sum:.6f} (expected ~1.0)")
            
            # Step 3: Find predicted class using argmax
            logger.info("Step 3: Determining predicted class...")
            predicted_idx = int(np.argmax(prediction_probs))
            
            if predicted_idx < 0 or predicted_idx >= len(self.class_names):
                raise IndexError(f"Invalid index: {predicted_idx}, valid 0-{len(self.class_names)-1}")
            
            predicted_class_name = self.class_names[predicted_idx]
            confidence_score = float(prediction_probs[predicted_idx])
            confidence_percent = round(confidence_score * 100.0, 2)
            
            logger.info(f"  ✓ Class: {predicted_class_name}")
            logger.info(f"  ✓ Confidence: {confidence_percent}%")
            
            # Log all predictions for debugging
            logger.debug("\n  All class probabilities:")
            for i, (cls, prob) in enumerate(zip(self.class_names, prediction_probs)):
                logger.debug(f"    [{i}] {cls:45s} {prob*100:6.2f}%")
            
            # Step 4: Parse prediction
            logger.info("Step 4: Parsing prediction...")
            crop, disease = self._parse_class_name(predicted_class_name)
            is_healthy = self._is_healthy(predicted_class_name)
            status = "Healthy" if is_healthy else "Diseased"
            logger.info(f"  ✓ Crop: {crop}")
            logger.info(f"  ✓ Disease: {disease}")
            logger.info(f"  ✓ Status: {status}")
            
            # Step 5: Get disease information
            logger.info("Step 5: Retrieving disease information...")
            disease_info = self._get_disease_info(crop, disease, is_healthy)
            
            # Step 6: Build recommendations
            logger.info("Step 6: Building recommendations...")
            recommendations = self._build_recommendations(
                crop, disease, is_healthy, disease_info
            )
            
            # Step 7: Assemble response
            logger.info("Step 7: Assembling response...")
            
            response = {
                'success': True,
                'crop': crop,
                'disease': disease,
                'status': status,
                'confidence': confidence_percent,
                'message': disease_info.get('message', ''),
                'symptoms': disease_info.get('symptoms', []),
                'causes': disease_info.get('causes', []),
                'severity': disease_info.get('severity', 'Unknown'),
                'medicine': recommendations.get('medicine', 'N/A'),
                'treatment': recommendations.get('treatment', 'N/A'),
                'scientific_treatment': recommendations.get('scientific', 'N/A'),
                'organic_solution': recommendations.get('organic', 'N/A'),
                'prevention': recommendations.get('prevention', 'N/A'),
                'recommendation': recommendations.get('overall', disease_info.get('message', ''))
            }
            
            # Add confidence warning if needed
            if confidence_percent < self.CONFIDENCE_THRESHOLD:
                response['confidence_warning'] = f"Low confidence ({confidence_percent}%) - consult specialist"
            
            logger.info(f"✓ Prediction complete: {status} ({confidence_percent}%)")
            logger.info(f"{'='*80}\n")
            
            return response
            
        except FileNotFoundError as e:
            logger.error(f"❌ File error: {str(e)}")
            return {'success': False, 'error': 'FileNotFound', 'message': str(e)}
        
        except ValueError as e:
            logger.error(f"❌ Preprocessing error: {str(e)}")
            return {'success': False, 'error': 'PreprocessingError', 'message': str(e)}
        
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
            return {'success': False, 'error': 'PredictionError', 'message': str(e)}


# Global predictor instance
_predictor = None


def get_predictor() -> ProductionCropDiseasePredictor:
    """Get or create predictor instance (lazy initialization)"""
    global _predictor
    if _predictor is None:
        _predictor = ProductionCropDiseasePredictor()
    return _predictor


def predict_image(image_path: str) -> Dict:
    """Simple prediction function"""
    return get_predictor().predict(image_path)


def print_prediction(result: Dict) -> None:
    """Print prediction in formatted output"""
    print("\n" + "="*90)
    print(" " * 25 + "CROP DISEASE PREDICTION RESULTS")
    print("="*90)
    
    if not result.get('success', False):
        print(f"\n❌ PREDICTION FAILED")
        print(f"Error: {result.get('error', 'Unknown')}")
        print(f"Message: {result.get('message', 'No details')}")
        print("="*90 + "\n")
        return
    
    # Basic info
    print(f"\n📍 CROP: {result.get('crop', 'Unknown')}")
    print(f"📊 STATUS: {result.get('status', 'Unknown')}")
    print(f"📈 CONFIDENCE: {result.get('confidence', 'N/A')}%")
    
    if result.get('confidence_warning'):
        print(f"⚠️  WARNING: {result['confidence_warning']}")
    
    # Disease details
    if result.get('status') == 'Diseased':
        print(f"\n🦠 DISEASE: {result.get('disease', 'Unknown')}")
        print(f"🔴 SEVERITY: {result.get('severity', 'Unknown')}")
        
        if result.get('symptoms'):
            print(f"\n📋 SYMPTOMS:")
            for symptom in result['symptoms']:
                print(f"   • {symptom}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATION: {result.get('recommendation', 'N/A')}")
    
    # Treatment
    if result.get('status') == 'Diseased':
        print(f"\n🧪 SCIENTIFIC TREATMENT:")
        print(result.get('scientific_treatment', 'N/A'))
        
        print(f"\n🌿 ORGANIC SOLUTION:")
        print(result.get('organic_solution', 'N/A'))
        
        print(f"\n💊 MEDICINE: {result.get('medicine', 'N/A')}")
    
    print(f"\n🛡️  PREVENTION: {result.get('prevention', 'N/A')}")
    print("\n" + "="*90 + "\n")


def main():
    """Command-line interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python predict_production.py <image_path>")
        print("Example: python predict_production.py test.jpg")
        sys.exit(0)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        sys.exit(1)
    
    try:
        predictor = get_predictor()
        result = predictor.predict(image_path)
        print_prediction(result)
        sys.exit(0 if result.get('success') else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        logger.exception("Fatal error")
        sys.exit(1)


if __name__ == "__main__":
    main()
