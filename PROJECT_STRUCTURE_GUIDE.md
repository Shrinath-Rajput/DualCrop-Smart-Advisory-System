# DualCrop Smart Advisory System - Project Structure & Pipeline Guide

## 📁 Current Project Structure

```
DualCrop Smart Advisory System/
├── app.py                          # ⚠️ EMPTY - Flask/Streamlit app
├── README.md
├── requirements.txt
│
├── artifacts/                      # Model & training data storage
│   ├── history.json               # Training history
│   ├── model.h5                   # Trained ML model
│   ├── test/                      # Test dataset split
│   │   ├── brinjal_Healthy Leaf/
│   │   ├── Grapes_Grape/
│   │   ├── Grapes_Grape___Black_rot/
│   │   ├── Grapes_Grape___Esca_(Black_Measles)/
│   │   ├── Grapes_Grape___healthy/
│   │   └── Grapes_Grape___Leaf_blight_(Isariopsis_Leaf_Spot)/
│   │
│   └── train/                     # Train dataset split
│       ├── brinjal_Healthy Leaf/
│       └── [same crop disease classes]
│
├── Dataset/                        # Raw source data
│   ├── __init__.py
│   ├── brinjal/
│   │   └── Healthy Leaf/
│   └── Grapes/
│       ├── Grape/
│       ├── Grape___Black_rot/
│       ├── Grape___Esca_(Black_Measles)/
│       ├── Grape___healthy/
│       └── Grape___Leaf_blight_(Isariopsis_Leaf_Spot)/
│
├── logs/                           # Application logs
│
├── src/                            # Source code
│   ├── __init__.py
│   ├── exception.py               # Custom exception handling
│   ├── logger.py                  # Logging configuration
│   ├── utlis.py                   # Utility functions
│   │
│   ├── Components/                # Reusable ML components
│   │   ├── __init__.py
│   │   ├── data_ingestion.py     # ✅ Splits Dataset into train/test
│   │   ├── data_transformation.py # ✅ Data augmentation & preprocessing
│   │   └── model_trainer.py       # ✅ Model training with transfer learning
│   │
│   └── pipeline/                  # Main execution pipelines
│       ├── __init__.py
│       ├── train_pipeline.py      # ⚠️ EMPTY - orchestrates training
│       └── predict_pipeline.py    # ✅ Handles model predictions
│
├── templates/                      # Web UI templates (HTML/CSS)
│
└── venv310/                        # Python virtual environment


```

---

## 🔄 Complete ML Pipeline Flow

### **Phase 1: Data Preparation (First Time Setup)**

```
Dataset/ (raw data)
    ↓
[data_ingestion.py]
    ├─ Reads from Dataset/ folder
    ├─ Splits images: 80% train, 20% test
    └─ Creates class folders: "{crop}_{disease}"
    ↓
artifacts/train/  &  artifacts/test/
```

**Code in `data_ingestion.py`:**
- `DataIngestionConfig`: Defines paths for train/test split
- `DataIngestion.initiate_data_ingestion()`: Main method
  - Iterates through `Dataset/` folder
  - Processes each crop and disease class
  - Splits and copies images to `artifacts/train/` and `artifacts/test/`

---

### **Phase 2: Data Transformation & Model Training**

```
artifacts/train/  &  artifacts/test/
    ↓
[data_transformation.py]
    ├─ Validates directories
    ├─ Creates ImageDataGenerator (with augmentation for training)
    └─ Loads images in batches (224x224, batch_size=32)
    ↓
[model_trainer.py]
    ├─ Builds transfer learning model (MobileNetV2 or ResNet50)
    ├─ Trains with callbacks (EarlyStopping, ModelCheckpoint, etc.)
    └─ Saves model & training history
    ↓
artifacts/model.h5  &  artifacts/history.json
```

**Components:**
- `data_transformation.py`: 
  - `get_data_transformation()`: Creates augmented data generators
  - `initiate_data_transformation()`: Loads batches from directories
  
- `model_trainer.py`:
  - `build_model()`: Creates MobileNetV2/ResNet50 with custom top layers
  - `initiate_model_trainer()`: Trains model with validation

---

### **Phase 3: Prediction**

```
User uploads image
    ↓
[predict_pipeline.py]
    ├─ Loads model.h5
    ├─ Loads class names from artifacts/train/
    ├─ Preprocesses image (224x224, normalize)
    └─ Returns: (predicted_class, confidence_score)
    ↓
Prediction Result
```

**Current code in `predict_pipeline.py`:**
```python
PredictPipeline()
├─ load_class_names() → Gets classes from artifacts/train/
├─ predict(img_path) → Returns (class_name, confidence)
```

---

## ⚠️ Missing / Empty Files To Complete

### **1. `train_pipeline.py` - MUST IMPLEMENT**
Should orchestrate the complete training workflow:

```python
from src.Components.data_ingestion import DataIngestion
from src.Components.data_transformation import DataTransformation
from src.Components.model_trainer import ModelTrainer

class TrainPipeline:
    def run(self):
        # Step 1: Ingest data
        data_ingestion = DataIngestion()
        train_path, test_path = data_ingestion.initiate_data_ingestion()
        
        # Step 2: Transform data
        data_transformation = DataTransformation(train_path, test_path)
        train_data, test_data = data_transformation.initiate_data_transformation()
        
        # Step 3: Train model
        model_trainer = ModelTrainer()
        model_trainer.initiate_model_trainer(train_data, test_data)
        
        return "Training completed!"
```

---

### **2. `app.py` - MUST IMPLEMENT**
Web interface for predictions:

```python
from flask import Flask, render_template, request, jsonify
from src.pipeline.predict_pipeline import PredictPipeline

app = Flask(__name__)
predict_pipeline = PredictPipeline()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    file.save('temp_image.jpg')
    
    predicted_class, confidence = predict_pipeline.predict('temp_image.jpg')
    
    return jsonify({
        'class': predicted_class,
        'confidence': float(confidence)
    })

if __name__ == '__main__':
    app.run(debug=True)
```

---

### **3. `templates/index.html` - Create this**
Basic UI for image upload and prediction display

---

## ✅ What's Working

| Component | Status | Notes |
|-----------|--------|-------|
| `data_ingestion.py` | ✅ Complete | Splits Dataset into train/test |
| `data_transformation.py` | ✅ Complete | Image preprocessing & augmentation |
| `model_trainer.py` | ✅ Complete | Transfer learning model |
| `predict_pipeline.py` | ✅ Complete | Prediction inference |
| `train_pipeline.py` | ❌ Empty | Needs orchestration code |
| `app.py` | ❌ Empty | Needs Flask/web interface |

---

## 📋 Quick Start Guide

### **Step 1: First Time Training**
```bash
# Run this once to prepare data and train model
python -m src.pipeline.train_pipeline
```

### **Step 2: Run Web Application**
```bash
# Start Flask server
python app.py
# Visit http://localhost:5000
```

### **Step 3: Make Predictions**
```python
from src.pipeline.predict_pipeline import PredictPipeline

predictor = PredictPipeline()
class_name, confidence = predictor.predict('path/to/image.jpg')
print(f"Prediction: {class_name} ({confidence:.2%})")
```

---

## 🔧 Configuration Files Needed

Create `config.yaml` (optional but recommended):
```yaml
data_config:
  dataset_path: "Dataset"
  train_split: 0.8
  target_size: [224, 224]
  batch_size: 32

model_config:
  model_type: "mobilenetv2"  # or "resnet50"
  epochs: 20
  learning_rate: 0.001
  early_stopping_patience: 5

app_config:
  debug: true
  port: 5000
```

---

## 📊 Training Data Structure Details

**Expected Format in `Dataset/` folder:**
```
Dataset/
├── brinjal/
│   └── Healthy Leaf/
│       ├── image1.jpg
│       ├── image2.jpg
│       └── ...
└── Grapes/
    ├── Grape/
    │   ├── image1.jpg
    │   └── ...
    ├── Grape___Black_rot/
    ├── Grape___Esca_(Black_Measles)/
    ├── Grape___healthy/
    └── Grape___Leaf_blight_(Isariopsis_Leaf_Spot)/
```

After `data_ingestion.py` runs, `artifacts/train/` will contain:
```
artifacts/train/
├── brinjal_Healthy Leaf/
├── Grapes_Grape/
├── Grapes_Grape___Black_rot/
├── Grapes_Grape___Esca_(Black_Measles)/
├── Grapes_Grape___healthy/
└── Grapes_Grape___Leaf_blight_(Isariopsis_Leaf_Spot)/
```

---

## 🎯 Next Actions

1. **Implement `train_pipeline.py`** - orchestrates all 3 components
2. **Implement `app.py`** - Flask web server with prediction endpoint
3. **Create `templates/index.html`** - upload form and results display
4. **Update `requirements.txt`** - ensure all dependencies are listed
5. **Test complete pipeline** - data ingestion → training → prediction

Would you like me to implement any of these components?
