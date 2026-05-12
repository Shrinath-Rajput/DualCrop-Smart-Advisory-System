"""
Production-Ready Deep Learning Training Pipeline
For Crop Disease Prediction System (Grapes & Brinjal)

Trains EfficientNetB0 model for:
- Grapes: Healthy, Black Rot, Esca, Leaf Blight
- Brinjal: Healthy, Leaf Spot, Wilt, Mosaic
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
import matplotlib.pyplot as plt
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrainingConfig:
    """Training configuration"""
    DATASET_PATH = "Dataset"
    MODEL_OUTPUT_PATH = "crop_disease_model.h5"
    CLASS_NAMES_PATH = "class_names.json"
    
    IMAGE_SIZE = 224
    BATCH_SIZE = 32
    EPOCHS = 20
    VALIDATION_SPLIT = 0.2
    
    # Augmentation
    ROTATION_RANGE = 20
    ZOOM_RANGE = 0.2
    HORIZONTAL_FLIP = True
    SHEAR_RANGE = 0.2
    BRIGHTNESS_RANGE = [0.8, 1.2]
    
    # Learning
    LEARNING_RATE = 1e-4
    EARLY_STOPPING_PATIENCE = 5
    REDUCE_LR_PATIENCE = 3
    
    SEED = 42


def setup_seed(seed):
    """Set random seeds for reproducibility"""
    np.random.seed(seed)
    tf.random.set_seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)


def validate_and_load_dataset(dataset_path):
    """Validate dataset structure and load all classes"""
    logger.info(f"Validating dataset at: {dataset_path}")
    
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset path not found: {dataset_path}")
    
    # Get all class directories
    classes = sorted([
        d for d in os.listdir(dataset_path)
        if os.path.isdir(os.path.join(dataset_path, d))
    ])
    
    if not classes:
        raise ValueError(f"No class directories found in {dataset_path}")
    
    # Validate each class has images
    logger.info("\n" + "="*70)
    logger.info("DATASET STRUCTURE VALIDATION")
    logger.info("="*70)
    
    total_images = 0
    class_stats = {}
    
    for idx, class_name in enumerate(classes):
        class_path = os.path.join(dataset_path, class_name)
        images = [f for f in os.listdir(class_path) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp'))]
        
        if not images:
            logger.warning(f"⚠️  No images found in {class_name}")
            continue
        
        class_stats[class_name] = len(images)
        total_images += len(images)
        
        logger.info(f"[{idx+1:2d}] {class_name:40s} → {len(images):4d} images")
    
    logger.info("-"*70)
    logger.info(f"Total Classes: {len(classes)}")
    logger.info(f"Total Images: {total_images}")
    logger.info("="*70 + "\n")
    
    if total_images < 100:
        logger.warning(f"⚠️  WARNING: Very few images ({total_images}). Training may be suboptimal.")
    
    return classes, class_stats


def create_data_generators(dataset_path, config):
    """Create training and validation data generators"""
    
    logger.info("Creating data generators with augmentation...")
    
    # Training data generator with augmentation
    train_datagen = ImageDataGenerator(
        rotation_range=config.ROTATION_RANGE,
        zoom_range=config.ZOOM_RANGE,
        horizontal_flip=config.HORIZONTAL_FLIP,
        shear_range=config.SHEAR_RANGE,
        brightness_range=config.BRIGHTNESS_RANGE,
        width_shift_range=0.15,
        height_shift_range=0.15,
        fill_mode='nearest',
        rescale=1./255,
        validation_split=config.VALIDATION_SPLIT
    )
    
    # Load training data
    train_generator = train_datagen.flow_from_directory(
        dataset_path,
        target_size=(config.IMAGE_SIZE, config.IMAGE_SIZE),
        batch_size=config.BATCH_SIZE,
        class_mode='categorical',
        subset='training',
        shuffle=True,
        seed=config.SEED
    )
    
    # Load validation data
    val_generator = train_datagen.flow_from_directory(
        dataset_path,
        target_size=(config.IMAGE_SIZE, config.IMAGE_SIZE),
        batch_size=config.BATCH_SIZE,
        class_mode='categorical',
        subset='validation',
        shuffle=True,
        seed=config.SEED
    )
    
    logger.info(f"✓ Train generator: {train_generator.samples} samples")
    logger.info(f"✓ Val generator: {val_generator.samples} samples")
    
    return train_generator, val_generator


def build_model(num_classes, config):
    """Build EfficientNetB0-based model"""
    
    logger.info("\nBuilding EfficientNetB0 model...")
    
    # Load pre-trained EfficientNetB0
    base_model = EfficientNetB0(
        input_shape=(config.IMAGE_SIZE, config.IMAGE_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model layers
    base_model.trainable = False
    
    # Build custom model
    model = models.Sequential([
        layers.Input(shape=(config.IMAGE_SIZE, config.IMAGE_SIZE, 3)),
        base_model,
        layers.GlobalAveragePooling2D(),
        
        # Dense layers with regularization
        layers.Dense(512, activation='relu', 
                    kernel_regularizer=keras.regularizers.l2(1e-4)),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        
        layers.Dense(256, activation='relu',
                    kernel_regularizer=keras.regularizers.l2(1e-4)),
        layers.BatchNormalization(),
        layers.Dropout(0.4),
        
        layers.Dense(128, activation='relu',
                    kernel_regularizer=keras.regularizers.l2(1e-4)),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        # Output layer - SOFTMAX for dynamic confidence
        layers.Dense(num_classes, activation='softmax')
    ])
    
    # Compile
    model.compile(
        optimizer=Adam(learning_rate=config.LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    logger.info(f"✓ Model built with {num_classes} output classes")
    logger.info(f"✓ Total parameters: {model.count_params():,}")
    
    return model


def get_callbacks(config):
    """Create training callbacks"""
    
    callbacks = [
        # Early stopping
        EarlyStopping(
            monitor='val_loss',
            patience=config.EARLY_STOPPING_PATIENCE,
            restore_best_weights=True,
            verbose=1
        ),
        
        # Model checkpoint - save best model
        ModelCheckpoint(
            config.MODEL_OUTPUT_PATH,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1,
            mode='max'
        ),
        
        # Reduce learning rate on plateau
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=config.REDUCE_LR_PATIENCE,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    return callbacks


def train_model(model, train_gen, val_gen, config):
    """Train the model"""
    
    logger.info("\n" + "="*70)
    logger.info("STARTING TRAINING")
    logger.info("="*70)
    
    callbacks = get_callbacks(config)
    
    history = model.fit(
        train_gen,
        validation_data=val_gen,
        epochs=config.EPOCHS,
        callbacks=callbacks,
        verbose=1,
        steps_per_epoch=len(train_gen)
    )
    
    return history


def save_class_names(train_generator, config):
    """Save class names and indices"""
    
    class_indices = train_generator.class_indices
    classes = sorted(class_indices.items(), key=lambda x: x[1])
    
    class_names_data = {
        'classes': {str(i): name for name, i in class_indices.items()},
        'class_indices': class_indices,
        'num_classes': len(class_indices)
    }
    
    with open(config.CLASS_NAMES_PATH, 'w') as f:
        json.dump(class_names_data, f, indent=2)
    
    logger.info(f"\n✓ Class names saved to: {config.CLASS_NAMES_PATH}")
    
    return class_names_data


def plot_training_history(history, output_path='training_history.png'):
    """Plot training and validation metrics"""
    
    logger.info("Generating training visualization...")
    
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Accuracy
    axes[0].plot(history.history['accuracy'], label='Train Accuracy', linewidth=2)
    axes[0].plot(history.history['val_accuracy'], label='Val Accuracy', linewidth=2)
    axes[0].set_xlabel('Epoch', fontsize=12)
    axes[0].set_ylabel('Accuracy', fontsize=12)
    axes[0].set_title('Model Accuracy Over Epochs', fontsize=13, fontweight='bold')
    axes[0].legend(fontsize=11)
    axes[0].grid(True, alpha=0.3)
    
    # Loss
    axes[1].plot(history.history['loss'], label='Train Loss', linewidth=2)
    axes[1].plot(history.history['val_loss'], label='Val Loss', linewidth=2)
    axes[1].set_xlabel('Epoch', fontsize=12)
    axes[1].set_ylabel('Loss', fontsize=12)
    axes[1].set_title('Model Loss Over Epochs', fontsize=13, fontweight='bold')
    axes[1].legend(fontsize=11)
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"✓ Visualization saved to: {output_path}")
    plt.close()


def main():
    """Main training pipeline"""
    
    print("\n" + "█"*70)
    print("█" + "CROP DISEASE PREDICTION MODEL - TRAINING PIPELINE".center(68) + "█")
    print("█"*70 + "\n")
    
    try:
        config = TrainingConfig()
        setup_seed(config.SEED)
        
        # Step 1: Validate dataset
        logger.info("\n[STEP 1/7] Validating Dataset...")
        classes, class_stats = validate_and_load_dataset(config.DATASET_PATH)
        
        # Step 2: Create data generators
        logger.info("\n[STEP 2/7] Creating Data Generators...")
        train_gen, val_gen = create_data_generators(config.DATASET_PATH, config)
        
        # Step 3: Build model
        logger.info("\n[STEP 3/7] Building Model Architecture...")
        num_classes = len(train_gen.class_indices)
        model = build_model(num_classes, config)
        
        # Step 4: Print model summary
        logger.info("\n[STEP 4/7] Model Summary:")
        model.summary()
        
        # Step 5: Train model
        logger.info("\n[STEP 5/7] Training Model...")
        history = train_model(model, train_gen, val_gen, config)
        
        # Step 6: Save model and class names
        logger.info("\n[STEP 6/7] Saving Model and Metadata...")
        class_names_data = save_class_names(train_gen, config)
        logger.info(f"✓ Model saved to: {config.MODEL_OUTPUT_PATH}")
        
        # Step 7: Generate visualization
        logger.info("\n[STEP 7/7] Generating Visualization...")
        plot_training_history(history)
        
        # Print summary
        logger.info("\n" + "="*70)
        logger.info("TRAINING COMPLETED SUCCESSFULLY")
        logger.info("="*70)
        logger.info(f"✓ Model: {config.MODEL_OUTPUT_PATH}")
        logger.info(f"✓ Classes: {num_classes}")
        logger.info(f"✓ Image Size: {config.IMAGE_SIZE}x{config.IMAGE_SIZE}")
        logger.info(f"✓ Total Epochs: {len(history.history['accuracy'])}")
        logger.info(f"✓ Final Train Accuracy: {history.history['accuracy'][-1]:.4f}")
        logger.info(f"✓ Final Val Accuracy: {history.history['val_accuracy'][-1]:.4f}")
        logger.info(f"✓ Final Train Loss: {history.history['loss'][-1]:.4f}")
        logger.info(f"✓ Final Val Loss: {history.history['val_loss'][-1]:.4f}")
        logger.info("="*70 + "\n")
        
        logger.info("✅ Training pipeline completed successfully!\n")
        
    except Exception as e:
        logger.error(f"\n❌ ERROR: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
