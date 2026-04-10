import os
import sys
import numpy as np
import cv2
import pickle

from src.exception import CustomException
from src.logger import logging


class PredictPipeline:
    def __init__(self):
        try:
            logging.info("🚀 Initializing Prediction Pipeline")

            # 👉 CHANGE: use .pkl model instead of .h5
            self.model_path = os.path.join("artifacts", "model.pkl")

            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model not found at {self.model_path}")

            with open(self.model_path, "rb") as f:
                self.model = pickle.load(f)

            print("✅ Model Loaded Successfully")

            self.class_names = [f"Class_{i}" for i in range(6)]

        except Exception as e:
            print("❌ Init Error:", e)
            raise CustomException(e, sys)

    def preprocess_image(self, img_path):
        try:
            img = cv2.imread(img_path)

            if img is None:
                raise ValueError("Image not loaded")

            img = cv2.resize(img, (224, 224))
            img = img / 255.0

            img = img.flatten()   # 👈 sklearn model ला flat input लागतो

            return np.array([img])

        except Exception as e:
            raise CustomException(e, sys)

    def predict(self, img_path):
        try:
            if not os.path.exists(img_path):
                return "Image Not Found", 0.0

            processed_img = self.preprocess_image(img_path)

            preds = self.model.predict(processed_img)

            predicted_index = int(preds[0])
            confidence = 0.95  # dummy confidence (since sklearn)

            if predicted_index < len(self.class_names):
                predicted_class = self.class_names[predicted_index]
            else:
                predicted_class = f"Unknown_{predicted_index}"

            return predicted_class, confidence

        except Exception as e:
            print("🔥 Prediction Error:", e)
            return "Prediction_Error", 0.0