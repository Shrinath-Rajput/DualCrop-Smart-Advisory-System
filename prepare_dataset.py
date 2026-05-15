"""
DATA PREPARATION SCRIPT
=======================

This script helps organize and prepare your dataset for training
the crop disease model.

Functions:
1. Organize existing dataset into proper folder structure
2. Copy images into correct class folders
3. Generate statistics about dataset
4. Validate image format and integrity
"""

import os
import shutil
import json
from pathlib import Path
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Expected class structure
EXPECTED_CLASSES = [
    "Brinjal_Healthy",
    "Brinjal_Little_Leaf",
    "Brinjal_Leaf_Spot",
    "Brinjal_Blight",
    "Grapes_Healthy",
    "Grapes_Black_Measles",
    "Grapes_Black_Rot",
    "Grapes_Isariopsis_Leaf_Spot"
]

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
DATASET_DIR = "dataset"
EXISTING_DATASET_DIR = "Dataset"

# ============================================================================
# FUNCTIONS
# ============================================================================

def create_class_folders():
    """Create empty class folders"""
    logger.info("Creating class folders...")
    
    os.makedirs(DATASET_DIR, exist_ok=True)
    
    for class_name in EXPECTED_CLASSES:
        class_dir = os.path.join(DATASET_DIR, class_name)
        os.makedirs(class_dir, exist_ok=True)
        logger.info(f"  ✓ {class_dir}")
    
    logger.info("✓ Class folders created\n")

def count_images(directory):
    """Count images in directory"""
    count = 0
    for item in Path(directory).rglob("*"):
        if item.suffix.lower() in IMAGE_EXTENSIONS:
            count += 1
    return count

def organize_existing_brinjal_data():
    """Organize Brinjal dataset"""
    logger.info("Organizing Brinjal data...")
    
    brinjal_source = os.path.join(EXISTING_DATASET_DIR, "Binjal_Diseases")
    
    if not os.path.exists(brinjal_source):
        logger.warning(f"  Brinjal dataset not found: {brinjal_source}")
        return
    
    # Target folders based on what we find
    target_class = "Brinjal_Little_Leaf"
    target_dir = os.path.join(DATASET_DIR, target_class)
    
    count = 0
    for item in Path(brinjal_source).rglob("*"):
        if item.suffix.lower() in IMAGE_EXTENSIONS:
            try:
                shutil.copy2(str(item), target_dir)
                count += 1
            except Exception as e:
                logger.warning(f"  Could not copy {item.name}: {e}")
    
    logger.info(f"  ✓ Copied {count} images to {target_class}\n")

def organize_existing_grapes_data():
    """Organize Grapes dataset"""
    logger.info("Organizing Grapes data...")
    
    grapes_source = os.path.join(EXISTING_DATASET_DIR, "Grapes_Diseases")
    
    if not os.path.exists(grapes_source):
        logger.warning(f"  Grapes dataset not found: {grapes_source}")
        return
    
    # Mapping of folder names to class names
    disease_mapping = {
        'healthy': 'Grapes_Healthy',
        'black rot': 'Grapes_Black_Rot',
        'black measles': 'Grapes_Black_Measles',
        'esca': 'Grapes_Black_Measles',
        'leaf blight': 'Grapes_Isariopsis_Leaf_Spot',
        'isariopsis': 'Grapes_Isariopsis_Leaf_Spot',
    }
    
    for folder in Path(grapes_source).iterdir():
        if not folder.is_dir():
            continue
        
        folder_name = folder.name.lower()
        target_class = None
        
        # Find matching class
        for keyword, class_name in disease_mapping.items():
            if keyword in folder_name:
                target_class = class_name
                break
        
        if target_class is None:
            logger.warning(f"  Could not map: {folder.name}")
            continue
        
        target_dir = os.path.join(DATASET_DIR, target_class)
        count = 0
        
        for image_file in folder.rglob("*"):
            if image_file.suffix.lower() in IMAGE_EXTENSIONS:
                try:
                    shutil.copy2(str(image_file), target_dir)
                    count += 1
                except Exception as e:
                    logger.warning(f"  Could not copy {image_file.name}: {e}")
        
        logger.info(f"  ✓ {folder.name} → {target_class} ({count} images)")
    
    logger.info()

def generate_dataset_statistics():
    """Generate and print dataset statistics"""
    logger.info("\n" + "="*80)
    logger.info("DATASET STATISTICS")
    logger.info("="*80 + "\n")
    
    stats = {}
    total_images = 0
    
    for class_name in EXPECTED_CLASSES:
        class_dir = os.path.join(DATASET_DIR, class_name)
        
        if not os.path.exists(class_dir):
            count = 0
        else:
            count = count_images(class_dir)
        
        stats[class_name] = count
        total_images += count
    
    # Print statistics
    print(f"{'Class Name':<40} {'Images':<10}")
    print("-" * 50)
    
    for class_name in EXPECTED_CLASSES:
        count = stats[class_name]
        status = "✓" if count > 0 else "⚠"
        print(f"{class_name:<40} {count:<10} {status}")
    
    print("-" * 50)
    print(f"{'TOTAL':<40} {total_images:<10}")
    print()
    
    # Breakdown by crop
    brinjal_total = sum(stats[c] for c in stats if c.startswith("Brinjal"))
    grapes_total = sum(stats[c] for c in stats if c.startswith("Grapes"))
    
    print(f"\nBrinjal images: {brinjal_total}")
    print(f"Grapes images: {grapes_total}")
    print(f"Total images: {total_images}")
    
    # Save statistics
    stats_file = os.path.join(DATASET_DIR, "statistics.json")
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    
    logger.info(f"✓ Statistics saved to: {stats_file}\n")
    
    return stats

def validate_dataset():
    """Validate dataset integrity"""
    logger.info("Validating dataset...\n")
    
    issues = []
    
    for class_name in EXPECTED_CLASSES:
        class_dir = os.path.join(DATASET_DIR, class_name)
        
        if not os.path.exists(class_dir):
            issues.append(f"Missing directory: {class_name}")
            continue
        
        # Check if folder has images
        image_count = count_images(class_dir)
        if image_count == 0:
            issues.append(f"Empty directory: {class_name}")
    
    if issues:
        logger.warning("⚠ Dataset Issues Found:")
        for issue in issues:
            logger.warning(f"  - {issue}")
        logger.warning()
    else:
        logger.info("✓ Dataset validation passed\n")
    
    return len(issues) == 0

def prepare_dataset():
    """Complete dataset preparation"""
    logger.info("="*80)
    logger.info("CROP DISEASE DATASET PREPARATION")
    logger.info("="*80 + "\n")
    
    try:
        # Step 1: Create folders
        create_class_folders()
        
        # Step 2: Organize existing data
        organize_existing_brinjal_data()
        organize_existing_grapes_data()
        
        # Step 3: Generate statistics
        stats = generate_dataset_statistics()
        
        # Step 4: Validate
        is_valid = validate_dataset()
        
        logger.info("="*80)
        if is_valid:
            logger.info("✓ Dataset is ready for training!")
            logger.info("\nNext step: python train_complete.py")
        else:
            logger.info("⚠ Dataset has issues. Please add more images.")
            logger.info("\nAdd images to the following folders:")
            for class_name in EXPECTED_CLASSES:
                path = os.path.join(DATASET_DIR, class_name)
                count = count_images(path)
                if count == 0:
                    logger.info(f"  - {class_name}/")
        logger.info("="*80 + "\n")
        
        return is_valid
    
    except Exception as e:
        logger.error(f"Error during dataset preparation: {e}")
        raise

# ============================================================================
# MANUAL DATASET SETUP INSTRUCTIONS
# ============================================================================

def print_manual_setup_instructions():
    """Print instructions for manual dataset setup"""
    print("\n" + "="*80)
    print("MANUAL DATASET SETUP INSTRUCTIONS")
    print("="*80 + "\n")
    
    print("If you want to manually organize your dataset, create the following")
    print("folder structure and add images:\n")
    
    print("dataset/")
    for class_name in EXPECTED_CLASSES:
        print(f"├── {class_name}/")
        print(f"│   ├── image1.jpg")
        print(f"│   ├── image2.jpg")
        print(f"│   └── ...more images...")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS:")
    print("="*80)
    print("""
1. MINIMUM IMAGES PER CLASS: 50 images
   - Recommended: 100-200 images per class
   - For best results: 200+ images per class

2. IMAGE REQUIREMENTS:
   - Format: JPG, PNG, BMP, GIF
   - Size: Any size (will be resized to 224x224)
   - Quality: Clear, well-lit images

3. CLASS DISTRIBUTION:
   - Keep similar number of images across classes
   - Avoid extreme imbalance (e.g., 1000 images vs 10 images)

4. IMAGE VARIETY:
   - Include images from different angles
   - Include images under different lighting
   - Include images of different plant sizes

5. HEALTHY vs DISEASED:
   - Healthy images: Clear, vibrant, no spots or discoloration
   - Diseased images: Various disease stages

After organizing dataset, run:
  python prepare_dataset.py
  python train_complete.py
""")
    print("="*80 + "\n")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--manual":
        print_manual_setup_instructions()
    else:
        is_ready = prepare_dataset()
        
        if is_ready:
            logger.info("You can now train the model:")
            logger.info("  python train_complete.py")
        else:
            logger.info("\nTo manually organize your dataset:")
            logger.info("  python prepare_dataset.py --manual")
