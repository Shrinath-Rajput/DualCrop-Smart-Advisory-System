"""
COMPLETE PRODUCTION-READY CROP DISEASE TRAINING PIPELINE
=========================================================

THIS SCRIPT:
✓ Uses proper TensorFlow/Keras training
✓ Handles real dataset structure
✓ Implements data augmentation
✓ Includes validation split
✓ Uses EarlyStopping to prevent overfitting
✓ Uses ModelCheckpoint to save best weights
✓ Uses ReduceLROnPlateau for adaptive learning
✓ Generates proper class_names.json
✓ Saves trained model in multiple formats (.h5 and .keras)
✓ Tracks training history and metrics

DATASET STRUCTURE EXPECTED:
dataset/
├── Brinjal_Healthy/
├── Brinjal_Little_Leaf/
├── Brinjal_Leaf_Spot/
├── Brinjal_Blight/
├── Grapes_Healthy/
├── Grapes_Black_Measles/
├── Grapes_Black_Rot/
├── Grapes_Isariopsis_Leaf_Spot/

Or use existing dataset:
Dataset/
├── Binjal_Diseases/
├── Grapes_Diseases/

This script will organize it properly.
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CropDiseaseTrainer:
    """Complete training pipeline for crop disease detection"""
    
    # Configuration
    IMAGE_SIZE = 224
    BATCH_SIZE = 32
    EPOCHS = 100
    VALIDATION_SPLIT = 0.2
    RANDOM_SEED = 42
    
    # Paths
    DATASET_DIR = "Dataset"
    ARTIFACTS_DIR = "artifacts"
    LOG_DIR = "logs/training"
    
    def __init__(self):
        """Initialize trainer"""
        np.random.seed(self.RANDOM_SEED)
        tf.random.set_seed(self.RANDOM_SEED)
        
        # Create directories
        os.makedirs(self.ARTIFACTS_DIR, exist_ok=True)
        os.makedirs(self.LOG_DIR, exist_ok=True)
        
        logger.info("="*80)
        logger.info("Crop Disease Training Pipeline Initialized")
        logger.info("="*80)
        logger.info(f"Image Size: {self.IMAGE_SIZE}x{self.IMAGE_SIZE}")
        logger.info(f"Batch Size: {self.BATCH_SIZE}")
        logger.info(f"Max Epochs: {self.EPOCHS}")
        logger.info(f"Validation Split: {self.VALIDATION_SPLIT*100}%")
    
    def create_proper_dataset_structure(self):
        """
        Organize dataset into proper structure with class folders
        
        Creates:
        dataset/
        ├── Brinjal_Healthy/
        ├── Brinjal_Little_Leaf/
        ├── Brinjal_Leaf_Spot/
        ├── Brinjal_Blight/
        ├── Grapes_Healthy/
        ├── Grapes_Black_Measles/
        ├── Grapes_Black_Rot/
        ├── Grapes_Isariopsis_Leaf_Spot/
        """
        logger.info("\n" + "="*80)
        logger.info("STEP 1: Creating Proper Dataset Structure")
        logger.info("="*80)
        
        # Define proper class structure
        classes = [
            "Brinjal_Healthy",
            "Brinjal_Little_Leaf",
            "Brinjal_Leaf_Spot",
            "Brinjal_Blight",
            "Grapes_Healthy",
            "Grapes_Black_Measles",
            "Grapes_Black_Rot",
            "Grapes_Isariopsis_Leaf_Spot"
        ]
        
        # Create dataset directory structure
        dataset_root = "dataset"
        os.makedirs(dataset_root, exist_ok=True)
        
        for class_name in classes:
            class_dir = os.path.join(dataset_root, class_name)
            os.makedirs(class_dir, exist_ok=True)
            logger.info(f"✓ Created: {class_dir}")
        
        # Try to organize existing data
        self._organize_existing_data(dataset_root, classes)
        
        return dataset_root, classes
    
    def _organize_existing_data(self, dataset_root, classes):
        """Try to organize existing Dataset folder into new structure"""
        logger.info("\nAttempting to organize existing Dataset folder...")
        
        if not os.path.exists(self.DATASET_DIR):
            logger.warning(f"Existing dataset folder not found at {self.DATASET_DIR}")
            logger.info("Please manually add images to dataset/<class_name>/ folders")
            return
        
        # Check for Brinjal data
        brinjal_path = os.path.join(self.DATASET_DIR, "Binjal_Diseases")
        if os.path.exists(brinjal_path):
            self._copy_class_images(brinjal_path, dataset_root, "Brinjal_Little_Leaf")
        
        # Check for Grapes data
        grapes_path = os.path.join(self.DATASET_DIR, "Grapes_Diseases")
        if os.path.exists(grapes_path):
            self._organize_grapes_data(grapes_path, dataset_root)
        
        logger.info("✓ Existing data organization attempted")
    
    def _copy_class_images(self, src_path, dst_root, class_name):
        """Copy images from source to destination class folder"""
        import shutil
        from pathlib import Path
        
        dst_path = os.path.join(dst_root, class_name)
        
        # Find all image files
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        image_count = 0
        
        for item in Path(src_path).rglob("*"):
            if item.suffix.lower() in image_extensions:
                try:
                    shutil.copy2(str(item), dst_path)
                    image_count += 1
                except Exception as e:
                    logger.warning(f"Could not copy {item}: {e}")
        
        logger.info(f"  Copied {image_count} images to {class_name}")
    
    def _organize_grapes_data(self, grapes_path, dataset_root):
        """Organize grapes data into disease classes"""
        import shutil
        from pathlib import Path
        
        # Map disease folders to class names
        disease_mapping = {
            "healthy": "Grapes_Healthy",
            "black rot": "Grapes_Black_Rot",
            "black measles": "Grapes_Black_Measles",
            "esca": "Grapes_Black_Measles",
            "leaf blight": "Grapes_Isariopsis_Leaf_Spot",
            "isariopsis": "Grapes_Isariopsis_Leaf_Spot",
        }
        
        image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
        
        # Process all folders in grapes directory
        for item in Path(grapes_path).iterdir():
            if not item.is_dir():
                continue
            
            folder_name = item.name.lower()
            
            # Find matching disease class
            target_class = None
            for keyword, class_name in disease_mapping.items():
                if keyword in folder_name:
                    target_class = class_name
                    break
            
            if target_class is None:
                logger.warning(f"Could not map folder: {item.name}")
                continue
            
            # Copy images
            dst_path = os.path.join(dataset_root, target_class)
            image_count = 0
            
            for image_file in item.rglob("*"):
                if image_file.suffix.lower() in image_extensions:
                    try:
                        shutil.copy2(str(image_file), dst_path)
                        image_count += 1
                    except Exception as e:
                        logger.warning(f"Could not copy {image_file}: {e}")
            
            logger.info(f"  Mapped {item.name} → {target_class} ({image_count} images)")
    
    def prepare_data_generators(self, dataset_root, classes):
        """Create data generators with augmentation"""
        logger.info("\n" + "="*80)
        logger.info("STEP 2: Preparing Data Generators with Augmentation")
        logger.info("="*80)
        
        # Training data generator with augmentation
        train_generator = ImageDataGenerator(
            rescale=1.0 / 255.0,
            rotation_range=20,
            width_shift_range=0.2,
            height_shift_range=0.2,
            horizontal_flip=True,
            vertical_flip=True,
            zoom_range=0.2,
            shear_range=0.15,
            fill_mode='nearest',
            validation_split=self.VALIDATION_SPLIT,
        )
        
        # Load training data
        logger.info("Loading training data with augmentation...")
        train_data = train_generator.flow_from_directory(
            dataset_root,
            target_size=(self.IMAGE_SIZE, self.IMAGE_SIZE),
            batch_size=self.BATCH_SIZE,
            class_mode='categorical',
            subset='training',
            shuffle=True
        )
        
        # Load validation data
        logger.info("Loading validation data...")
        validation_data = train_generator.flow_from_directory(
            dataset_root,
            target_size=(self.IMAGE_SIZE, self.IMAGE_SIZE),
            batch_size=self.BATCH_SIZE,
            class_mode='categorical',
            subset='validation',
            shuffle=True
        )
        
        logger.info(f"✓ Training samples: {train_data.samples}")
        logger.info(f"✓ Validation samples: {validation_data.samples}")
        logger.info(f"✓ Classes: {list(train_data.class_indices.keys())}")
        
        # Save class mapping
        self._save_class_mapping(train_data.class_indices)
        
        return train_data, validation_data, train_data.class_indices
    
    def _save_class_mapping(self, class_indices):
        """Save class to index mapping to JSON"""
        # Reverse mapping: index -> class name
        class_names = {str(v): k for k, v in class_indices.items()}
        
        output_path = os.path.join(self.ARTIFACTS_DIR, "class_names.json")
        
        with open(output_path, 'w') as f:
            json.dump(class_names, f, indent=2)
        
        logger.info(f"\n✓ Class mapping saved to: {output_path}")
        logger.info("Class Mapping:")
        for idx in sorted(class_names.keys(), key=lambda x: int(x)):
            logger.info(f"  [{idx}] {class_names[idx]}")
    
    def build_model(self, num_classes):
        """Build convolutional neural network model"""
        logger.info("\n" + "="*80)
        logger.info("STEP 3: Building Model")
        logger.info("="*80)
        
        # Use transfer learning with MobileNetV2
        logger.info("Using MobileNetV2 with transfer learning...")
        
        base_model = keras.applications.MobileNetV2(
            input_shape=(self.IMAGE_SIZE, self.IMAGE_SIZE, 3),
            include_top=False,
            weights='imagenet'
        )
        
        # Freeze base model layers for faster training
        base_model.trainable = False
        logger.info("✓ Base model layers frozen")
        
        # Build complete model
        model = models.Sequential([
            layers.Input(shape=(self.IMAGE_SIZE, self.IMAGE_SIZE, 3)),
            
            # Preprocessing layers
            layers.Rescaling(1./127.5, offset=-1),  # Normalize to [-1, 1]
            
            # Base model (MobileNetV2)
            base_model,
            
            # Custom top layers
            layers.GlobalAveragePooling2D(),
            layers.Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(1e-4)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(128, activation='relu', kernel_regularizer=keras.regularizers.l2(1e-4)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(64, activation='relu', kernel_regularizer=keras.regularizers.l2(1e-4)),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            # Output layer with softmax
            layers.Dense(num_classes, activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy', keras.metrics.Precision(), keras.metrics.Recall()]
        )
        
        logger.info("✓ Model built and compiled")
        model.summary()
        
        return model
    
    def train_model(self, model, train_data, validation_data):
        """Train the model with callbacks"""
        logger.info("\n" + "="*80)
        logger.info("STEP 4: Training Model")
        logger.info("="*80)
        
        # Callbacks
        callbacks = [
            # Save best model
            keras.callbacks.ModelCheckpoint(
                os.path.join(self.ARTIFACTS_DIR, 'crop_disease_model_best.h5'),
                monitor='val_loss',
                save_best_only=True,
                verbose=1
            ),
            
            # Stop if no improvement
            keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            
            # Reduce learning rate on plateau
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=5,
                min_lr=1e-7,
                verbose=1
            ),
            
            # Tensorboard logging
            keras.callbacks.TensorBoard(
                log_dir=self.LOG_DIR,
                histogram_freq=1
            )
        ]
        
        # Train
        logger.info("Starting training...")
        history = model.fit(
            train_data,
            epochs=self.EPOCHS,
            validation_data=validation_data,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def save_model(self, model):
        """Save trained model in multiple formats"""
        logger.info("\n" + "="*80)
        logger.info("STEP 5: Saving Model")
        logger.info("="*80)
        
        # Save as .h5
        h5_path = os.path.join(self.ARTIFACTS_DIR, 'crop_disease_model.h5')
        model.save(h5_path)
        logger.info(f"✓ Model saved (H5): {h5_path}")
        
        # Save as .keras (TensorFlow 2.11+)
        keras_path = os.path.join(self.ARTIFACTS_DIR, 'crop_disease_model.keras')
        model.save(keras_path)
        logger.info(f"✓ Model saved (Keras): {keras_path}")
    
    def save_training_history(self, history):
        """Save training history to JSON"""
        history_dict = {
            'loss': history.history['loss'],
            'accuracy': history.history['accuracy'],
            'val_loss': history.history['val_loss'],
            'val_accuracy': history.history['val_accuracy'],
            'epochs': len(history.history['loss'])
        }
        
        history_path = os.path.join(self.ARTIFACTS_DIR, 'training_history.json')
        
        # Convert numpy values to Python floats for JSON serialization
        json_history = {}
        for key, value in history_dict.items():
            if isinstance(value, list):
                json_history[key] = [float(v) for v in value]
            else:
                json_history[key] = value
        
        with open(history_path, 'w') as f:
            json.dump(json_history, f, indent=2)
        
        logger.info(f"✓ Training history saved: {history_path}")
    
    def run_complete_pipeline(self):
        """Run complete training pipeline"""
        try:
            logger.info("\n" + "="*80)
            logger.info("STARTING COMPLETE CROP DISEASE TRAINING PIPELINE")
            logger.info("="*80)
            
            # Step 1: Create dataset structure
            dataset_root, classes = self.create_proper_dataset_structure()
            
            # Step 2: Prepare data
            train_data, val_data, class_indices = self.prepare_data_generators(dataset_root, classes)
            
            # Step 3: Build model
            num_classes = len(class_indices)
            model = self.build_model(num_classes)
            
            # Step 4: Train model
            history = self.train_model(model, train_data, val_data)
            
            # Step 5: Save model
            self.save_model(model)
            
            # Step 6: Save history
            self.save_training_history(history)
            
            logger.info("\n" + "="*80)
            logger.info("✓ TRAINING PIPELINE COMPLETE")
            logger.info("="*80)
            logger.info(f"Model saved to: {self.ARTIFACTS_DIR}/crop_disease_model.h5")
            logger.info(f"Classes saved to: {self.ARTIFACTS_DIR}/class_names.json")
            logger.info(f"Training history saved to: {self.ARTIFACTS_DIR}/training_history.json")
            
            # Evaluate model
            logger.info("\n" + "="*80)
            logger.info("Evaluating Model")
            logger.info("="*80)
            
            val_loss, val_accuracy, val_precision, val_recall = model.evaluate(val_data)
            logger.info(f"Validation Loss: {val_loss:.4f}")
            logger.info(f"Validation Accuracy: {val_accuracy*100:.2f}%")
            logger.info(f"Validation Precision: {val_precision:.4f}")
            logger.info(f"Validation Recall: {val_recall:.4f}")
            
            return model, class_indices
            
        except Exception as e:
            logger.error(f"Error in training pipeline: {str(e)}", exc_info=True)
            raise


def main():
    """Main entry point"""
    try:
        trainer = CropDiseaseTrainer()
        model, classes = trainer.run_complete_pipeline()
        logger.info("\n✓ Training complete! Model is ready for predictions.")
        
    except KeyboardInterrupt:
        logger.info("\nTraining interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
