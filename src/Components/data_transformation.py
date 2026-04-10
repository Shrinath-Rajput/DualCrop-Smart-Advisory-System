import os
import sys
from dataclasses import dataclass

from tensorflow.keras.preprocessing.image import ImageDataGenerator

from src.exception import CustomException
from src.logger import logging


@dataclass
class DataTransformationConfig:
    train_dir: str = os.path.join("artifacts", "train")
    test_dir: str = os.path.join("artifacts", "test")
    target_size: tuple = (224, 224)
    batch_size: int = 32


class DataTransformation:
    def __init__(self, train_dir=None, test_dir=None):
        self.config = DataTransformationConfig()
        
        # Use provided paths or default config paths
        if train_dir:
            self.config.train_dir = train_dir
        if test_dir:
            self.config.test_dir = test_dir

    def validate_data_directories(self):
        """Validate that train and test directories exist and contain data"""
        try:
            if not os.path.exists(self.config.train_dir):
                raise Exception(f"Train directory not found: {self.config.train_dir}")
            
            if not os.path.exists(self.config.test_dir):
                raise Exception(f"Test directory not found: {self.config.test_dir}")
            
            # Check if directories have subdirectories (class folders)
            train_classes = [d for d in os.listdir(self.config.train_dir) 
                            if os.path.isdir(os.path.join(self.config.train_dir, d))]
            
            if not train_classes:
                raise Exception(f"No class folders found in train directory: {self.config.train_dir}")
            
            logging.info(f"Found {len(train_classes)} classes in training data: {train_classes}")
            return True
            
        except Exception as e:
            raise CustomException(e, sys)

    def get_data_transformation(self):
        try:
            logging.info("Creating ImageDataGenerator with augmentation")

            train_datagen = ImageDataGenerator(
                rescale=1./255,
                rotation_range=20,
                width_shift_range=0.2,
                height_shift_range=0.2,
                shear_range=0.2,
                zoom_range=0.2,
                horizontal_flip=True,
                fill_mode='nearest'
            )

            test_datagen = ImageDataGenerator(
                rescale=1./255
            )

            logging.info("✅ ImageDataGenerator created successfully")
            return train_datagen, test_datagen

        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_transformation(self):
        try:
            logging.info("Starting data transformation process")
            
            # Validate directories first
            self.validate_data_directories()
            
            train_datagen, test_datagen = self.get_data_transformation()

            logging.info(f"Loading training data from: {self.config.train_dir}")
            train_data = train_datagen.flow_from_directory(
                self.config.train_dir,
                target_size=self.config.target_size,
                batch_size=self.config.batch_size,
                class_mode='categorical',
                shuffle=True
            )

            logging.info(f"Loading testing data from: {self.config.test_dir}")
            test_data = test_datagen.flow_from_directory(
                self.config.test_dir,
                target_size=self.config.target_size,
                batch_size=self.config.batch_size,
                class_mode='categorical',
                shuffle=False
            )

            logging.info("✅ Data transformation completed successfully")
            return train_data, test_data

        except Exception as e:
            raise CustomException(e, sys)


if __name__ == "__main__":
    try:
        from src.Components.data_ingestion import DataIngestion

        logging.info("=" * 50)
        logging.info("Starting Data Pipeline")
        logging.info("=" * 50)

        # Step 1: Data Ingestion
        logging.info("\n📊 STEP 1: Data Ingestion")
        ingestion = DataIngestion()
        train_path, test_path = ingestion.initiate_data_ingestion()
        logging.info(f"✅ Data Ingestion Complete")
        logging.info(f"   Train path: {train_path}")
        logging.info(f"   Test path: {test_path}")

        # Step 2: Data Transformation
        logging.info("\n🔄 STEP 2: Data Transformation")
        transformation = DataTransformation(train_dir=train_path, test_dir=test_path)
        train_data, test_data = transformation.initiate_data_transformation()
        
        logging.info(f"✅ Data Transformation Complete")
        logging.info(f"   Number of classes: {len(train_data.class_indices)}")
        logging.info(f"   Classes: {list(train_data.class_indices.keys())}")
        logging.info(f"   Train batches: {len(train_data)}")
        logging.info(f"   Test batches: {len(test_data)}")

        logging.info("\n" + "=" * 50)
        logging.info("✅ Data Pipeline Completed Successfully!")
        logging.info("=" * 50)

    except Exception as e:
        logging.error(f"❌ Error in data pipeline: {str(e)}")
        raise