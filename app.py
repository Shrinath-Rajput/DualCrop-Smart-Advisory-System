import os
import traceback
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from src.pipeline.predict_pipeline import PredictPipeline

# ================= INIT ================= #

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_FILE_SIZE = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

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


# ================= HELPER ================= #

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ================= ROUTES ================= #

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/history")
def history():
    return render_template("history.html")


@app.route("/about")
def about():
    return render_template("about.html")


# ================= PREDICTION API ================= #

@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        pipeline = get_pipeline()

        if pipeline is None:
            return jsonify({"error": "Model not loaded"}), 500

        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type"}), 400

        filepath = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(file.filename))
        file.save(filepath)

        # 🔥 SAFE PREDICTION (FINAL FIX)
        result = pipeline.predict(filepath)

        prediction = str(result[0])
        confidence = float(result[1])

        # cleanup
        if os.path.exists(filepath):
            os.remove(filepath)

        return jsonify({
            "prediction": prediction,
            "confidence": confidence
        })

    except Exception as e:
        print("❌ Prediction Error:", e)
        traceback.print_exc()
        return jsonify({
            "prediction": "Error",
            "confidence": 0.0
        })


# ================= ERROR HANDLER ================= #

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404


# ================= RUN ================= #

if __name__ == "__main__":
    print("\n🚀 SERVER RUNNING → http://localhost:5000\n")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )