import os
import sys
import numpy as np
import cv2
from tensorflow.keras.models import load_model

from src.exception import CustomException
from src.logger import logging


class PredictPipeline:
    def __init__(self):
        try:
            logging.info("🚀 Initializing Prediction Pipeline")

            # Load Keras model (.h5 format)
            self.model_path = os.path.join("artifacts", "model.h5")

            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model not found at {self.model_path}")

            self.model = load_model(self.model_path)

            print("✅ Model Loaded Successfully")

            # Disease classes for crop disease detection
            self.class_names = [
                "Brinjal Healthy Leaf",
                "Grapes Healthy",
                "Grapes Black Rot",
                "Grapes Esca (Black Measles)",
                "Grapes Leaf Blight",
                "Unknown"
            ]

        except Exception as e:
            print("❌ Init Error:", e)
            raise CustomException(e, sys)

    def preprocess_image(self, img_path):
        try:
            img = cv2.imread(img_path)

            if img is None:
                raise ValueError("Image not loaded")

            # Resize to model input size (224x224 for standard CNN models)
            img = cv2.resize(img, (224, 224))
            
            # Normalize pixel values to 0-1 range
            img = img / 255.0

            # Add batch dimension for model input
            return np.array([img])

        except Exception as e:
            raise CustomException(e, sys)

    def predict(self, img_path):
        try:
            if not os.path.exists(img_path):
                return "Image Not Found", 0.0

            # Preprocess the image
            processed_img = self.preprocess_image(img_path)

            # Get model predictions
            preds = self.model.predict(processed_img, verbose=0)

            # Get the predicted class index and confidence
            predicted_index = np.argmax(preds[0])
            confidence = float(np.max(preds[0])) * 100  # Convert to percentage

            if predicted_index < len(self.class_names):
                predicted_class = self.class_names[predicted_index]
            else:
                predicted_class = f"Unknown_{predicted_index}"

            print(f"✅ Prediction: {predicted_class} ({confidence:.2f}%)")
            return predicted_class, confidence

        except Exception as e:
            print("🔥 Prediction Error:", e)
            raise CustomException(e, sys)
            print("❌ Init Error:", e)
            raise CustomException(e, sys)

    def preprocess_image(self, img_path):
        try:
            img = cv2.imread(img_path)

            if img is None:
                raise ValueError("Image not loaded")

            # Resize to model input size (224x224 for standard CNN models)
            img = cv2.resize(img, (224, 224))
            
            # Normalize pixel values to 0-1 range
            img = img / 255.0

            # Add batch dimension for model input
            return np.array([img])

        except Exception as e:
            raise CustomException(e, sys)

    def predict(self, img_path):
        try:
            if not os.path.exists(img_path):
                return "Image Not Found", 0.0

            # Preprocess the image
            processed_img = self.preprocess_image(img_path)

            # Get model predictions
            preds = self.model.predict(processed_img, verbose=0)

            # Get the predicted class index and confidence
            predicted_index = np.argmax(preds[0])
            confidence = float(np.max(preds[0])) * 100  # Convert to percentage

            if predicted_index < len(self.class_names):
                predicted_class = self.class_names[predicted_index]
            else:
                predicted_class = f"Unknown_{predicted_index}"

            print(f"✅ Prediction: {predicted_class} ({confidence:.2f}%)")
            return predicted_class, confidence

        except Exception as e:
            print("🔥 Prediction Error:", e)
            raise CustomException(e, sys)
            print("🔥 Prediction Error:", e)
            return "Prediction_Error", 0.0