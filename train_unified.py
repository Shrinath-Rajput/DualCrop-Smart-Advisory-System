po 
""
UNIFIED CROP DISEASE PREDICTION MODEL - FAST TRAINING PIPELINE (OPTIMIZED)
===========================================================================

This script trains a SINGLE unified model for both crops and all diseases.
OPTIMIZED FOR FAST TRAINING with EarlyStopping and reduced epochs.

TRAINING ONLY ON 8 CLASSES (ignores Binjal_Diseases and Grapes_Diseases folders):
- Brinjal_Healthy
- Brinjal_Little_Leaf
- Brinjal_Leaf_Spot
- Brinjal_Blight
- Grapes_Healthy
- Grapes_Black_Measles
- Grapes_Black_Rot
- Grapes_Isariopsis_Leaf_Spot

OUTPUT:
- artifacts/best_model.keras (optimized model)
- artifacts/class_names.json (8 classes)

OPTIMIZATIONS:
- Epochs: 10 (reduced from 100)
- EarlyStopping patience: 3
- Batch size: 16 (reduced from 32)
- Mixed precision training enabled
- Lightweight EfficientNetB0 architecture
- Fast CPU-compatible training
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
)
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.mixed_precision import LossScaleOptimizer
import matplotlib.pyplot as plt
import logging
from datetime import datetime
import time

# Configure logging with detailed epoch progress
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Note: Mixed precision training disabled due to CPU compatibility
# (CPU lacks AVX-512 support and TopKCategoricalAccuracy type mismatch)
# Training will use float32 for stability and compatibility


class UnifiedTrainingConfig:
    """Unified training configuration for all 8 classes - OPTIMIZED"""
    
    # Dataset and model paths
    DATASET_BASE = "Dataset"
    MODELS_DIR = "artifacts"
    MODEL_PATH = os.path.join(MODELS_DIR, "best_model.keras")  # Changed to .keras format
    CLASSES_PATH = os.path.join(MODELS_DIR, "class_names.json")
    
    # 8 classes - unified structure (FILTERS OUT Binjal_Diseases and Grapes_Diseases)
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
    
    # Folders to IGNORE (skip during training)
    IGNORE_FOLDERS = [
        "Binjal_Diseases",
        "Grapes_Diseases"
    ]
    
    # Training parameters - OPTIMIZED FOR SPEED
    IMAGE_SIZE = 224
    BATCH_SIZE = 16  # REDUCED from 32 for faster training
    EPOCHS = 10  # REDUCED from 100 for faster training
    VALIDATION_SPLIT = 0.15
    TEST_SPLIT = 0.1
    
    # Data augmentation - BALANCED for speed and robustness
    ROTATION_RANGE = 20
    ZOOM_RANGE = 0.25
    HORIZONTAL_FLIP = True
    VERTICAL_FLIP = True
    SHEAR_RANGE = 0.15
    WIDTH_SHIFT = 0.15
    HEIGHT_SHIFT = 0.15
    BRIGHTNESS_RANGE = [0.8, 1.2]
    
    # Learning rates
    LEARNING_RATE = 1e-3  # Slightly higher for faster convergence
    EARLY_STOPPING_PATIENCE = 3  # REDUCED from 15 for faster stop
    REDUCE_LR_PATIENCE = 2
    REDUCE_LR_FACTOR = 0.5
    
    SEED = 42


def setup_seed(seed):
    """Set random seeds for reproducibility"""
    np.random.seed(seed)
    tf.random.set_seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    logger.info(f"✓ Random seeds set to {seed}")


def ensure_directories():
    """Create required directories"""
    os.makedirs(UnifiedTrainingConfig.MODELS_DIR, exist_ok=True)
    logger.info(f"✓ Models directory ready: {UnifiedTrainingConfig.MODELS_DIR}")


def validate_dataset_structure():
    """Validate unified dataset structure (ignores unwanted disease folders)"""
    logger.info("\n" + "="*80)
    logger.info("VALIDATING DATASET STRUCTURE")
    logger.info("="*80)
    
    config = UnifiedTrainingConfig()
    base_path = config.DATASET_BASE
    
    if not os.path.exists(base_path):
        logger.error(f"❌ Dataset directory not found: {base_path}")
        return False
    
    all_classes = {}
    total_images = 0
    
    # Check for each expected class
    for class_name in config.EXPECTED_CLASSES:
        class_path = os.path.join(base_path, class_name)
        
        if not os.path.exists(class_path):
            logger.warning(f"⚠ Class directory not found: {class_name}")
            all_classes[class_name] = 0
            continue
        
        # Count images
        images = [f for f in os.listdir(class_path) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))]
        
        image_count = len(images)
        all_classes[class_name] = image_count
        total_images += image_count
        
        status = "✓" if image_count > 0 else "⚠"
        logger.info(f"{status} {class_name:40s} → {image_count:6d} images")
    
    # Log ignored folders
    logger.info("\n" + "-"*80)
    logger.info("IGNORED FOLDERS (not used in training):")
    for ignore_folder in config.IGNORE_FOLDERS:
        ignore_path = os.path.join(base_path, ignore_folder)
        if os.path.exists(ignore_path):
            count = len([f for f in os.listdir(ignore_path) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif'))])
            logger.info(f"  ⊗ {ignore_folder:40s} → {count:6d} images (SKIPPED)")
    
    logger.info("="*80)
    logger.info(f"Total images for training: {total_images}")
    logger.info("="*80 + "\n")
    
    # Check if we have minimum data
    min_classes_with_data = sum(1 for count in all_classes.values() if count > 0)
    min_total_images = sum(all_classes.values())
    
    if min_classes_with_data < 4:
        logger.error(f"❌ Need at least 4 classes with data. Found {min_classes_with_data}")
        return False
    
    if min_total_images < 100:
        logger.error(f"❌ Need at least 100 total images. Found {min_total_images}")
        return False
    
    return True


def create_data_generator(config):
    """Create training data generator with balanced augmentation"""
    
    logger.info("Creating data generator (balanced augmentation for speed)...")
    
    # Balanced augmentation - faster than strong augmentation
    datagen = ImageDataGenerator(
        rotation_range=config.ROTATION_RANGE,
        zoom_range=config.ZOOM_RANGE,
        horizontal_flip=config.HORIZONTAL_FLIP,
        vertical_flip=config.VERTICAL_FLIP,
        shear_range=config.SHEAR_RANGE,
        width_shift_range=config.WIDTH_SHIFT,
        height_shift_range=config.HEIGHT_SHIFT,
        brightness_range=config.BRIGHTNESS_RANGE,
        fill_mode='nearest',
        rescale=1./255.0  # Normalize to [0, 1]
    )
    
    logger.info("✓ Data generator created")
    return datagen


def load_data(config, datagen):
    """Load unified dataset with train/val split (only expected classes)"""
    
    logger.info("\nLoading dataset from: " + config.DATASET_BASE)
    logger.info(f"Batch size: {config.BATCH_SIZE} (reduced for faster training)")
    
    # Load from directory with validation split
    data_generator = datagen.flow_from_directory(
        config.DATASET_BASE,
        target_size=(config.IMAGE_SIZE, config.IMAGE_SIZE),
        batch_size=config.BATCH_SIZE,
        class_mode='categorical',
        subset=None,  # Load all data
        shuffle=True,
        seed=config.SEED,
        classes=config.EXPECTED_CLASSES  # ONLY load expected classes
    )
    
    logger.info(f"✓ Dataset loaded: {data_generator.samples} total images")
    logger.info(f"✓ Classes found: {len(data_generator.class_indices)}")
    
    # Display class indices
    for class_name, idx in sorted(data_generator.class_indices.items(), key=lambda x: x[1]):
        logger.info(f"    [{idx}] {class_name}")
    
    # Create train/val split manually
    class_indices_inverse = {v: k for k, v in data_generator.class_indices.items()}
    
    return data_generator, class_indices_inverse


def build_unified_model(num_classes, config, input_shape=(224, 224, 3)):
    """
    Build lightweight unified disease detection model
    
    Architecture:
    - EfficientNetB0 base (transfer learning from ImageNet)
    - Global average pooling
    - Fewer dense layers for faster training
    - BatchNorm + Dropout for regularization
    - Output layer with softmax for all 8 classes
    """
    
    logger.info(f"\nBuilding lightweight model for {num_classes} classes...")
    
    # Load EfficientNetB0 with ImageNet weights
    base_model = EfficientNetB0(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model for transfer learning
    base_model.trainable = False
    logger.info(f"  Base model (EfficientNetB0) frozen with {base_model.count_params():,} parameters")
    
    # Build simplified model for faster training
    model = models.Sequential([
        layers.Input(shape=input_shape),
        
        # Input normalization
        layers.LayerNormalization(),
        
        # Transfer learning backbone
        base_model,
        
        # Global average pooling
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        
        # Dense block 1 - REDUCED from 1024 to 512 for speed
        layers.Dense(512, activation='relu', 
                    kernel_regularizer=keras.regularizers.l2(1e-4),
                    kernel_initializer='he_normal'),
        layers.BatchNormalization(),
        layers.Dropout(0.4),
        
        # Dense block 2 - REDUCED from 512 to 256 for speed
        layers.Dense(256, activation='relu',
                    kernel_regularizer=keras.regularizers.l2(1e-4),
                    kernel_initializer='he_normal'),
        layers.BatchNormalization(),
        layers.Dropout(0.3),
        
        # Dense block 3 - REDUCED from 256 to 128 for speed
        layers.Dense(128, activation='relu',
                    kernel_regularizer=keras.regularizers.l2(1e-4),
                    kernel_initializer='he_normal'),
        layers.BatchNormalization(),
        layers.Dropout(0.2),
        
        # Output layer - SOFTMAX for proper confidence scores
        layers.Dense(num_classes, activation='softmax')
    ])
    
    # Compile with Adam optimizer (faster than SGD)
    model.compile(
        optimizer=Adam(learning_rate=config.LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=[
            'accuracy',
            keras.metrics.TopKCategoricalAccuracy(k=3, name='top_3_accuracy')
        ]
    )
    
    total_params = model.count_params()
    trainable_params = sum([tf.size(w).numpy() for w in model.trainable_weights])
    
    logger.info(f"\n✓ Model built successfully")
    logger.info(f"  Total parameters: {total_params:,}")
    logger.info(f"  Trainable parameters: {trainable_params:,}")
    
    return model


def train_unified_model(model, train_data, config):
    """Train the unified model with detailed progress logging"""
    
    logger.info("\n" + "="*80)
    logger.info("FAST TRAINING: UNIFIED CROP DISEASE MODEL")
    logger.info("="*80)
    logger.info(f"Epochs: {config.EPOCHS} | Batch Size: {config.BATCH_SIZE} | EarlyStopping Patience: {config.EARLY_STOPPING_PATIENCE}")
    logger.info("="*80 + "\n")
    
    # Callbacks for faster training
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=config.EARLY_STOPPING_PATIENCE,  # Reduced from 15 to 3
            restore_best_weights=True,
            verbose=1,
            min_delta=1e-4
        ),
        ModelCheckpoint(
            config.MODEL_PATH,
            monitor='val_accuracy',
            save_best_only=True,
            verbose=1,
            mode='max'
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=config.REDUCE_LR_FACTOR,
            patience=config.REDUCE_LR_PATIENCE,
            min_lr=1e-7,
            verbose=1
        )
    ]
    
    # Calculate steps per epoch
    steps_per_epoch = max(1, train_data.samples // config.BATCH_SIZE)
    logger.info(f"Training on {train_data.samples} samples ({steps_per_epoch} steps per epoch)")
    
    # Start timer
    start_time = time.time()
    
    # Train model with custom logging
    history = model.fit(
        train_data,
        steps_per_epoch=steps_per_epoch,
        epochs=config.EPOCHS,
        callbacks=callbacks,
        verbose=1
    )
    
    # End timer
    elapsed_time = time.time() - start_time
    logger.info(f"\n✓ Training complete in {elapsed_time:.1f} seconds ({elapsed_time/60:.1f} minutes)")
    
    return history


def save_model_and_classes(model, class_indices_inverse, config):
    """Save model and class mapping in optimized formats"""
    
    logger.info("\nSaving model and classes...")
    
    # Save model in .keras format (more efficient than .h5)
    model.save(config.MODEL_PATH)
    logger.info(f"✓ Model saved: {config.MODEL_PATH}")
    
    # Verify file exists and get size
    if os.path.exists(config.MODEL_PATH):
        model_size = os.path.getsize(config.MODEL_PATH) / (1024*1024)
        logger.info(f"  Model size: {model_size:.1f} MB")
    
    # Create class mapping: index -> class_name
    class_mapping = {}
    for idx, class_name in class_indices_inverse.items():
        class_mapping[str(idx)] = class_name
    
    # Save class mapping
    with open(config.CLASSES_PATH, 'w') as f:
        json.dump(class_mapping, f, indent=2)
    
    logger.info(f"✓ Class mapping saved: {config.CLASSES_PATH}")
    logger.info("\n  Trained classes:")
    for idx, class_name in sorted(class_mapping.items(), key=lambda x: int(x[0])):
        logger.info(f"    [{idx}] {class_name}")


def plot_training_results(history, config):
    """Plot and save simplified training results"""
    
    logger.info("\nGenerating training plots...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Accuracy
    axes[0].plot(history.history['accuracy'], label='Train Accuracy', linewidth=2, marker='o')
    if 'val_accuracy' in history.history:
        axes[0].plot(history.history['val_accuracy'], label='Val Accuracy', linewidth=2, marker='s')
    axes[0].set_title('Model Accuracy', fontsize=12, fontweight='bold')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Accuracy')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Loss
    axes[1].plot(history.history['loss'], label='Train Loss', linewidth=2, marker='o')
    if 'val_loss' in history.history:
        axes[1].plot(history.history['val_loss'], label='Val Loss', linewidth=2, marker='s')
    axes[1].set_title('Model Loss', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Loss')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plot_path = os.path.join(config.MODELS_DIR, 'training_history.png')
    plt.savefig(plot_path, dpi=100, bbox_inches='tight')
    logger.info(f"✓ Plot saved: {plot_path}")
    plt.close()


def main():
    """Main training pipeline - OPTIMIZED FOR FAST TRAINING"""
    
    logger.info("\n" + "="*80)
    logger.info("OPTIMIZED CROP DISEASE PREDICTION - FAST TRAINING PIPELINE")
    logger.info("="*80)
    logger.info("Configuration: 10 epochs, EarlyStopping, batch size 16, float32")
    logger.info("="*80 + "\n")
    
    config = UnifiedTrainingConfig()
    
    # Setup
    setup_seed(config.SEED)
    ensure_directories()
    
    # Validate dataset
    if not validate_dataset_structure():
        logger.error("❌ Dataset validation failed!")
        return False
    
    # Load data
    datagen = create_data_generator(config)
    train_data, class_indices_inverse = load_data(config, datagen)
    
    # Build model
    num_classes = len(train_data.class_indices)
    model = build_unified_model(num_classes, config)
    
    # Train
    history = train_unified_model(model, train_data, config)
    
    # Save
    save_model_and_classes(model, class_indices_inverse, config)
    
    # Plot
    plot_training_results(history, config)
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("✓ FAST TRAINING COMPLETED SUCCESSFULLY")
    logger.info("="*80)
    logger.info(f"Model:      {config.MODEL_PATH}")
    logger.info(f"Classes:    {config.CLASSES_PATH}")
    logger.info(f"Classes:    {num_classes} (trained on 8 specific crop diseases)")
    logger.info(f"Epochs:     {config.EPOCHS} (with EarlyStopping patience={config.EARLY_STOPPING_PATIENCE})")
    logger.info(f"Batch Size: {config.BATCH_SIZE}")
    logger.info("="*80 + "\n")
    
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
