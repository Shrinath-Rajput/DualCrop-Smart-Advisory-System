import os
import sys
import shutil
import random
import json
import time
from dataclasses import dataclass

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.exception import CustomException
from src.logger import logging


@dataclass
class DataIngestionConfig:
    train_path: str = os.path.join("artifacts", "train")
    test_path: str = os.path.join("artifacts", "test")
    class_names_path: str = os.path.join("artifacts", "class_names.json")


class DataIngestion:
    def __init__(self):
        self.config = DataIngestionConfig()
        self.class_names = {}  # Track crop_disease class combinations

    def safe_remove_tree(self, path, retries=3, delay=0.5):
        """
        Safely remove a directory tree with retry logic for Windows file locking issues
        """
        if not os.path.exists(path):
            return True
        
        for attempt in range(retries):
            try:
                def handle_remove_error(func, path, exc):
                    """Handle permission errors by retrying after a delay"""
                    import stat
                    if not os.access(path, os.W_OK):
                        os.chmod(path, stat.S_IWUSR | stat.S_IRUSR)
                        func(path)
                    else:
                        raise
                
                shutil.rmtree(path, onerror=handle_remove_error)
                logging.info(f"Successfully removed directory: {path}")
                return True
            except Exception as e:
                if attempt < retries - 1:
                    logging.warning(f"Attempt {attempt + 1} failed to remove {path}, retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    logging.error(f"Failed to remove {path} after {retries} attempts: {str(e)}")
                    # Try Windows-specific force delete as last resort
                    try:
                        if sys.platform == 'win32':
                            os.system(f'rmdir /s /q "{path}" >nul 2>&1')
                            if not os.path.exists(path):
                                logging.info(f"Force removed directory using Windows command: {path}")
                                return True
                    except Exception:
                        pass
                    raise

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
                return 0, 0
            
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

            logging.info(f"   Split {len(train_files)} train and {len(test_files)} test images")
            return len(train_files), len(test_files)

        except Exception as e:
            raise CustomException(e, sys)

    def _process_nested_dataset(self, crop_name, crop_path):
        """
        Process nested disease folders (like Binjal_Diseases structure)
        Recursively finds all disease folders and their images
        Returns: (total_train, total_test)
        """
        total_train = 0
        total_test = 0
        
        def find_disease_folders(path, depth=0):
            nonlocal total_train, total_test
            
            if depth > 5:  # Prevent infinite recursion
                return
            
            for item in sorted(os.listdir(path)):
                item_path = os.path.join(path, item)
                
                if not os.path.isdir(item_path):
                    continue
                
                # Check if this folder contains images
                images = [f for f in os.listdir(item_path) 
                         if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
                
                if images:
                    # Found a disease folder with images
                    disease_name = item
                    class_folder_name = f"{crop_name}_{disease_name}"
                    
                    train_class_path = os.path.join(self.config.train_path, class_folder_name)
                    test_class_path = os.path.join(self.config.test_path, class_folder_name)
                    
                    logging.info(f"   🦠 Found disease: {disease_name} ({len(images)} images)")
                    train_count, test_count = self.split_data(item_path, train_class_path, test_class_path)
                    
                    total_train += train_count
                    total_test += test_count
                    
                    self.class_names[class_folder_name] = {
                        "crop": crop_name,
                        "disease": disease_name
                    }
                else:
                    # No images here, keep searching deeper
                    find_disease_folders(item_path, depth + 1)
        
        find_disease_folders(crop_path)
        return total_train, total_test

    def _process_presplit_dataset(self, crop_name, crop_path):
        """
        Process pre-split dataset (like Grapes_Diseases with test/train folders)
        Returns: (total_train, total_test)
        """
        total_train = 0
        total_test = 0
        
        for split_type in ['train', 'test']:
            split_path = os.path.join(crop_path, split_type)
            
            if not os.path.exists(split_path):
                continue
            
            logging.info(f"   Processing {split_type} set...")
            
            # Each disease is a subdirectory in train/test
            for disease_name in sorted(os.listdir(split_path)):
                disease_path = os.path.join(split_path, disease_name)
                
                if not os.path.isdir(disease_path):
                    continue
                
                # Count images
                images = [f for f in os.listdir(disease_path)
                         if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
                
                if not images:
                    continue
                
                class_folder_name = f"{crop_name}_{disease_name}"
                
                # For pre-split data, copy to artifacts while maintaining split
                if split_type == 'train':
                    dest_path = os.path.join(self.config.train_path, class_folder_name)
                    logging.info(f"   🦠 Copying {disease_name} ({len(images)} train images)")
                    total_train += len(images)
                else:
                    dest_path = os.path.join(self.config.test_path, class_folder_name)
                    logging.info(f"   🦠 Copying {disease_name} ({len(images)} test images)")
                    total_test += len(images)
                
                os.makedirs(dest_path, exist_ok=True)
                for file in images:
                    src = os.path.join(disease_path, file)
                    dst = os.path.join(dest_path, file)
                    shutil.copy2(src, dst)
                
                # Track class only once
                if class_folder_name not in self.class_names:
                    self.class_names[class_folder_name] = {
                        "crop": crop_name,
                        "disease": disease_name
                    }
        
        return total_train, total_test

    def initiate_data_ingestion(self):
        logging.info("Starting data ingestion for disease-only crop dataset")

        try:
            dataset_root = "Dataset"
            
            if not os.path.exists(dataset_root):
                raise Exception(f"Dataset folder not found at {dataset_root}")

            # Clear old artifacts
            logging.info("Clearing old artifacts...")
            if os.path.exists(self.config.train_path):
                self.safe_remove_tree(self.config.train_path)
            if os.path.exists(self.config.test_path):
                self.safe_remove_tree(self.config.test_path)

            total_train = 0
            total_test = 0
            class_count = 0

            # Iterate through crop types (Grapes_Diseases, Brinjal_Diseases, etc.)
            for crop_name in sorted(os.listdir(dataset_root)):
                crop_path = os.path.join(dataset_root, crop_name)
                
                # Skip if not a directory
                if not os.path.isdir(crop_path):
                    continue
                
                logging.info(f"📁 Processing crop: {crop_name}")
                
                # Check if this crop already has test/train split
                contents = sorted(os.listdir(crop_path))
                if 'test' in contents or 'train' in contents:
                    # Grapes_Diseases structure: has test/train folders with disease subdirs
                    logging.info(f"   Found pre-split test/train structure")
                    train_count, test_count = self._process_presplit_dataset(crop_name, crop_path)
                else:
                    # Brinjal_Diseases structure: nested disease folders
                    logging.info(f"   Found nested disease folder structure")
                    train_count, test_count = self._process_nested_dataset(crop_name, crop_path)
                
                total_train += train_count
                total_test += test_count
                class_count += len([k for k in self.class_names.keys() if k.startswith(crop_name)])

            # Save class names to JSON
            os.makedirs(os.path.dirname(self.config.class_names_path), exist_ok=True)
            with open(self.config.class_names_path, 'w') as f:
                json.dump(self.class_names, f, indent=4)
            logging.info(f"✅ Class names saved to {self.config.class_names_path}")

            logging.info("\n✅ Data ingestion completed successfully")
            logging.info(f"   📊 Total classes: {len(self.class_names)}")
            logging.info(f"   🖼️  Total train images: {total_train}")
            logging.info(f"   🖼️  Total test images: {total_test}")

            return self.config.train_path, self.config.test_path

        except Exception as e:
            raise CustomException(e, sys)


if __name__ == "__main__":
    obj = DataIngestion()
    train_path, test_path = obj.initiate_data_ingestion()
    print("Train Path:", train_path)
    print("Test Path:", test_path)