import os
import sys
import shutil
import random
from dataclasses import dataclass

from src.exception import CustomException
from src.logger import logging


@dataclass
class DataIngestionConfig:
    train_path: str = os.path.join("artifacts", "train")
    test_path: str = os.path.join("artifacts", "test")


class DataIngestion:
    def __init__(self):
        self.config = DataIngestionConfig()

    def split_data(self, source_dir, train_dir, test_dir, split_ratio=0.8):
        """
        Split images from source directory into train and test directories
        """
        try:
            os.makedirs(train_dir, exist_ok=True)
            os.makedirs(test_dir, exist_ok=True)

            # Get list of image files (filter out non-image files)
            images = [f for f in os.listdir(source_dir) 
                     if os.path.isfile(os.path.join(source_dir, f)) 
                     and f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
            
            if not images:
                logging.warning(f"No images found in {source_dir}")
                return
            
            random.shuffle(images)
            split_index = int(len(images) * split_ratio)

            train_files = images[:split_index]
            test_files = images[split_index:]

            for file in train_files:
                src_path = os.path.join(source_dir, file)
                dst_path = os.path.join(train_dir, file)
                shutil.copy2(src_path, dst_path)

            for file in test_files:
                src_path = os.path.join(source_dir, file)
                dst_path = os.path.join(test_dir, file)
                shutil.copy2(src_path, dst_path)

            logging.info(f"Split {len(train_files)} train and {len(test_files)} test images from {source_dir}")

        except Exception as e:
            raise CustomException(e, sys)

    def initiate_data_ingestion(self):
        logging.info("Starting data ingestion for crop disease dataset")

        try:
            dataset_root = "Dataset"  # Updated to match your folder structure
            
            if not os.path.exists(dataset_root):
                raise Exception(f"Dataset folder not found at {dataset_root}")

            # Iterate through crop types (brinjal, Grapes, etc.)
            for crop_name in os.listdir(dataset_root):
                crop_path = os.path.join(dataset_root, crop_name)
                
                # Skip if not a directory
                if not os.path.isdir(crop_path):
                    continue
                
                logging.info(f"Processing crop: {crop_name}")

                # Iterate through disease classes within each crop
                for disease_class in os.listdir(crop_path):
                    disease_path = os.path.join(crop_path, disease_class)
                    
                    # Skip if not a directory
                    if not os.path.isdir(disease_path):
                        continue
                    
                    # Create unique class folder name combining crop and disease
                    class_folder_name = f"{crop_name}_{disease_class}"
                    
                    train_class_path = os.path.join(self.config.train_path, class_folder_name)
                    test_class_path = os.path.join(self.config.test_path, class_folder_name)

                    logging.info(f"  Processing disease class: {disease_class}")
                    self.split_data(disease_path, train_class_path, test_class_path)

            logging.info("Data ingestion completed successfully")

            return self.config.train_path, self.config.test_path

        except Exception as e:
            raise CustomException(e, sys)


if __name__ == "__main__":
    obj = DataIngestion()
    train_path, test_path = obj.initiate_data_ingestion()
    print("Train Path:", train_path)
    print("Test Path:", test_path)