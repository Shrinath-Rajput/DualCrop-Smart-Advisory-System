"""
PRODUCTION-READY CROP DISEASE PREDICTION SYSTEM
====================================================
Advanced disease detection using trained TensorFlow/Keras model

CRITICAL FEATURES:
✓ REAL model inference only - NO FALLBACK MODE
✓ NO fake predictions - NO hardcoded confidence
✓ Proper image preprocessing: 224x224 + normalize /255.0
✓ Softmax confidence from model output
✓ argmax-based class selection
✓ Comprehensive agricultural recommendations
✓ Disease severity assessment
✓ Scientific + organic treatment options
✓ Crop-specific guidance
✓ No placeholder values - real predictions only

SUPPORTED CROPS:
- Brinjal (Little Leaf disease detection)
- Grapes (4 disease types + healthy)

CONFIDENCE: Based on actual softmax probabilities
PREPROCESSING: 224x224 RGB, normalized [0, 1]
"""

import os
import json
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
import logging
from typing import Dict, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CropDiseasePredictor:
    """PRODUCTION-READY Crop Disease Prediction Engine"""
    
    # Model and resource paths
    MODEL_PATH = "artifacts/crop_disease_model.h5"
    MODEL_PATH_KERAS = "artifacts/crop_disease_model.keras"
    CLASSES_PATH = "artifacts/class_names.json"
    DISEASE_DB_PATH = "disease_database.json"
    
    # Image preprocessing constants
    TARGET_SIZE = 224
    NORMALIZATION_FACTOR = 255.0
    
    # Confidence threshold - warnings if below this
    CONFIDENCE_THRESHOLD = 70.0
    
    def __init__(self):
        """Initialize prediction engine with model and resources"""
        self.model = None
        self.class_names = []
        self.disease_database = {}
        
        logger.info("="*80)
        logger.info("Initializing Production-Ready Crop Disease Predictor")
        logger.info("="*80)
        
        self._load_model()
        self._load_classes()
        self._load_disease_database()
        
        logger.info("✓ Predictor initialized successfully")
        logger.info("="*80)
    
    def _load_model(self) -> None:
        """Load trained TensorFlow/Keras model from artifacts folder"""
        model_path = None
        
        # Try .keras format first (TensorFlow 2.11+)
        if os.path.exists(self.MODEL_PATH_KERAS):
            model_path = self.MODEL_PATH_KERAS
        # Fall back to .h5 format
        elif os.path.exists(self.MODEL_PATH):
            model_path = self.MODEL_PATH
        else:
            raise FileNotFoundError(
                f"Model files not found!\n"
                f"Checked paths:\n"
                f"  - {self.MODEL_PATH_KERAS}\n"
                f"  - {self.MODEL_PATH}\n"
                f"Please train the model first using: python train_improved.py"
            )
        
        try:
            self.model = keras.models.load_model(model_path)
            logger.info(f"✓ Model loaded: {model_path}")
            logger.info(f"  Input shape:  {self.model.input_shape}")
            logger.info(f"  Output shape: {self.model.output_shape}")
            
            # Verify model is properly built
            if self.model is None:
                raise RuntimeError("Model loaded but is None")
                
        except Exception as e:
            raise RuntimeError(f"Failed to load model from {model_path}: {str(e)}")
    
    def _load_classes(self) -> None:
        """Load class names from JSON file"""
        if not os.path.exists(self.CLASSES_PATH):
            raise FileNotFoundError(
                f"Class names file not found: {self.CLASSES_PATH}\n"
                f"Required: artifacts/class_names.json"
            )
        
        try:
            with open(self.CLASSES_PATH, 'r') as f:
                data = json.load(f)
            
            # Handle multiple JSON formats
            if isinstance(data, dict) and 'classes' in data:
                classes_dict = data['classes']
            else:
                classes_dict = data
            
            # Validate class dictionary
            if not isinstance(classes_dict, dict):
                raise ValueError(f"Classes must be a dictionary, got {type(classes_dict)}")
            
            # Extract class names in order (0, 1, 2, ...)
            num_classes = len(classes_dict)
            self.class_names = []
            for i in range(num_classes):
                if str(i) not in classes_dict:
                    raise KeyError(f"Missing class index {i} in class_names.json")
                self.class_names.append(classes_dict[str(i)])
            
            logger.info(f"✓ Classes loaded: {num_classes} classes")
            for idx, name in enumerate(self.class_names):
                logger.info(f"    [{idx}] {name}")
                
        except Exception as e:
            raise RuntimeError(f"Failed to load classes from {self.CLASSES_PATH}: {str(e)}")
    
    def _load_disease_database(self) -> None:
        """Load comprehensive disease information database"""
        if not os.path.exists(self.DISEASE_DB_PATH):
            logger.warning(f"⚠ Disease database not found: {self.DISEASE_DB_PATH}")
            logger.warning("  Predictions will have limited information")
            return
        
        try:
            with open(self.DISEASE_DB_PATH, 'r') as f:
                data = json.load(f)
            
            self.disease_database = data.get('diseases', {})
            logger.info(f"✓ Disease database loaded: {len(self.disease_database)} disease entries")
            
        except Exception as e:
            logger.warning(f"⚠ Failed to load disease database: {str(e)}")
    
    def _preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for model prediction - STRICT REQUIREMENTS
        
        Processing steps:
        1. Read image with OpenCV (BGR format)
        2. Convert BGR → RGB
        3. Resize to 224x224
        4. Normalize with /255.0 (convert to [0, 1] range)
        5. Add batch dimension: (224, 224, 3) → (1, 224, 224, 3)
        
        Args:
            image_path: Path to image file
            
        Returns:
            np.ndarray: Preprocessed image with shape (1, 224, 224, 3)
            
        Raises:
            ValueError: If image cannot be read or processed
        """
        # Step 1: Read image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Cannot read image from: {image_path}")
        
        original_shape = image.shape
        logger.debug(f"Original image shape: {original_shape}")
        
        # Step 2: Convert BGR to RGB (OpenCV loads in BGR)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Step 3: Resize to 224x224
        image = cv2.resize(image, (self.TARGET_SIZE, self.TARGET_SIZE), 
                          interpolation=cv2.INTER_LINEAR)
        
        # Step 4: Normalize to [0, 1] range
        image = image.astype(np.float32) / self.NORMALIZATION_FACTOR
        
        # Validate normalization
        if np.min(image) < 0.0 or np.max(image) > 1.0:
            raise ValueError(f"Normalization failed: pixel range is [{np.min(image)}, {np.max(image)}]")
        
        # Step 5: Add batch dimension
        image = np.expand_dims(image, axis=0)
        
        logger.debug(f"Preprocessed shape: {image.shape}")
        logger.debug(f"Preprocessed range: [{np.min(image):.4f}, {np.max(image):.4f}]")
        
        return image
    
    def _extract_crop_and_disease(self, class_name: str) -> Tuple[str, str]:
        """
        Parse class name to extract crop type and disease name
        
        Expected class name format: "Crop_Prefix_DiseaseType"
        Examples:
        - "Binjal_Diseases_brinjal_little_leaf" → ("Brinjal", "Little Leaf")
        - "Grapes_Diseases_Black Rot" → ("Grapes", "Black Rot")
        - "Grapes_Diseases_Healthy" → ("Grapes", "Healthy")
        
        Args:
            class_name: Full class name from model
            
        Returns:
            Tuple of (crop_type, disease_name)
        """
        # Split by underscore
        parts = class_name.split('_')
        
        if len(parts) < 2:
            logger.warning(f"Unexpected class name format: {class_name}")
            return "Unknown", class_name
        
        # First part is crop name (Brinjal or Grapes)
        crop_raw = parts[0]
        crop = "Brinjal" if crop_raw == "Binjal" else crop_raw
        
        # Extract disease name after "Diseases_"
        if "Diseases" in class_name:
            disease_raw = class_name.split("Diseases_", 1)[1]
            # Convert underscore format to title case
            if disease_raw == "brinjal_little_leaf":
                disease = "Little Leaf"
            else:
                disease = disease_raw
        else:
            disease = "_".join(parts[1:])
        
        return crop, disease
    
    def _is_healthy(self, class_name: str) -> bool:
        """
        Determine if predicted class indicates HEALTHY plant
        
        Returns True ONLY if model explicitly predicts healthy class
        
        Args:
            class_name: Predicted class name from model
            
        Returns:
            bool: True if healthy, False if diseased
        """
        return 'healthy' in class_name.lower()
    
    def _get_disease_info(self, predicted_class: str, crop: str, is_healthy: bool) -> Dict:
        """
        Retrieve disease information from database with EXACT matching
        
        Database key mapping:
        - "Grapes_Healthy", "Grapes_Black Rot", "Grapes_Black Measles", etc.
        - "Brinjal_Healthy", "Brinjal_brinjal_little_leaf"
        
        Args:
            predicted_class: Full class name from model
            crop: Extracted crop type
            is_healthy: Whether prediction is healthy
            
        Returns:
            Dict: Disease information (or defaults if not found)
        """
        # Extract disease part for database lookup
        disease_part = predicted_class.split("Diseases_", 1)[-1] if "Diseases_" in predicted_class else predicted_class
        
        # Build possible database keys
        if is_healthy:
            db_key = f"{crop}_Healthy"
        else:
            # Try direct key first
            if disease_part == "brinjal_little_leaf":
                db_key = f"{crop}_brinjal_little_leaf"
            else:
                db_key = f"{crop}_{disease_part}"
        
        # Look up in database
        if db_key in self.disease_database:
            logger.debug(f"Found disease info with key: {db_key}")
            return self.disease_database[db_key]
        
        logger.warning(f"Disease info not found for key: {db_key}, using defaults")
        
        # Generate safe defaults (NO PLACEHOLDERS)
        if is_healthy:
            return {
                'disease_name': 'Healthy',
                'status': 'Healthy',
                'severity': 'None',
                'medicine': 'None',
                'treatment': 'Continue regular maintenance and monitoring to keep plant healthy',
                'prevention': 'Monitor plant health regularly, maintain proper spacing, ensure adequate water and nutrition',
                'symptoms': ['No visible disease signs', 'Vibrant green leaves', 'Normal growth'],
                'causes': ['Plant is healthy'],
                'message': f'Your {crop} plant is healthy. No disease detected.'
            }
        else:
            return {
                'disease_name': disease_part,
                'status': 'Diseased',
                'severity': 'Medium',
                'medicine': 'Consult agricultural expert for diagnosis confirmation',
                'treatment': 'Isolate plant, remove affected leaves, consult with agricultural specialist',
                'prevention': 'Improve air circulation, maintain proper hygiene, monitor regularly',
                'symptoms': [f'Potential symptoms of {disease_part}'],
                'causes': ['Disease condition detected by model'],
                'message': f'{disease_part} detected. Seek professional agricultural advice.'
            }
    
    def _build_treatment_recommendations(self, crop: str, disease_name: str, 
                                        is_healthy: bool, disease_info: Dict) -> Dict:
        """
        Build comprehensive treatment recommendations with agricultural expertise
        
        Returns crop-specific guidance with:
        - Scientific treatments
        - Organic/sustainable options
        - Prevention strategies
        - Severity assessment
        
        Args:
            crop: Crop type
            disease_name: Disease name
            is_healthy: Health status
            disease_info: Disease information from database
            
        Returns:
            Dict: Comprehensive recommendations
        """
        recommendations = {}
        
        if is_healthy:
            recommendations["overall"] = f"Your {crop} plant is healthy. Continue current care practices."
            recommendations["scientific_treatment"] = "No treatment needed"
            recommendations["organic_treatment"] = "No treatment needed"
            recommendations["prevention"] = disease_info.get('prevention', 'Regular monitoring and maintenance')
            
        else:
            # BRINJAL-specific recommendations
            if crop == "Brinjal":
                if "little_leaf" in disease_name.lower():
                    recommendations["overall"] = "Little Leaf disease detected. Requires immediate zinc supplementation and insect vector control."
                    recommendations["scientific_treatment"] = (
                        "1. Apply Zinc Sulfate (0.5%) as foliar spray 2-3 times at 10-15 day intervals\n"
                        "2. Or use Borax solution (0.2%) as supplement\n"
                        "3. Apply Imidacloprid 17.8SL (1ml/L) to control whiteflies and mites\n"
                        "4. Repeat spraying every 7-10 days for 4-5 weeks"
                    )
                    recommendations["organic_treatment"] = (
                        "1. Neem oil spray (5%) every 7 days to control insect vectors\n"
                        "2. Zinc-rich compost or vermicompost application\n"
                        "3. Manual removal of severely affected leaves\n"
                        "4. Plant spacing improvement for better air circulation\n"
                        "5. Companion planting with marigold to repel insects"
                    )
                    recommendations["prevention"] = (
                        "Use disease-resistant varieties, maintain soil fertility, control vector insects early, "
                        "ensure proper zinc in soil, avoid water stress"
                    )
                else:
                    recommendations["overall"] = f"{disease_name} detected on Brinjal. Consult specialist."
                    recommendations["scientific_treatment"] = disease_info.get('treatment', 'Specialist consultation required')
                    recommendations["organic_treatment"] = "Use neem oil, sulfur dust, and proper sanitation"
                    recommendations["prevention"] = disease_info.get('prevention', 'Regular monitoring')
            
            # GRAPES-specific recommendations
            elif crop == "Grapes":
                if "Black Rot" in disease_name:
                    recommendations["overall"] = "Black Rot disease detected. Requires immediate fungicide treatment."
                    recommendations["scientific_treatment"] = (
                        "1. Apply Mancozeb 75% WP (2g/L) immediately\n"
                        "2. Or use Copper-based fungicide (2g/L)\n"
                        "3. Remove infected leaves and berries\n"
                        "4. Repeat every 7-10 days until control\n"
                        "5. Improve drainage and air circulation"
                    )
                    recommendations["organic_treatment"] = (
                        "1. Sulfur dust (3%) application\n"
                        "2. Copper fungicide spray (0.5%)\n"
                        "3. Remove and destroy infected plant parts\n"
                        "4. Improve canopy air circulation by pruning\n"
                        "5. Avoid overhead irrigation"
                    )
                    recommendations["fungicide"] = "Mancozeb 75% or Copper fungicide"
                    recommendations["irrigation_advice"] = "Use drip irrigation only, avoid wetting foliage, water early morning"
                    
                elif "Black Measles" in disease_name or "Esca" in disease_name:
                    recommendations["overall"] = "Esca (Black Measles) detected. This is serious. Requires urgent professional intervention."
                    recommendations["scientific_treatment"] = (
                        "1. Apply Carbendazim 50% WP (1ml/L) to pruning wounds immediately\n"
                        "2. Or Propiconazole 25% EC (1ml/L)\n"
                        "3. Prune only during dry season\n"
                        "4. Remove severely affected canes\n"
                        "5. Sanitize pruning tools with bleach between cuts"
                    )
                    recommendations["organic_treatment"] = (
                        "1. Remove and burn severely infected wood\n"
                        "2. Improve vineyard drainage\n"
                        "3. Reduce plant stress (adequate water/nutrition)\n"
                        "4. Avoid pruning wounds, use proper techniques\n"
                        "5. Maintain good air circulation"
                    )
                    recommendations["fungicide"] = "Carbendazim or Propiconazole (apply to pruning wounds)"
                    recommendations["irrigation_advice"] = "Maintain consistent moisture, avoid stress conditions, apply during dormancy"
                    
                elif "Leaf Spot" in disease_name or "Isariopsis" in disease_name:
                    recommendations["overall"] = "Leaf Blight (Isariopsis) detected. Moderate severity - manageable with fungicide."
                    recommendations["scientific_treatment"] = (
                        "1. Apply Mancozeb 75% WP (2g/L) or Sulfur (3g/L)\n"
                        "2. Remove infected leaves from plant\n"
                        "3. Clean up fallen leaves from ground\n"
                        "4. Repeat every 10-14 days\n"
                        "5. Improve canopy air circulation"
                    )
                    recommendations["organic_treatment"] = (
                        "1. Sulfur dust application (3g/L)\n"
                        "2. Copper fungicide spray (0.5%)\n"
                        "3. Remove infected leaves manually\n"
                        "4. Improve spacing for air flow\n"
                        "5. Avoid overhead watering"
                    )
                    recommendations["fungicide"] = "Mancozeb 75% or Sulfur"
                    recommendations["irrigation_advice"] = "Drip irrigation preferred, water at base, avoid wetting leaves"
                else:
                    recommendations["overall"] = f"{disease_name} detected. Standard fungicide treatment recommended."
                    recommendations["scientific_treatment"] = disease_info.get('treatment', 'Apply appropriate fungicide')
                    recommendations["organic_treatment"] = "Sulfur or copper-based organic fungicide"
                    recommendations["fungicide"] = disease_info.get('medicine', 'Consult specialist')
                    recommendations["irrigation_advice"] = "Use drip irrigation, avoid overhead watering"
            
            else:
                recommendations["overall"] = f"{disease_name} detected. Seek professional advice."
                recommendations["scientific_treatment"] = disease_info.get('treatment', 'Specialist consultation')
                recommendations["organic_treatment"] = "Organic treatments available"
                recommendations["prevention"] = disease_info.get('prevention', 'Standard prevention practices')
        
        return recommendations
    
    def predict(self, image_path: str) -> Dict:
        """
        PRODUCTION PREDICTION - Real model inference ONLY
        
        NO fallback mode, NO fake predictions, NO placeholders
        Uses real softmax confidence from model output
        
        Args:
            image_path: Path to input image file
            
        Returns:
            Dict with prediction results:
            {
                "success": bool,
                "crop": str,
                "disease": str,
                "status": "Healthy" | "Diseased",
                "confidence": float (0-100),
                "recommendation": str,
                "treatment": str,
                "prevention": str,
                "medicine": str,
                "severity": str,
                "symptoms": list,
                "scientific_treatment": str,
                "organic_treatment": str,
                ... (additional fields from database)
            }
        """
        try:
            logger.info(f"\n{'='*80}")
            logger.info(f"Processing image: {image_path}")
            logger.info(f"{'='*80}")
            
            # Validate image path
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image not found: {image_path}")
            
            # Step 1: Preprocess image
            logger.info("Step 1: Preprocessing image...")
            image_array = self._preprocess_image(image_path)
            logger.info(f"  ✓ Preprocessed shape: {image_array.shape}")
            
            # Step 2: Get raw model predictions (NO fallback)
            logger.info("Step 2: Getting model predictions...")
            raw_predictions = self.model.predict(image_array, verbose=0)
            
            if raw_predictions is None or len(raw_predictions) == 0:
                raise RuntimeError("Model returned no predictions")
            
            prediction_probs = raw_predictions[0]
            
            # Verify softmax output
            prob_sum = np.sum(prediction_probs)
            if not (0.99 <= prob_sum <= 1.01):
                logger.warning(f"Softmax probabilities sum to {prob_sum}, expected ~1.0")
            
            # Step 3: Find predicted class using argmax
            logger.info("Step 3: Determining predicted class...")
            predicted_idx = int(np.argmax(prediction_probs))
            
            if predicted_idx < 0 or predicted_idx >= len(self.class_names):
                raise IndexError(f"Invalid prediction index: {predicted_idx}, expected 0-{len(self.class_names)-1}")
            
            predicted_class = self.class_names[predicted_idx]
            confidence_score = float(prediction_probs[predicted_idx])
            confidence_percent = confidence_score * 100.0
            
            logger.info(f"  ✓ Predicted class: {predicted_class}")
            logger.info(f"  ✓ Confidence: {confidence_percent:.2f}%")
            
            # Log all predictions for debugging
            logger.debug("All predictions:")
            for i, (class_name, prob) in enumerate(zip(self.class_names, prediction_probs)):
                logger.debug(f"    [{i}] {class_name}: {prob*100:.2f}%")
            
            # Step 4: Extract crop and disease
            logger.info("Step 4: Extracting crop and disease type...")
            crop, disease = self._extract_crop_and_disease(predicted_class)
            is_healthy = self._is_healthy(predicted_class)
            status = "Healthy" if is_healthy else "Diseased"
            logger.info(f"  ✓ Crop: {crop}")
            logger.info(f"  ✓ Disease: {disease}")
            logger.info(f"  ✓ Status: {status}")
            
            # Step 5: Get disease information from database
            logger.info("Step 5: Retrieving disease information...")
            disease_info = self._get_disease_info(predicted_class, crop, is_healthy)
            
            # Step 6: Build comprehensive recommendations
            logger.info("Step 6: Building treatment recommendations...")
            recommendations = self._build_treatment_recommendations(
                crop, disease, is_healthy, disease_info
            )
            
            # Step 7: Assemble complete response
            logger.info("Step 7: Assembling response...")
            response = {
                'success': True,
                'crop': crop,
                'disease': disease,
                'status': status,
                'confidence': round(confidence_percent, 2),
                'recommendation': recommendations.get('overall', disease_info.get('message', 'See treatment details')),
                'treatment': recommendations.get('scientific_treatment', disease_info.get('treatment', 'N/A')),
                'organic_treatment': recommendations.get('organic_treatment', 'N/A'),
                'prevention': recommendations.get('prevention', disease_info.get('prevention', 'N/A')),
                'medicine': recommendations.get('fungicide', disease_info.get('medicine', 'N/A')),
                'irrigation_advice': recommendations.get('irrigation_advice', 'N/A'),
                'severity': disease_info.get('severity', 'Unknown'),
                'symptoms': disease_info.get('symptoms', []),
                'causes': disease_info.get('causes', []),
                'message': disease_info.get('message', ''),
                'scientific_treatment': recommendations.get('scientific_treatment', 'N/A'),
                'confidence_warning': 'Low confidence - consult specialist' if confidence_percent < self.CONFIDENCE_THRESHOLD else None
            }
            
            # Remove None values
            response = {k: v for k, v in response.items() if v is not None}
            
            logger.info(f"✓ Prediction complete: {status}")
            logger.info(f"{'='*80}\n")
            
            return response
        
        except FileNotFoundError as e:
            logger.error(f"❌ File error: {str(e)}")
            return {
                'success': False,
                'error': 'FileNotFound',
                'message': str(e)
            }
        
        except ValueError as e:
            logger.error(f"❌ Preprocessing error: {str(e)}")
            return {
                'success': False,
                'error': 'PreprocessingError',
                'message': f'Image preprocessing failed: {str(e)}'
            }
        
        except RuntimeError as e:
            logger.error(f"❌ Model error: {str(e)}")
            return {
                'success': False,
                'error': 'ModelError',
                'message': f'Model prediction failed: {str(e)}'
            }
        
        except Exception as e:
            logger.error(f"❌ Unexpected error: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': 'UnexpectedError',
                'message': f'Prediction error: {str(e)}'
            }


def predict_image(image_path: str) -> Dict:
    """
    Quick prediction function - Load model once and predict
    
    Args:
        image_path: Path to image file
        
    Returns:
        Prediction result dictionary
    """
    try:
        predictor = CropDiseasePredictor()
        return predictor.predict(image_path)
    except Exception as e:
        logger.error(f"Failed to initialize predictor: {str(e)}")
        return {
            'success': False,
            'error': 'InitializationError',
            'message': f'Failed to initialize predictor: {str(e)}'
        }


def print_prediction_details(result: Dict) -> None:
    """
    Print detailed prediction results in formatted output
    
    Args:
        result: Prediction result dictionary
    """
    print("\n" + "="*90)
    print(" " * 25 + "CROP DISEASE PREDICTION RESULTS")
    print("="*90)
    
    if not result.get('success', False):
        print(f"\n❌ PREDICTION FAILED")
        print(f"Error: {result.get('error', 'Unknown')}")
        print(f"Message: {result.get('message', 'No additional details')}")
        print("="*90 + "\n")
        return
    
    # Header information
    print(f"\n📍 CROP INFORMATION:")
    print(f"   Crop Type:          {result.get('crop', 'Unknown')}")
    print(f"   Status:             {result.get('status', 'Unknown')} ({result.get('confidence', 'N/A')}% confidence)")
    
    if result.get('confidence_warning'):
        print(f"   ⚠️  {result['confidence_warning']}")
    
    # Disease information
    if result.get('status') == 'Diseased':
        print(f"\n🦠 DISEASE INFORMATION:")
        print(f"   Disease Name:       {result.get('disease', 'Unknown')}")
        print(f"   Severity:           {result.get('severity', 'Unknown')}")
        
        if result.get('symptoms'):
            print(f"\n   Symptoms:")
            for symptom in result['symptoms']:
                print(f"      • {symptom}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print(f"   {result.get('recommendation', 'No specific recommendations')}")
    
    # Treatment information
    if result.get('status') == 'Diseased':
        print(f"\n🧪 SCIENTIFIC TREATMENT:")
        for line in str(result.get('scientific_treatment', 'N/A')).split('\n'):
            if line.strip():
                print(f"   {line}")
        
        print(f"\n🌿 ORGANIC/SUSTAINABLE TREATMENT:")
        for line in str(result.get('organic_treatment', 'N/A')).split('\n'):
            if line.strip():
                print(f"   {line}")
        
        if result.get('medicine') and result['medicine'] != 'N/A':
            print(f"\n💊 RECOMMENDED FUNGICIDE/MEDICINE:")
            print(f"   {result['medicine']}")
        
        if result.get('irrigation_advice') and result['irrigation_advice'] != 'N/A':
            print(f"\n💧 IRRIGATION ADVICE:")
            print(f"   {result['irrigation_advice']}")
    
    # Prevention
    if result.get('prevention') and result['prevention'] != 'N/A':
        print(f"\n🛡️  PREVENTION STRATEGIES:")
        print(f"   {result['prevention']}")
    
    print("\n" + "="*90 + "\n")

# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

def main():
    """Command-line interface for disease prediction"""
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python predict.py <image_path>")
        print("\nExamples:")
        print("  python predict.py test_images/brinjal_healthy.jpg")
        print("  python predict.py test_images/grapes_disease.jpg")
        sys.exit(0)
    
    image_path = sys.argv[1]
    
    if not os.path.exists(image_path):
        print(f"Error: Image file not found: {image_path}")
        sys.exit(1)
    
    try:
        print(f"\nInitializing predictor and processing image: {image_path}")
        predictor = CropDiseasePredictor()
        result = predictor.predict(image_path)
        print_prediction_details(result)
        
        # Return exit code based on success
        sys.exit(0 if result.get('success') else 1)
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        logger.exception("Fatal error during prediction")
        sys.exit(1)


if __name__ == "__main__":
    main()
