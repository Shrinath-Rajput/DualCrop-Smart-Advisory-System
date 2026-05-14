import os
import sys
import json
from dataclasses import dataclass

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import tensorflow as tf
from tensorflow.keras.applications import EfficientNetB0
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

from src.exception import CustomException
from src.logger import logging


@dataclass
class ModelTrainerConfig:
    model_path: str = os.path.join("artifacts", "crop_disease_model.h5")
    class_names_path: str = os.path.join("artifacts", "class_names.json")
    history_path: str = os.path.join("artifacts", "history.json")
    epochs: int = 20
    batch_size: int = 32
    learning_rate: float = 0.001


class ModelTrainer:
    def __init__(self):
        self.config = ModelTrainerConfig()
        self.model = None
        self.history = None

    def build_model(self, num_classes):
        """
        Build EfficientNetB0 transfer learning model for disease classification
        EfficientNetB0 is lightweight yet effective for disease detection
        """
        try:
            logging.info(f"🏗️  Building EfficientNetB0 model with {num_classes} disease classes")

            # Load EfficientNetB0 base model pre-trained on ImageNet
            base_model = EfficientNetB0(
                weights='imagenet',
                include_top=False,
                input_shape=(224, 224, 3)
            )

            # Freeze base model layers for transfer learning
            base_model.trainable = False
            logging.info("   ✅ Base model layers frozen for transfer learning")

            # Build custom top layers for disease classification
            x = base_model.output
            x = GlobalAveragePooling2D()(x)
            x = Dense(256, activation='relu', name='dense_256')(x)
            x = Dropout(0.5)(x)
            x = Dense(128, activation='relu', name='dense_128')(x)
            x = Dropout(0.3)(x)
            
            # Output layer for multi-class disease classification
            output = Dense(num_classes, activation='softmax', name='disease_output')(x)

            # Create complete model
            model = Model(inputs=base_model.input, outputs=output)

            # Compile model with appropriate loss for multi-class classification
            optimizer = Adam(learning_rate=self.config.learning_rate)
            model.compile(
                optimizer=optimizer,
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )

            logging.info("✅ Model compiled successfully")
            logging.info("   • Optimizer: Adam (lr=0.001)")
            logging.info("   • Loss: Categorical Crossentropy")
            logging.info("   • Metrics: Accuracy")
            
            return model

        except Exception as e:
            raise CustomException(e, sys)

    def get_callbacks(self):
        """Create training callbacks for optimal model training"""
        try:
            callbacks = [
                EarlyStopping(
                    monitor='val_loss',
                    patience=5,
                    restore_best_weights=True,
                    verbose=1
                ),
                ReduceLROnPlateau(
                    monitor='val_loss',
                    factor=0.5,
                    patience=3,
                    min_lr=1e-7,
                    verbose=1
                ),
                ModelCheckpoint(
                    self.config.model_path,
                    monitor='val_accuracy',
                    save_best_only=True,
                    verbose=1
                )
            ]
            logging.info("✅ Callbacks configured")
            return callbacks
        except Exception as e:
            raise CustomException(e, sys)

    def save_class_names(self, class_indices):
        """Save class names mapping to JSON file"""
        try:
            # class_indices from flow_from_directory: {'class_name': index}
            # Reverse to: {index: 'class_name'}
            class_names_dict = {str(v): k for k, v in class_indices.items()}
            
            os.makedirs(os.path.dirname(self.config.class_names_path), exist_ok=True)
            with open(self.config.class_names_path, 'w') as f:
                json.dump(class_names_dict, f, indent=4)
            
            logging.info(f"✅ Class names saved to {self.config.class_names_path}")
            return class_names_dict
            
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_model_trainer(self, train_data, test_data):
        """Train the EfficientNetB0 disease classification model"""
        try:
            logging.info("\n" + "=" * 70)
            logging.info("🤖 STARTING DISEASE CLASSIFICATION MODEL TRAINING")
            logging.info("=" * 70)

            # Get number of disease classes
            num_classes = len(train_data.class_indices)
            logging.info(f"📊 Total disease classes to classify: {num_classes}")
            logging.info(f"🏷️  Classes: {list(train_data.class_indices.keys())}")

            # Build model
            self.model = self.build_model(num_classes)
            
            # Print model summary
            logging.info("\n📋 Model Architecture Summary:")
            self.model.summary()

            # Get callbacks
            callbacks = self.get_callbacks()

            # Train model
            logging.info(f"\n⏳ Starting training for {self.config.epochs} epochs...")
            logging.info(f"   • Batch size: {self.config.batch_size}")
            logging.info(f"   • Training samples: {len(train_data) * self.config.batch_size}")
            
            self.history = self.model.fit(
                train_data,
                validation_data=test_data,
                epochs=self.config.epochs,
                callbacks=callbacks,
                verbose=1
            )

            # Save model
            os.makedirs(os.path.dirname(self.config.model_path), exist_ok=True)
            self.model.save(self.config.model_path)
            logging.info(f"\n✅ Model saved to: {self.config.model_path}")

            # Save class names
            self.save_class_names(train_data.class_indices)

            # Save training history
            history_dict = {
                'accuracy': [float(x) for x in self.history.history.get('accuracy', [])],
                'loss': [float(x) for x in self.history.history.get('loss', [])],
                'val_accuracy': [float(x) for x in self.history.history.get('val_accuracy', [])],
                'val_loss': [float(x) for x in self.history.history.get('val_loss', [])]
            }
            
            os.makedirs(os.path.dirname(self.config.history_path), exist_ok=True)
            with open(self.config.history_path, 'w') as f:
                json.dump(history_dict, f, indent=4)
            logging.info(f"✅ Training history saved to: {self.config.history_path}")

            # Evaluate on test data
            logging.info("\n📊 Evaluating model on test dataset...")
            test_loss, test_accuracy = self.model.evaluate(test_data, verbose=0)
            logging.info(f"   • Test Loss: {test_loss:.4f}")
            logging.info(f"   • Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")

            logging.info("\n" + "=" * 70)
            logging.info("✅ MODEL TRAINING COMPLETED SUCCESSFULLY!")
            logging.info("=" * 70)
            logging.info(f"\n📁 Saved Artifacts:")
            logging.info(f"   • Model: {self.config.model_path}")
            logging.info(f"   • Class Names: {self.config.class_names_path}")
            logging.info(f"   • History: {self.config.history_path}")

            return self.model

        except Exception as e:
            raise CustomException(e, sys)


if __name__ == "__main__":
    try:
        from src.Components.data_ingestion import DataIngestion
        from src.Components.data_transformation import DataTransformation

        logging.info("\n" + "=" * 70)
        logging.info("STARTING COMPLETE ML PIPELINE")
        logging.info("=" * 70)

        # Step 1: Data Ingestion
        logging.info("\n📊 STEP 1: DATA INGESTION")
        ingestion = DataIngestion()
        train_path, test_path = ingestion.initiate_data_ingestion()

        # Step 2: Data Transformation
        logging.info("\n🔄 STEP 2: DATA TRANSFORMATION")
        transformation = DataTransformation(train_dir=train_path, test_dir=test_path)
        train_data, test_data = transformation.initiate_data_transformation()

        # Step 3: Model Training
        logging.info("\n🤖 STEP 3: MODEL TRAINING")
        trainer = ModelTrainer()
        model = trainer.initiate_model_trainer(train_data, test_data)

        logging.info("\n" + "=" * 70)
        logging.info("✅ COMPLETE ML PIPELINE EXECUTED SUCCESSFULLY!")
        logging.info("=" * 70)

    except Exception as e:
        logging.error(f"❌ Pipeline Error: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        from src.Components.data_ingestion import DataIngestion
        from src.Components.data_transformation import DataTransformation

        logging.info("\n" + "=" * 60)
        logging.info("STARTING COMPLETE ML PIPELINE")
        logging.info("=" * 60)

        # Step 1: Data Ingestion
        logging.info("\n STEP 1: DATA INGESTION")
        ingestion = DataIngestion()
        train_path, test_path = ingestion.initiate_data_ingestion()

        # Step 2: Data Transformation
        logging.info("\n STEP 2: DATA TRANSFORMATION")
        transformation = DataTransformation(train_dir=train_path, test_dir=test_path)
        train_data, test_data = transformation.initiate_data_transformation()

        # Step 3: Model Training
        logging.info("\n STEP 3: MODEL TRAINING")
        trainer = ModelTrainer()
        model = trainer.initiate_model_trainer(train_data, test_data)

        logging.info("\n" + "=" * 60)
        logging.info(" COMPLETE ML PIPELINE EXECUTED SUCCESSFULLY!")
        logging.info("=" * 60)

    except Exception as e:
        logging.error(f" Pipeline Error: {str(e)}")
        raise