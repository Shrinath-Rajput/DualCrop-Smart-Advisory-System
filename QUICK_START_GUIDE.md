# QUICK START - CROP DISEASE PREDICTION (UNIFIED SYSTEM)
## Get Started in 10 Minutes

---

## 1️⃣  INSTALL (2 minutes)

```bash
# Install dependencies
pip install tensorflow keras numpy opencv-python flask

# Or from requirements file
pip install -r requirements.txt
```

**Verify installation:**
```bash
python -c "import tensorflow; print(f'TensorFlow {tensorflow.__version__}')"
python -c "import cv2; print(f'OpenCV {cv2.__version__}')"
```

---

## 2️⃣  PREPARE DATASET (3 minutes)

### Create folder structure:
```bash
mkdir -p Dataset/Brinjal_Healthy
mkdir -p Dataset/Brinjal_Little_Leaf
mkdir -p Dataset/Brinjal_Leaf_Spot
mkdir -p Dataset/Brinjal_Blight
mkdir -p Dataset/Grapes_Healthy
mkdir -p Dataset/Grapes_Black_Measles
mkdir -p Dataset/Grapes_Black_Rot
mkdir -p Dataset/Grapes_Isariopsis_Leaf_Spot
```

### Move images:
```bash
# Copy your images to appropriate folders
# Each folder needs 50-100+ images

# Example:
cp /path/to/healthy/brinjal/*.jpg Dataset/Brinjal_Healthy/
cp /path/to/diseased/brinjal/little_leaf/*.jpg Dataset/Brinjal_Little_Leaf/
cp /path/to/grapes/black_rot/*.jpg Dataset/Grapes_Black_Rot/
# ... etc
```

### Verify structure:
```bash
ls -R Dataset/
```

Expected output:
```
Dataset/
├── Brinjal_Healthy/           (100+ images)
├── Brinjal_Little_Leaf/       (50+ images)
├── Brinjal_Leaf_Spot/         (50+ images)
├── Brinjal_Blight/            (50+ images)
├── Grapes_Healthy/            (100+ images)
├── Grapes_Black_Measles/      (50+ images)
├── Grapes_Black_Rot/          (50+ images)
└── Grapes_Isariopsis_Leaf_Spot/ (50+ images)
```

---

## 3️⃣  TRAIN MODEL (✓ automatic)

```bash
python train_unified.py
```

**What happens:**
- Validates dataset ✓
- Loads images ✓
- Builds model ✓
- Trains for ~100 epochs ✓
- Saves model to `artifacts/crop_disease_model.h5` ✓
- Generates `artifacts/class_names.json` ✓

**Training output:**
```
================================================================================
UNIFIED CROP DISEASE PREDICTION - TRAINING PIPELINE
================================================================================

VALIDATING DATASET STRUCTURE
================================================================================
✓ Brinjal_Healthy                    →    120 images
✓ Brinjal_Little_Leaf                →     65 images
✓ Brinjal_Leaf_Spot                  →     58 images
✓ Brinjal_Blight                     →     52 images
✓ Grapes_Healthy                     →    110 images
✓ Grapes_Black_Measles               →     42 images
✓ Grapes_Black_Rot                   →     38 images
✓ Grapes_Isariopsis_Leaf_Spot        →     45 images
================================================================================

TRAINING UNIFIED CROP DISEASE MODEL
================================================================================

Epoch 1/100
23/23 ━━━━━━━━━━━━━━━━━━ 5s 200ms/step - loss: 2.1847 - accuracy: 0.4532 - val_loss: 1.8532 - val_accuracy: 0.6321

Epoch 2/100
...

Epoch 45/100
23/23 ━━━━━━━━━━━━━━━━━━ 1s 45ms/step - loss: 0.1234 - accuracy: 0.9834 - val_loss: 0.3212 - val_accuracy: 0.9612

✓ TRAINING COMPLETED SUCCESSFULLY
================================================================================
Model:  artifacts/crop_disease_model.h5
Classes: artifacts/class_names.json
================================================================================
```

**Training time:** ~10-60 minutes (depending on hardware)
**GPU recommended but not required**

---

## 4️⃣  TEST PREDICTION (instant)

### Option A: Command Line

```bash
python predict.py path/to/test_image.jpg
```

**Output example:**
```
================================================================================
                    CROP DISEASE PREDICTION RESULTS
================================================================================

📍 CROP: Brinjal
📊 STATUS: Diseased
📈 CONFIDENCE: 94.32%

🦠 DISEASE: Little Leaf
🔴 SEVERITY: High

📋 SYMPTOMS:
   • Leaves become abnormally small
   • Excessive branching
   • Stunted growth
   • Poor fruit development
   • Yellowing of leaves
   • Sparse foliage

💡 RECOMMENDATION: Little Leaf disease detected. Requires immediate zinc supplementation and insect vector control.

🧪 SCIENTIFIC TREATMENT:
1. Apply Zinc Sulfate (0.5%) as foliar spray 2-3 times at 10-15 day intervals
2. Or use Borax solution (0.2%) as supplement
3. Apply Imidacloprid 17.8SL (1ml/L) to control whiteflies and mites
4. Repeat spraying every 7-10 days for 4-5 weeks

🌿 ORGANIC SOLUTION:
1. Neem oil spray (5%) every 7 days to control insect vectors
2. Zinc-rich compost or vermicompost application
3. Manual removal of severely affected leaves
4. Plant spacing improvement for better air circulation
5. Companion planting with marigold to repel insects

💊 MEDICINE: Zinc Sulfate (0.5%) or Imidacloprid 17.8SL

🛡️  PREVENTION: Use disease-resistant varieties, maintain soil fertility, control vector insects early, ensure proper zinc in soil, avoid water stress

================================================================================
```

### Option B: Python Script

```python
from predict import CropDiseasePredictor

# Initialize
predictor = CropDiseasePredictor()

# Predict
result = predictor.predict('test.jpg')

# Use results
print(f"Crop: {result['crop']}")
print(f"Disease: {result['disease']}")
print(f"Confidence: {result['confidence']}%")
print(f"Status: {result['status']}")
print(f"Treatment: {result['scientific_treatment']}")
```

### Option C: API Call

```bash
# Start server
python app_api_unified.py

# In another terminal
curl -X POST -F "file=@test.jpg" http://localhost:5000/api/predict
```

**Response:**
```json
{
  "success": true,
  "crop": "Brinjal",
  "disease": "Little Leaf",
  "status": "Diseased",
  "confidence": 94.32,
  "symptoms": ["Leaves become abnormally small", "Excessive branching", ...],
  "severity": "High",
  "medicine": "Zinc Sulfate (0.5%)...",
  "treatment": "Spray zinc sulfate solution...",
  "scientific_treatment": "1. Apply Zinc Sulfate...",
  "organic_solution": "1. Neem oil spray...",
  "prevention": "Use disease-resistant varieties...",
  "timestamp": "2026-05-15T10:30:45.123456"
}
```

---

## 5️⃣  DEPLOY API (1 minute)

### Start Flask Server

```bash
python app_api_unified.py
```

Server runs on: `http://localhost:5000`

### API Endpoints

**Predict disease:**
```bash
curl -X POST -F "file=@image.jpg" http://localhost:5000/api/predict
```

**Check health:**
```bash
curl http://localhost:5000/api/health
```

**Get system info:**
```bash
curl http://localhost:5000/api/info
```

---

## 📊 UNDERSTANDING CONFIDENCE

### What does confidence mean?

```
Softmax probability for the predicted class
Range: 0% - 100%
Higher = More reliable

Examples:
- 95% confidence → Very reliable ✓✓✓
- 80% confidence → Reliable ✓✓
- 65% confidence → Medium, consult specialist ✓
- 45% confidence → Unreliable, seek expert ✗
```

### Example prediction breakdown:

```
All 8 classes with probabilities:

Brinjal_Healthy:               0.2%
Brinjal_Little_Leaf:          94.3% ← PREDICTED (highest)
Brinjal_Leaf_Spot:             3.1%
Brinjal_Blight:                0.5%
Grapes_Healthy:                0.1%
Grapes_Black_Measles:          1.2%
Grapes_Black_Rot:              0.4%
Grapes_Isariopsis_Leaf_Spot:   0.2%
────────────────
Total:                        100.0% ✓
```

---

## 🎯 NEXT STEPS

### To improve accuracy:
1. Collect more images per class (target: 100-200)
2. Ensure good image quality and variety
3. Include different lighting and angles
4. Retrain: `python train_unified.py`

### To deploy to production:
1. Use Gunicorn: `pip install gunicorn`
2. Run: `gunicorn -w 4 -b 0.0.0.0:5000 app_api_unified:app`
3. Use reverse proxy (Nginx)
4. Enable HTTPS/SSL

### To add new diseases:
1. Create new folder in Dataset/
2. Add images
3. Retrain model
4. Update disease_database.json
5. Redeploy

---

## 🐛 QUICK TROUBLESHOOTING

### Model not found?
```bash
# Train first
python train_unified.py
```

### Out of memory?
```python
# In train_unified.py, reduce:
BATCH_SIZE = 16  # was 32
```

### Low accuracy?
```bash
# Collect more images (100+ per class)
# Improve image quality
# Retrain: python train_unified.py
```

### API not responding?
```bash
# Check if running
curl http://localhost:5000/api/health

# Check if model is loaded
curl http://localhost:5000/api/info
```

---

## 📁 KEY FILES

```
Project structure:
├── train_unified.py              ← Run training
├── predict.py                    ← Run predictions
├── app_api_unified.py            ← Start API server
├── artifacts/
│   ├── crop_disease_model.h5     ← Trained model
│   └── class_names.json          ← 8 class mapping
├── disease_database.json         ← Disease information
├── Dataset/                      ← Training images
│   ├── Brinjal_Healthy/
│   ├── Brinjal_Little_Leaf/
│   ├── Brinjal_Leaf_Spot/
│   ├── Brinjal_Blight/
│   ├── Grapes_Healthy/
│   ├── Grapes_Black_Measles/
│   ├── Grapes_Black_Rot/
│   └── Grapes_Isariopsis_Leaf_Spot/
└── templates/                    ← HTML files (optional)
```

---

## 💡 TIPS

1. **Test with diverse images**: Different lighting, angles, backgrounds
2. **Monitor confidence scores**: Values < 70% should be reviewed by experts
3. **Retrain monthly**: Add new images to improve accuracy
4. **Keep database updated**: Add new disease information as discovered
5. **Use GPU for training**: 10x faster with NVIDIA GPU

---

## 📚 FULL DOCUMENTATION

For detailed information, see:
- `UNIFIED_SYSTEM_COMPLETE.md` - Complete guide
- `FIX_COMPLETE_PRODUCTION_READY.md` - What was fixed

---

## ✅ VERIFICATION CHECKLIST

After setup, verify:
- [ ] Dataset organized in 8 folders
- [ ] Model training completes
- [ ] Predictions show varying confidence (not always 50%)
- [ ] Healthy predictions work correctly
- [ ] Diseased predictions show treatment info
- [ ] API responds to requests
- [ ] No errors in logs

---

## 🚀 YOU'RE READY!

Your crop disease prediction system is now:
- ✅ Properly structured
- ✅ Using real confidence scores
- ✅ Production-ready
- ✅ Well-documented
- ✅ Easy to deploy

**Next:** Train and test!

```bash
python train_unified.py
python predict.py test.jpg
```

---

**Version**: 2.0.0 (Unified System)
**Status**: ✅ Production Ready
**Last Updated**: 2026-05-15

Need help? Check `UNIFIED_SYSTEM_COMPLETE.md` or `FIX_COMPLETE_PRODUCTION_READY.md`
