"""
QUICK START SCRIPT
Simplified setup and training for improved disease prediction system
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_command(cmd, description):
    """Run command and handle errors"""
    logger.info(f"\n{'='*70}")
    logger.info(f"▶️  {description}")
    logger.info(f"{'='*70}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode != 0:
            logger.error(f"❌ {description} failed!")
            return False
        logger.info(f"✓ {description} completed successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        return False


def main():
    """Main quick start function"""
    
    logger.info("\n" + "="*70)
    logger.info("🚀 DUALCROP DISEASE PREDICTION - QUICK START")
    logger.info("="*70)
    
    # Step 1: Setup
    logger.info("\n📋 STEP 1: VALIDATING DATASET")
    if not run_command("python setup_dataset.py", "Dataset validation"):
        logger.error("❌ Dataset validation failed. Please check your dataset structure.")
        return False
    
    # Step 2: Train
    logger.info("\n🎓 STEP 2: TRAINING MODELS")
    logger.info("\nThis will take 20-30 minutes (CPU) or 5-10 minutes (GPU)")
    logger.info("Models will be saved to: models/")
    
    confirm = input("\nContinue with training? (y/n): ").lower()
    if confirm != 'y':
        logger.info("Training cancelled.")
        return False
    
    if not run_command("python train_improved.py", "Model training"):
        logger.error("❌ Training failed. Check logs above for errors.")
        return False
    
    # Step 3: Verify
    logger.info("\n✅ STEP 3: VERIFICATION")
    
    required_files = [
        "models/grapes_disease_model.h5",
        "models/brinjal_disease_model.h5",
        "models/grapes_classes.json",
        "models/brinjal_classes.json",
        "disease_database.json"
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / (1024*1024)  # MB
            logger.info(f"  ✓ {file:50s} ({size:.1f} MB)")
        else:
            logger.error(f"  ✗ {file:50s} NOT FOUND")
            all_exist = False
    
    if not all_exist:
        logger.error("❌ Some required files are missing!")
        return False
    
    # Step 4: Test
    logger.info("\n🧪 STEP 4: TESTING PREDICTION")
    logger.info("Testing with a sample image...")
    
    # Find a sample image
    sample_image = None
    for root, dirs, files in os.walk("Dataset"):
        for file in files:
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                sample_image = os.path.join(root, file)
                break
        if sample_image:
            break
    
    if sample_image:
        logger.info(f"Using sample: {sample_image}")
        if run_command(f"python predict_improved.py \"{sample_image}\"", "Prediction test"):
            logger.info("✓ Prediction test successful!")
        else:
            logger.warning("⚠️  Prediction test had issues, but models are ready")
    else:
        logger.warning("⚠️  No sample images found in dataset")
    
    # Step 5: Launch
    logger.info("\n" + "="*70)
    logger.info("✅ ALL SETUP COMPLETE!")
    logger.info("="*70)
    logger.info("\n📚 NEXT STEPS:")
    logger.info("1. Start Flask app:  python app.py")
    logger.info("2. Open browser:     http://localhost:5000")
    logger.info("3. Upload images and test predictions!")
    logger.info("\n📖 For detailed guide, see: IMPROVED_IMPLEMENTATION_GUIDE.md")
    logger.info("="*70 + "\n")
    
    # Offer to start Flask
    start_flask = input("Start Flask app now? (y/n): ").lower()
    if start_flask == 'y':
        logger.info("Starting Flask app...")
        run_command("python app.py", "Flask server")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⏸️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)
