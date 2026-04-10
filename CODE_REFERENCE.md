# 🌾 DualCrop Smart Advisory System - Complete Code Reference

## ✅ Implemented Components

### 1. **Training Pipeline** (`src/pipeline/train_pipeline.py`)
**Status: ✅ COMPLETE**

Orchestrates the complete ML workflow:
```
Dataset/ → Data Ingestion → artifacts/train & test/ 
           → Data Transformation → Preprocessed Data
           → Model Training → artifacts/model.h5
```

**Key Methods:**
- `run_step_1_data_ingestion()` - Splits raw dataset into 80% train, 20% test
- `run_step_2_data_transformation()` - Preprocessing & augmentation
- `run_step_3_model_training()` - Transfer learning model training
- `run()` - Execute complete pipeline

**Usage:**
```bash
cd "DualCrop Smart Advisory System"
.\venv310\Scripts\activate
python -m src.pipeline.train_pipeline
```

---

### 2. **Prediction Pipeline** (`src/pipeline/predict_pipeline.py`)
**Status: ✅ COMPLETE**

Inference on new images using trained model:
```
Image Upload → Load Model → Preprocess Image 
            → Generate Prediction → Return (class, confidence)
```

**Key Methods:**
- `__init__()` - Load model and class names
- `load_class_names()` - Auto-detect classes from artifacts/train/
- `predict(img_path)` - Get prediction for single image

**Usage:**
```python
from src.pipeline.predict_pipeline import PredictPipeline

pipeline = PredictPipeline()
class_name, confidence = pipeline.predict('path/to/image.jpg')
print(f"Predicted: {class_name} ({confidence:.2%})")
```

---

### 3. **Web Application** (`app.py`)
**Status: ✅ COMPLETE**

Flask web server with REST API and UI:

**Endpoints:**
```
GET  /                    - Home page (UI)
GET  /api/info           - App info
GET  /api/classes        - Available disease classes
GET  /api/health         - Health check
POST /api/predict        - Single image prediction
POST /api/predict-multiple - Multiple image predictions
```

**Features:**
- Drag & drop image upload
- Real-time prediction
- Error handling
- File size validation (max 16MB)
- Comprehensive logging

**Usage:**
```bash
cd "DualCrop Smart Advisory System"
.\venv310\Scripts\activate
python app.py
# Visit: http://localhost:5000
```

---

### 4. **Web Interface** (`templates/index.html`)
**Status: ✅ COMPLETE**

Modern, responsive UI with:
- Drag & drop file upload
- Image preview
- Real-time prediction results
- Confidence score display
- Error handling
- Mobile responsive design

**Features:**
- Beautiful gradient background
- Animated loading spinner
- Smooth transitions
- Intuitive controls
- Class statistics

---

### 5. **Test Suite** (`test_predict_pipeline.py`)
**Status: ✅ COMPLETE**

Comprehensive testing for prediction pipeline:

**Features:**
- Tests all images in artifacts/test/
- Calculates accuracy per class
- Overall accuracy metrics
- Detailed logging
- Per-image confidence tracking

**Usage:**
```bash
cd "DualCrop Smart Advisory System"
.\venv310\Scripts\activate
python test_predict_pipeline.py
```

---

## 📊 Component Overview

| Component | File | Status | Purpose |
|-----------|------|--------|---------|
| Data Ingestion | `src/Components/data_ingestion.py` | ✅ | Split Dataset into train/test |
| Data Transform | `src/Components/data_transformation.py` | ✅ | Preprocessing & augmentation |
| Model Trainer | `src/Components/model_trainer.py` | ✅ | Train MobileNetV2 model |
| Training Pipeline | `src/pipeline/train_pipeline.py` | ✅ | Orchestrate training workflow |
| Prediction Pipeline | `src/pipeline/predict_pipeline.py` | ✅ | Inference on new images |
| Web App | `app.py` | ✅ | Flask web server |
| Web UI | `templates/index.html` | ✅ | Interactive web interface |
| Tests | `test_predict_pipeline.py` | ✅ | Test suite & metrics |

---

## 🚀 Quick Start Guide

### Step 1: Setup Environment
```bash
cd "D:\e drive\Only_Project\DualCrop Smart Advisory System"
.\venv310\Scripts\activate
```

### Step 2: Train Model (First Time Only)
```bash
python -m src.pipeline.train_pipeline
```

This will:
- ✅ Split Dataset/ into train/test sets
- ✅ Preprocess and augment images
- ✅ Train MobileNetV2 model
- ✅ Save model.h5 and history.json

**Expected Output:**
```
╔════════════════════════════════════════════════════════════════╗
║  🌾 DUALCROP SMART ADVISORY SYSTEM 🌾                          ║
║  COMPLETE TRAINING PIPELINE                                   ║
╚════════════════════════════════════════════════════════════════╝

📊 STEP 1: DATA INGESTION
   ✅ DATA INGESTION COMPLETED
   📁 Train data path: artifacts/train
   📁 Test data path: artifacts/test

🔄 STEP 2: DATA TRANSFORMATION
   ✅ DATA TRANSFORMATION COMPLETED
   📊 Number of classes: 6
   🏷️  Classes: ['Grapes_Grape___Black_rot', ...]

🤖 STEP 3: MODEL TRAINING
   ✅ MODEL TRAINING COMPLETED
   💾 Model saved: artifacts/model.h5
```

### Step 3: Test Predictions
```bash
python test_predict_pipeline.py
```

Tests all images in artifacts/test/ and shows accuracy metrics.

### Step 4: Start Web Server
```bash
python app.py
```

Open browser: http://localhost:5000

---

## 📁 Complete Directory Structure

```
DualCrop Smart Advisory System/
│
├── 🤖 PIPELINES
│   ├── src/pipeline/train_pipeline.py      ✅ Complete
│   └── src/pipeline/predict_pipeline.py    ✅ Complete
│
├── 🔧 COMPONENTS
│   ├── src/Components/data_ingestion.py       ✅ Complete
│   ├── src/Components/data_transformation.py  ✅ Complete
│   └── src/Components/model_trainer.py        ✅ Complete
│
├── 🌐 WEB SERVER
│   ├── app.py                          ✅ Complete
│   └── templates/index.html            ✅ Complete
│
├── 📖 UTILITIES
│   ├── src/logger.py
│   ├── src/exception.py
│   └── src/utlis.py
│
├── 📊 DATA
│   ├── Dataset/                        (Raw data)
│   └── artifacts/
│       ├── train/                      (Train dataset after split)
│       ├── test/                       (Test dataset after split)
│       ├── model.h5                    (Trained model)
│       └── history.json                (Training history)
│
├── 🧪 TESTING
│   ├── test_predict_pipeline.py        ✅ Complete
│   └── test_results.txt                (Test output)
│
├── 📝 DOCUMENTATION
│   ├── README.md
│   ├── PROJECT_STRUCTURE_GUIDE.md
│   └── requirements.txt
│
└── 🐍 ENVIRONMENT
    └── venv310/                        (Virtual environment)
```

---

## 🎯 Workflow

### 1️⃣ **Training Phase** (One-time)
```
python -m src.pipeline.train_pipeline
│
├─ Load Dataset/
├─ Split 80% train, 20% test → artifacts/
├─ Preprocess images (224×224, normalize)
├─ Apply augmentation (rotation, flip, zoom)
├─ Train MobileNetV2 model
├─ Save model → artifacts/model.h5
└─ Save history → artifacts/history.json
```

### 2️⃣ **Prediction Phase** (Per request)
```
User uploads image
│
├─ app.py receives file
├─ predict_pipeline.py loads model
├─ Preprocess image (224×224, normalize)
├─ Model inference
├─ Return (disease_class, confidence)
└─ Display results in UI
```

### 3️⃣ **Testing Phase** (Validation)
```
python test_predict_pipeline.py
│
├─ Load artifacts/test/ images
├─ Predict on each image
├─ Compare with true label
├─ Calculate accuracy per class
└─ Generate accuracy report
```

---

## 📊 Model Details

**Architecture:** MobileNetV2 with custom top layers
- **Base Model:** MobileNetV2 (ImageNet pretrained, frozen)
- **Input:** 224×224×3 images
- **Top Layers:**
  - GlobalAveragePooling2D
  - Dense(256, relu) + Dropout(0.5)
  - Dense(128, relu) + Dropout(0.3)
  - Dense(num_classes, softmax)

**Training Configuration:**
- **Optimizer:** Adam (lr=0.001)
- **Loss:** Categorical Crossentropy
- **Epochs:** 20
- **Batch Size:** 32
- **Callbacks:**
  - EarlyStopping (patience=5)
  - ReduceLROnPlateau (factor=0.5)
  - ModelCheckpoint (save best)

---

## ✅ Checklist

- [x] Data ingestion component
- [x] Data transformation component
- [x] Model trainer component
- [x] Training pipeline
- [x] Prediction pipeline
- [x] Flask web server
- [x] Web UI (HTML/CSS/JS)
- [x] Test suite
- [x] Error handling
- [x] Logging system
- [x] Documentation

---

## 🔗 API Examples

### Get Classes
```bash
curl http://localhost:5000/api/classes
```

### Single Image Prediction
```bash
curl -X POST -F "file=@image.jpg" http://localhost:5000/api/predict
```

### Health Check
```bash
curl http://localhost:5000/api/health
```

---

## 🐛 Troubleshooting

**Error: Model not found**
```
→ Run training: python -m src.pipeline.train_pipeline
```

**Error: No classes found**
```
→ Verify artifacts/train/ exists and has class folders
```

**Error: File too large**
```
→ Max file size is 16MB, reduce image size
```

**Error: Port 5000 in use**
```bash
# Change port in app.py line ~295
app.run(port=8000, debug=True)
```

---

## 📈 Next Steps

1. **Deploy to Cloud** (AWS/Azure/GCP)
2. **Add batch processing** for multiple images
3. **Implement caching** for faster predictions
4. **Add advisory recommendations** based on disease
5. **Mobile app** (React Native/Flutter)
6. **Database integration** for results tracking

---

**Status:** All core components implemented and tested ✅
**Ready for:** Production deployment
