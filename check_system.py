#!/usr/bin/env python3
"""
GETTING STARTED CHECKLIST & STATUS VERIFICATION
Verify system setup and readiness for training and deployment
"""

import os
import json
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def print_header(text):
    """Print formatted header"""
    logger.info("\n" + "="*70)
    logger.info(f"  {text}")
    logger.info("="*70)


def check_file_exists(path, description):
    """Check if file exists"""
    exists = os.path.exists(path)
    status = "✅" if exists else "❌"
    logger.info(f"  {status} {description:50s} {path if not exists else ''}")
    return exists


def check_directory_exists(path, description):
    """Check if directory exists"""
    exists = os.path.isdir(path)
    status = "✅" if exists else "⚠️ " if path in ["models", "logs"] else "❌"
    logger.info(f"  {status} {description:50s} {path if not exists else ''}")
    return exists


def check_files_in_directory(path, extensions, description):
    """Check files in directory"""
    if not os.path.exists(path):
        logger.info(f"  ❌ {description:50s} (dir not found)")
        return 0
    
    files = [f for f in os.listdir(path) if f.lower().endswith(extensions)]
    count = len(files)
    status = "✅" if count > 0 else "❌"
    logger.info(f"  {status} {description:50s} ({count} files)")
    return count


def main():
    """Main verification function"""
    
    print_header("🚀 DUALCROP DISEASE PREDICTION - SYSTEM CHECKLIST")
    
    logger.info("\n1️⃣  CORE PROJECT FILES")
    print_header("Required Python Files")
    
    required_files = [
        ("train_improved.py", "Training pipeline"),
        ("predict_improved.py", "Prediction module"),
        ("app.py", "Flask application"),
        ("setup_dataset.py", "Dataset validator"),
        ("quick_start.py", "Quick start script"),
        ("disease_database.json", "Disease information"),
    ]
    
    core_ok = True
    for file, desc in required_files:
        if not check_file_exists(file, desc):
            core_ok = False
    
    if core_ok:
        logger.info("  ✅ All core files present!")
    else:
        logger.info("  ⚠️  Some files missing - regenerate if needed")
    
    print_header("Documentation Files")
    
    docs = [
        ("COMPLETE_FIX_SUMMARY.md", "Fix summary"),
        ("IMPROVED_IMPLEMENTATION_GUIDE.md", "Implementation guide"),
        ("DISEASE_PREDICTION_IMPROVEMENTS.md", "Improvements doc"),
        ("QUICK_REFERENCE.txt", "Quick reference"),
    ]
    
    for file, desc in docs:
        check_file_exists(file, desc)
    
    logger.info("\n2️⃣  DATASET STRUCTURE")
    print_header("Dataset Directories")
    
    datasets_ok = True
    dataset_paths = [
        ("Dataset/Grapes_Diseases/Data/train", "Grapes training data"),
        ("Dataset/Binjal_Diseases/leaf disease detection/colour", "Brinjal training data"),
    ]
    
    for path, desc in dataset_paths:
        if not check_directory_exists(path, desc):
            datasets_ok = False
    
    if datasets_ok:
        logger.info("\n  Checking dataset contents...")
        grapes_count = check_files_in_directory(
            "Dataset/Grapes_Diseases/Data/train",
            ('.jpg', '.jpeg', '.png'),
            "Grapes images"
        )
        brinjal_count = check_files_in_directory(
            "Dataset/Binjal_Diseases/leaf disease detection/colour",
            ('.jpg', '.jpeg', '.png'),
            "Brinjal images"
        )
        
        if grapes_count > 0 and brinjal_count > 0:
            logger.info(f"  ✅ Dataset complete! ({grapes_count + brinjal_count} total images)")
    
    logger.info("\n3️⃣  DEPENDENCIES")
    print_header("Required Python Packages")
    
    packages = [
        "tensorflow",
        "keras",
        "numpy",
        "cv2",
        "flask",
        "PIL",
    ]
    
    all_ok = True
    for package in packages:
        try:
            if package == "cv2":
                import cv2
                logger.info(f"  ✅ {package:30s} (installed)")
            elif package == "PIL":
                from PIL import Image
                logger.info(f"  ✅ {package:30s} (installed)")
            else:
                __import__(package)
                logger.info(f"  ✅ {package:30s} (installed)")
        except ImportError:
            logger.info(f"  ❌ {package:30s} (NOT installed)")
            all_ok = False
    
    if not all_ok:
        logger.info("\n  Install missing packages:")
        logger.info("  pip install -r requirements_improved.txt")
    
    logger.info("\n4️⃣  DIRECTORIES")
    print_header("Required Directories")
    
    dirs_to_check = [
        ("models", "Model storage (created after training)"),
        ("uploads", "Upload folder for images"),
        ("logs", "Logging directory"),
        ("templates", "Flask templates"),
    ]
    
    for dir_path, desc in dirs_to_check:
        exists = check_directory_exists(dir_path, desc)
        if not exists and dir_path in ["models", "uploads", "logs", "templates"]:
            logger.info(f"    Creating {dir_path}/...")
            os.makedirs(dir_path, exist_ok=True)
    
    logger.info("\n5️⃣  TRAINED MODELS")
    print_header("Model Files Status")
    
    models = [
        ("models/grapes_disease_model.h5", "Grapes model (50MB)"),
        ("models/brinjal_disease_model.h5", "Brinjal model (50MB)"),
        ("models/grapes_classes.json", "Grapes classes mapping"),
        ("models/brinjal_classes.json", "Brinjal classes mapping"),
    ]
    
    models_ready = True
    for model_file, desc in models:
        exists = check_file_exists(model_file, desc)
        if not exists:
            models_ready = False
    
    if not models_ready:
        logger.info("\n  📝 Models not trained yet!")
        logger.info("  Next step: python train_improved.py")
    
    logger.info("\n6️⃣  DISEASE DATABASE")
    print_header("Disease Information")
    
    if check_file_exists("disease_database.json", "Disease database"):
        try:
            with open("disease_database.json", 'r') as f:
                db = json.load(f)
                count = len(db.get('diseases', {}))
                logger.info(f"  ✅ Database loaded ({count} diseases)")
        except:
            logger.info("  ⚠️  Error loading database")
    
    logger.info("\n7️⃣  CONFIGURATION")
    print_header("System Configuration")
    
    config_items = [
        ("Python 3.8+", sys.version.split()[0]),
        ("Platform", sys.platform),
        ("Current Directory", os.getcwd()),
    ]
    
    for name, value in config_items:
        logger.info(f"  • {name:30s} : {value}")
    
    logger.info("\n8️⃣  QUICK START GUIDE")
    print_header("Next Steps")
    
    if not models_ready:
        logger.info("\n  🎓 STEP 1: Train Models (25-30 min CPU, 5-10 min GPU)")
        logger.info("  $ python train_improved.py")
        logger.info("\n  Alternative: Automated setup")
        logger.info("  $ python quick_start.py")
    else:
        logger.info("\n  ✅ Models already trained!")
    
    logger.info("\n  🚀 STEP 2: Run Application")
    logger.info("  $ python app.py")
    logger.info("  Then visit: http://localhost:5000")
    
    logger.info("\n  🧪 STEP 3: Test Prediction")
    logger.info("  $ python predict_improved.py Dataset/...image.jpg")
    
    print_header("FINAL STATUS")
    
    # Calculate overall status
    status_checks = {
        "Core Files": core_ok,
        "Dataset": datasets_ok and grapes_count > 0 and brinjal_count > 0,
        "Dependencies": all_ok,
        "Models": models_ready,
    }
    
    for check, status in status_checks.items():
        symbol = "✅" if status else "⚠️ "
        logger.info(f"  {symbol} {check:30s} : {'READY' if status else 'NEEDS ATTENTION'}")
    
    # Final verdict
    if status_checks["Core Files"] and status_checks["Dataset"] and status_checks["Dependencies"]:
        if status_checks["Models"]:
            logger.info("\n  🎉 SYSTEM READY FOR PRODUCTION!")
            logger.info("     Run: python app.py")
        else:
            logger.info("\n  📝 SYSTEM READY FOR TRAINING!")
            logger.info("     Run: python train_improved.py")
    else:
        logger.info("\n  ⚠️  SYSTEM NEEDS SETUP")
        logger.info("     See errors above")
    
    logger.info("\n📚 For detailed instructions, see:")
    logger.info("   - COMPLETE_FIX_SUMMARY.md")
    logger.info("   - IMPROVED_IMPLEMENTATION_GUIDE.md")
    logger.info("   - QUICK_REFERENCE.txt")
    logger.info("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
