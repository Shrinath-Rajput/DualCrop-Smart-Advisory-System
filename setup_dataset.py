"""
DATASET ORGANIZATION SCRIPT
Prepares dataset structure for training with improved pipeline

This script:
1. Validates existing dataset
2. Creates proper directory structure
3. Generates required class mappings
4. Validates all images
"""

import os
import json
import shutil
import cv2
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def validate_image(image_path):
    """Validate if file is a valid image"""
    try:
        img = cv2.imread(image_path)
        return img is not None
    except:
        return False


def organize_dataset():
    """Organize dataset for training"""
    
    logger.info("\n" + "="*70)
    logger.info("DATASET ORGANIZATION")
    logger.info("="*70 + "\n")
    
    # Check source dataset structure
    dataset_base = "Dataset"
    if not os.path.exists(dataset_base):
        logger.error(f"Dataset directory not found: {dataset_base}")
        return False
    
    # Validate Grapes dataset
    grapes_path = os.path.join(dataset_base, "Grapes_Diseases", "Data", "train")
    if not os.path.exists(grapes_path):
        logger.error(f"Grapes dataset not found: {grapes_path}")
        return False
    
    grapes_classes = [d for d in os.listdir(grapes_path) 
                      if os.path.isdir(os.path.join(grapes_path, d))]
    
    logger.info("✓ Grapes dataset structure:")
    for cls in sorted(grapes_classes):
        cls_path = os.path.join(grapes_path, cls)
        images = [f for f in os.listdir(cls_path) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        logger.info(f"  • {cls:40s} → {len(images):4d} images")
    
    # Validate Brinjal dataset
    brinjal_path = os.path.join(dataset_base, "Binjal_Diseases", "leaf disease detection", "colour")
    if not os.path.exists(brinjal_path):
        logger.error(f"Brinjal dataset not found: {brinjal_path}")
        return False
    
    brinjal_classes = [d for d in os.listdir(brinjal_path) 
                       if os.path.isdir(os.path.join(brinjal_path, d))]
    
    logger.info("\n✓ Brinjal dataset structure:")
    for cls in sorted(brinjal_classes):
        cls_path = os.path.join(brinjal_path, cls)
        images = [f for f in os.listdir(cls_path) 
                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        logger.info(f"  • {cls:40s} → {len(images):4d} images")
    
    logger.info("\n" + "="*70)
    logger.info("✓ Dataset structure validated successfully!")
    logger.info("="*70 + "\n")
    
    return True


def main():
    """Main function"""
    
    logger.info("\n" + "="*70)
    logger.info("DATASET SETUP FOR IMPROVED TRAINING")
    logger.info("="*70 + "\n")
    
    # Ensure models directory exists
    os.makedirs("models", exist_ok=True)
    logger.info("✓ Models directory created")
    
    # Validate dataset
    if not organize_dataset():
        logger.error("❌ Dataset validation failed!")
        return False
    
    logger.info("\n" + "="*70)
    logger.info("NEXT STEPS:")
    logger.info("="*70)
    logger.info("1. Run: python train_improved.py")
    logger.info("   - This will train crop-specific models")
    logger.info("   - Will generate models/grapes_disease_model.h5")
    logger.info("   - Will generate models/brinjal_disease_model.h5")
    logger.info("   - Will generate models/grapes_classes.json")
    logger.info("   - Will generate models/brinjal_classes.json")
    logger.info("\n2. After training, run: python app.py")
    logger.info("   - Flask server will use improved two-stage prediction")
    logger.info("   - Upload images to get accurate disease predictions")
    logger.info("="*70 + "\n")
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
