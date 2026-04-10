import os
import sys
import json
from dataclasses import dataclass

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2, ResNet50
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint

from src.exception import CustomException
from src.logger import logging


@dataclass
class ModelTrainerConfig:
    model_path: str = os.path.join("artifacts", "model.h5")
    history_path: str = os.path.join("artifacts", "history.json")
    epochs: int = 20
    batch_size: int = 32
    learning_rate: float = 0.001
    model_type: str = "mobilenetv2"  # 'mobilenetv2' or 'resnet50'


class ModelTrainer:
    def __init__(self):
        self.config = ModelTrainerConfig()
        self.model = None
        self.history = None

    def build_model(self, num_classes):
        """Build transfer learning model for crop disease classification"""
        try:
            logging.info(f"Building {self.config.model_type} model with {num_classes} classes")

            # Load base model
            if self.config.model_type.lower() == "resnet50":
                base_model = ResNet50(
                    weights='imagenet',
                    include_top=False,
                    input_shape=(224, 224, 3)
                )
            else:  # default MobileNetV2
                base_model = MobileNetV2(
                    weights='imagenet',
                    include_top=False,
                    input_shape=(224, 224, 3)
                )

            # Freeze base model layers
            base_model.trainable = False
            logging.info(" Base model layers frozen")

            # Add custom top layers
            x = base_model.output
            x = GlobalAveragePooling2D()(x)
            x = Dense(256, activation='relu')(x)
            x = Dropout(0.5)(x)
            x = Dense(128, activation='relu')(x)
            x = Dropout(0.3)(x)
            output = Dense(num_classes, activation='softmax')(x)

            model = Model(inputs=base_model.input, outputs=output)

            # Compile model
            optimizer = Adam(learning_rate=self.config.learning_rate)
            model.compile(
                optimizer=optimizer,
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )

            logging.info(" Model compiled successfully")
            return model

        except Exception as e:
            raise CustomException(e, sys)

    def get_callbacks(self):
        """Create training callbacks"""
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
            logging.info(" Callbacks configured")
            return callbacks
        except Exception as e:
            raise CustomException(e, sys)

    def initiate_model_trainer(self, train_data, test_data):
        """Train the model"""
        try:
            logging.info("=" * 60)
            logging.info("STARTING MODEL TRAINING")
            logging.info("=" * 60)

            # Get number of classes
            num_classes = len(train_data.class_indices)
            logging.info(f"Number of disease classes: {num_classes}")
            logging.info(f"Classes: {list(train_data.class_indices.keys())}")

            # Build model
            self.model = self.build_model(num_classes)
            
            # Print model summary
            logging.info("Model Architecture:")
            self.model.summary()

            # Get callbacks
            callbacks = self.get_callbacks()

            # Train model
            logging.info(f"\n Training starting for {self.config.epochs} epochs...")
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
            logging.info(f" Model saved to: {self.config.model_path}")

            # Save training history
            history_dict = {
                'accuracy': [float(x) for x in self.history.history.get('accuracy', [])],
                'loss': [float(x) for x in self.history.history.get('loss', [])],
                'val_accuracy': [float(x) for x in self.history.history.get('val_accuracy', [])],
                'val_loss': [float(x) for x in self.history.history.get('val_loss', [])]
            }
            
            with open(self.config.history_path, 'w') as f:
                json.dump(history_dict, f, indent=4)
            logging.info(f" Training history saved to: {self.config.history_path}")

            # Evaluate on test data
            logging.info("\n Evaluating model on test data...")
            test_loss, test_accuracy = self.model.evaluate(test_data, verbose=0)
            logging.info(f" Test Loss: {test_loss:.4f}")
            logging.info(f" Test Accuracy: {test_accuracy:.4f} ({test_accuracy*100:.2f}%)")

            logging.info("=" * 60)
            logging.info(" MODEL TRAINING COMPLETED!")
            logging.info("=" * 60)

            return self.model

        except Exception as e:
            raise CustomException(e, sys)


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