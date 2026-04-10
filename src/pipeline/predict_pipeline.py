import os
import sys
import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import load_model

from src.exception import CustomException
from src.logger import logging


class PredictPipeline:
    def __init__(self):
        try:
            logging.info("🚀 Initializing Prediction Pipeline")

            self.model_path = os.path.join("artifacts", "model.h5")

            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model not found at {self.model_path}")

            self.model = load_model(self.model_path)
            print("✅ Model Loaded Successfully")

            # 🔥 AUTO FIX → 6 classes (from your model output)
            self.class_names = [f"Class_{i}" for i in range(6)]

        except Exception as e:
            print("❌ Init Error:", e)
            raise CustomException(e, sys)

    def preprocess_image(self, img_path):
        try:
            img = image.load_img(img_path, target_size=(224, 224))
            img_array = image.img_to_array(img)

            img_array = img_array / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            return img_array

        except Exception as e:
            raise CustomException(e, sys)

    def predict(self, img_path):
        try:
            if not os.path.exists(img_path):
                return "Image Not Found", 0.0

            processed_img = self.preprocess_image(img_path)

            preds = self.model.predict(processed_img, verbose=0)

            print("DEBUG shape:", preds.shape)

            predicted_index = int(np.argmax(preds[0]))
            confidence = float(np.max(preds[0]))

            # 🔥 SAFE
            if predicted_index < len(self.class_names):
                predicted_class = self.class_names[predicted_index]
            else:
                predicted_class = f"Unknown_{predicted_index}"

            return predicted_class, confidence

        except Exception as e:
            print("🔥 Prediction Error:", e)
            return "Prediction_Error", 0.0


# 🔥 TEST
if __name__ == "__main__":
    pipeline = PredictPipeline()

    test_img = "test.jpg"

    if os.path.exists(test_img):
        result, conf = pipeline.predict(test_img)
        print(result, conf)
    else:
        print("⚠️ Test image not found")