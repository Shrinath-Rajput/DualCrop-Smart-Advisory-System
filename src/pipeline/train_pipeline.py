"""
Main Training Pipeline
Orchestrates the complete ML workflow: Data Ingestion → Data Transformation → Model Training
"""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.Components.data_ingestion import DataIngestion
from src.Components.data_transformation import DataTransformation
from src.Components.model_trainer import ModelTrainer

from src.exception import CustomException
from src.logger import logging


class TrainPipeline:
    """
    Complete training pipeline that orchestrates:
    1. Data Ingestion: Split raw dataset into train/test
    2. Data Transformation: Apply preprocessing and augmentation
    3. Model Training: Train transfer learning model
    """

    def __init__(self):
        """Initialize pipeline components"""
        self.data_ingestion = DataIngestion()
        self.data_transformation = None
        self.model_trainer = ModelTrainer()
        
        self.train_path = None
        self.test_path = None
        self.train_data = None
        self.test_data = None
        self.model = None

    def run_step_1_data_ingestion(self):
        """
        STEP 1: Data Ingestion
        Splits raw images from Dataset/ into train/test folders in artifacts/
        """
        try:
            logging.info("\n" + "=" * 70)
            logging.info("📊 STEP 1: DATA INGESTION")
            logging.info("=" * 70)
            logging.info("Purpose: Split raw dataset into training and testing sets")
            logging.info("Source: Dataset/ folder")
            logging.info("Output: artifacts/train/ and artifacts/test/")

            self.train_path, self.test_path = self.data_ingestion.initiate_data_ingestion()

            logging.info("\n✅ DATA INGESTION COMPLETED")
            logging.info(f"   📁 Train data path: {self.train_path}")
            logging.info(f"   📁 Test data path: {self.test_path}")
            logging.info("=" * 70)

            return True

        except Exception as e:
            logging.error(f"❌ Data Ingestion failed: {str(e)}")
            raise CustomException(e, sys)

    def run_step_2_data_transformation(self):
        """
        STEP 2: Data Transformation
        Applies preprocessing, augmentation, and creates data generators
        """
        try:
            logging.info("\n" + "=" * 70)
            logging.info("🔄 STEP 2: DATA TRANSFORMATION")
            logging.info("=" * 70)
            logging.info("Purpose: Preprocess images and apply augmentation")
            logging.info("Operations: Resize to 224x224, normalize, augment")

            # Initialize transformation with ingested data paths
            self.data_transformation = DataTransformation(
                train_dir=self.train_path,
                test_dir=self.test_path
            )

            # Transform data and get data generators
            self.train_data, self.test_data = self.data_transformation.initiate_data_transformation()

            # Log class information
            num_classes = len(self.train_data.class_indices)
            classes = list(self.train_data.class_indices.keys())
            
            logging.info("\n✅ DATA TRANSFORMATION COMPLETED")
            logging.info(f"   📊 Number of classes: {num_classes}")
            logging.info(f"   🏷️  Classes: {classes}")
            logging.info(f"   📈 Train batches: {len(self.train_data)}")
            logging.info(f"   📈 Test batches: {len(self.test_data)}")
            logging.info(f"   🖼️  Image size: 224x224")
            logging.info(f"   📦 Batch size: 32")
            logging.info("=" * 70)

            return True

        except Exception as e:
            logging.error(f"❌ Data Transformation failed: {str(e)}")
            raise CustomException(e, sys)

    def run_step_3_model_training(self):
        """
        STEP 3: Model Training
        Builds and trains EfficientNetB0 transfer learning model for disease classification
        """
        try:
            logging.info("\n" + "=" * 70)
            logging.info("🤖 STEP 3: MODEL TRAINING")
            logging.info("=" * 70)
            logging.info("Purpose: Train EfficientNetB0 model for disease classification")
            logging.info("Model: EfficientNetB0 with custom top layers")
            logging.info("Optimizer: Adam (lr=0.001)")
            logging.info("Loss: Categorical Crossentropy")
            logging.info("Epochs: 20")

            # Train model
            self.model = self.model_trainer.initiate_model_trainer(
                self.train_data,
                self.test_data
            )

            logging.info("\n✅ MODEL TRAINING COMPLETED")
            logging.info(f"   💾 Model saved: artifacts/crop_disease_model.h5")
            logging.info(f"   📛 Classes saved: artifacts/class_names.json")
            logging.info(f"   📊 History saved: artifacts/history.json")
            logging.info("=" * 70)

            return True

        except Exception as e:
            logging.error(f"❌ Model Training failed: {str(e)}")
            raise CustomException(e, sys)

    def run(self):
        """
        Execute complete training pipeline
        Orchestrates all 3 steps: Ingestion → Transformation → Training
        """
        try:
            logging.info("\n\n")
            logging.info("╔" + "=" * 68 + "╗")
            logging.info("║" + " " * 15 + "🌾 DUALCROP SMART ADVISORY SYSTEM 🌾" + " " * 15 + "║")
            logging.info("║" + " " * 20 + "COMPLETE TRAINING PIPELINE" + " " * 22 + "║")
            logging.info("╚" + "=" * 68 + "╝")

            # Step 1: Data Ingestion
            self.run_step_1_data_ingestion()

            # Step 2: Data Transformation
            self.run_step_2_data_transformation()

            # Step 3: Model Training
            self.run_step_3_model_training()

            # Final summary
            logging.info("\n\n")
            logging.info("╔" + "=" * 68 + "╗")
            logging.info("║" + " " * 18 + "✅ PIPELINE EXECUTION SUCCESSFUL ✅" + " " * 14 + "║")
            logging.info("╚" + "=" * 68 + "╝")
            
            logging.info("\n📋 PIPELINE SUMMARY:")
            logging.info("   ✅ Step 1: Data Ingestion - COMPLETED")
            logging.info("   ✅ Step 2: Data Transformation - COMPLETED")
            logging.info("   ✅ Step 3: Model Training - COMPLETED")
            logging.info("\n📂 Generated Artifacts:")
            logging.info("   • artifacts/train/ - Training dataset")
            logging.info("   • artifacts/test/ - Testing dataset")
            logging.info("   • artifacts/crop_disease_model.h5 - Trained EfficientNetB0 model")
            logging.info("   • artifacts/class_names.json - Disease class names mapping")
            logging.info("   • artifacts/history.json - Training history")
            logging.info("\n🎯 Next Steps:")
            logging.info("   1. Run predictions: python src/pipeline/predict_pipeline.py")
            logging.info("   2. Start web app: python app.py")
            logging.info("   3. Test predictions: python test_predict_pipeline.py")
            logging.info("\n" + "=" * 70 + "\n")

            return True

        except Exception as e:
            logging.error(f"\n❌ PIPELINE FAILED: {str(e)}")
            logging.error("Check logs for detailed error information")
            raise CustomException(e, sys)


def main():
    """Main entry point"""
    try:
        pipeline = TrainPipeline()
        pipeline.run()
        
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()