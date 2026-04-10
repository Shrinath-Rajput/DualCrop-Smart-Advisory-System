import os
import traceback
from src.pipeline.predict_pipeline import PredictPipeline

# 🔥 HuggingFace UI
import gradio as gr

# ================= INIT ================= #

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ================= PIPELINE ================= #

predict_pipeline = None

def get_pipeline():
    global predict_pipeline
    if predict_pipeline is None:
        try:
            predict_pipeline = PredictPipeline()
            print("✅ Model Loaded Successfully")
        except Exception as e:
            print("❌ Model Load Error:", e)
            traceback.print_exc()
            predict_pipeline = None
    return predict_pipeline


# ================= GRADIO FUNCTION ================= #

def gradio_predict(img):
    try:
        pipeline = get_pipeline()

        if pipeline is None:
            return "❌ Model not loaded"

        # save temp image
        temp_path = "temp.jpg"
        img.save(temp_path)

        result = pipeline.predict(temp_path)

        prediction = str(result[0])
        confidence = float(result[1])

        # cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return f"🌿 Prediction: {prediction}\n📊 Confidence: {confidence:.2f}"

    except Exception as e:
        traceback.print_exc()
        return f"❌ Error: {str(e)}"


# ================= LAUNCH ================= #

demo = gr.Interface(
    fn=gradio_predict,
    inputs=gr.Image(type="pil"),
    outputs="text",
    title="🌾 DualCrop Smart Advisory System",
    description="Upload crop image to detect disease"
)

demo.launch()