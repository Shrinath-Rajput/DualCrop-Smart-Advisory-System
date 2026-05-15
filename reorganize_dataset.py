"""
Dataset Reorganization Script
Converts existing scattered dataset structure to unified 8-class format
"""

import os
import shutil
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# New unified structure
NEW_STRUCTURE = {
    'Brinjal_Healthy': [],
    'Brinjal_Little_Leaf': ['Dataset/Binjal_Diseases/leaf disease detection/colour/brinjal_little_leaf'],
    'Brinjal_Leaf_Spot': [],
    'Brinjal_Blight': [],
    'Grapes_Healthy': [],
    'Grapes_Black_Measles': ['Dataset/Grapes_Diseases/Data/train/Black Measles'],
    'Grapes_Black_Rot': ['Dataset/Grapes_Diseases/Data/train/Black Rot'],
    'Grapes_Isariopsis_Leaf_Spot': ['Dataset/Grapes_Diseases/Data/train/Isariopsis Leaf Spot'],
}

def reorganize_dataset():
    """Reorganize dataset into unified structure"""
    
    logger.info("="*80)
    logger.info("DATASET REORGANIZATION - Converting to Unified 8-Class Structure")
    logger.info("="*80 + "\n")
    
    # Create base Dataset directory
    os.makedirs('Dataset', exist_ok=True)
    
    # Create all class folders
    for class_name in NEW_STRUCTURE.keys():
        class_path = os.path.join('Dataset', class_name)
        os.makedirs(class_path, exist_ok=True)
        logger.info(f"✓ Created: Dataset/{class_name}/")
    
    logger.info("\n" + "="*80)
    logger.info("COPYING EXISTING IMAGES")
    logger.info("="*80 + "\n")
    
    # Copy images from old locations
    for new_class, old_paths in NEW_STRUCTURE.items():
        new_class_path = os.path.join('Dataset', new_class)
        
        if not old_paths:
            logger.warning(f"⚠ {new_class}: No source data found - folder is empty")
            logger.warning(f"   → Add images to Dataset/{new_class}/\n")
            continue
        
        total_copied = 0
        for old_path in old_paths:
            if not os.path.exists(old_path):
                logger.warning(f"⚠ Source path not found: {old_path}")
                continue
            
            # Get all image files
            image_files = []
            for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
                image_files.extend(Path(old_path).rglob(f'*{ext}'))
                image_files.extend(Path(old_path).rglob(f'*{ext.upper()}'))
            
            # Copy images
            for img_file in image_files:
                try:
                    dest = os.path.join(new_class_path, img_file.name)
                    shutil.copy2(img_file, dest)
                    total_copied += 1
                except Exception as e:
                    logger.error(f"  Error copying {img_file.name}: {e}")
        
        if total_copied > 0:
            logger.info(f"✓ {new_class}: {total_copied} images copied")
        else:
            logger.warning(f"⚠ {new_class}: No images found in source")
    
    logger.info("\n" + "="*80)
    logger.info("VERIFICATION")
    logger.info("="*80 + "\n")
    
    # Verify structure
    total_images = 0
    for class_name in sorted(NEW_STRUCTURE.keys()):
        class_path = os.path.join('Dataset', class_name)
        
        image_files = []
        for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.gif']:
            image_files.extend(Path(class_path).rglob(f'*{ext}'))
            image_files.extend(Path(class_path).rglob(f'*{ext.upper()}'))
        
        count = len(image_files)
        total_images += count
        status = "✓" if count > 0 else "⚠"
        logger.info(f"{status} Dataset/{class_name:40s} → {count:4d} images")
    
    logger.info("\n" + "="*80)
    logger.info(f"TOTAL IMAGES: {total_images}")
    logger.info("="*80 + "\n")
    
    # Summary and next steps
    logger.info("NEXT STEPS:")
    logger.info("-" * 80)
    
    missing = [c for c in NEW_STRUCTURE if len(os.listdir(f'Dataset/{c}')) == 0]
    if missing:
        logger.info(f"\n1. Add images for {len(missing)} missing classes:")
        for class_name in missing:
            logger.info(f"   - Dataset/{class_name}/ (needs 50-100+ images)")
    
    logger.info("\n2. Once dataset is complete, run training:")
    logger.info("   python train_unified.py")
    logger.info("\n3. Then test predictions:")
    logger.info("   python predict.py path/to/test_image.jpg")
    
    logger.info("\n" + "="*80)
    logger.info("✓ REORGANIZATION COMPLETE")
    logger.info("="*80 + "\n")
    
    return total_images > 0


if __name__ == '__main__':
    success = reorganize_dataset()
    exit(0 if success else 1)
