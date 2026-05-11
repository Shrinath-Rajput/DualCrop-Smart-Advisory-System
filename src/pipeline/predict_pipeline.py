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

            # Load class names dynamically from training directory
            train_dir = os.path.join("artifacts", "train")
            if os.path.exists(train_dir):
                # Get class names from directory structure (sorted alphabetically, same as flow_from_directory)
                self.class_names = sorted([
                    d for d in os.listdir(train_dir)
                    if os.path.isdir(os.path.join(train_dir, d))
                ])
                print(f"✅ Classes loaded from training data: {self.class_names}")
            else:
                # Fallback class names if train directory doesn't exist
                self.class_names = [
                    "brinjal_Healthy Leaf",
                    "Grapes_Grape",
                    "Grapes_Grape___Black_rot",
                    "Grapes_Grape___Esca_(Black_Measles)",
                    "Grapes_Grape___healthy",
                    "Grapes_Grape___Leaf_blight_(Isariopsis_Leaf_Spot)"
                ]
                print(f"⚠️  Using fallback class names: {self.class_names}")

        except Exception as e:
            print("❌ Init Error:", e)
            raise CustomException(e, sys)

    def preprocess_image(self, img_path):
        try:
            img = cv2.imread(img_path)

            if img is None:
                raise ValueError("Image not loaded")

            # Convert BGR to RGB (OpenCV reads as BGR by default)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Resize to model input size (224x224 for standard CNN models)
            img = cv2.resize(img, (224, 224))
            
            # Normalize pixel values to 0-1 range (same as training: rescale=1./255)
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

            # Get predicted class name
            if predicted_index < len(self.class_names):
                predicted_class = self.class_names[predicted_index]
            else:
                predicted_class = f"Unknown_Class_{predicted_index}"

            # Print all predictions for debugging
            print(f"\n📊 Prediction Details:")
            print(f"   Image: {img_path}")
            for idx, (class_name, prob) in enumerate(zip(self.class_names, preds[0])):
                print(f"   [{idx}] {class_name}: {prob*100:.2f}%")
            print(f"\n✅ Final Prediction: {predicted_class} ({confidence:.2f}%)\n")
            
            return predicted_class, confidence

        except Exception as e:
            print("🔥 Prediction Error:", e)
            raise CustomException(e, sys)