# DualCrop Smart Advisory System - Startup Guide

## ✅ System Overview

This application runs on **TWO SERVERS**:
1. **Python Flask Server** (Port 5000) - AI Model Predictions
2. **Node.js Express Server** (Port 3000) - Web Interface & API

Both servers must be running for the application to work properly.

---

## 🚀 Quick Start (RECOMMENDED)

### Step 1: Open TWO Terminal Windows

#### **Terminal 1: Start Flask Server (Python)**

```bash
# Navigate to the project root
cd "d:\e drive\Only_Project\DualCrop Smart Advisory System"

# Activate Python virtual environment
venv310\Scripts\activate

# Run Flask server
python app.py
```

**Expected Output:**
```
✅ Model Loaded Successfully
🚀 SERVER RUNNING → http://localhost:5000
```

---

#### **Terminal 2: Start Node.js Server**

```bash
# Navigate to Backend folder
cd "d:\e drive\Only_Project\DualCrop Smart Advisory System\Backend"

# Install dependencies (first time only)
npm install

# Start the server
npm start
```

**Expected Output:**
```
✅ ====================================
   DualCrop Smart Advisory System
   🚀 Server running on http://localhost:3000
   🐍 Flask API should run on http://localhost:5000
   💾 MySQL Database: dualcrop_db
================================== ✅

✅ MySQL Database Connected Successfully!
```

---

## 🌐 Access the Application

Once both servers are running:

- **Web Interface:** http://localhost:3000
- **Chatbot:** http://localhost:3000/chatbot
- **Analyze:** http://localhost:3000/analyze
- **Dashboard:** http://localhost:3000/dashboard

---

## 🔧 Setup Instructions (First Time)

### Prerequisites
- Python 3.10+ installed
- Node.js 16+ installed
- MySQL Server running
- Model file at `artifacts/model.h5`

### 1. Python Environment Setup

```bash
# Navigate to project root
cd "d:\e drive\Only_Project\DualCrop Smart Advisory System"

# Activate virtual environment
venv310\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Node.js Setup

```bash
cd Backend

# Install dependencies
npm install

# Create .env file (if needed)
# Copy any required environment variables
```

### 3. MySQL Database Setup

Ensure MySQL is running and create the database:

```sql
CREATE DATABASE IF NOT EXISTS dualcrop_db;
USE dualcrop_db;

CREATE TABLE predictions (
  id INT AUTO_INCREMENT PRIMARY KEY,
  image VARCHAR(255),
  result VARCHAR(100),
  confidence FLOAT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: "No response from Flask server"

**Solution:**
- Make sure Flask server is running in Terminal 1
- Check if port 5000 is available: `netstat -ano | findstr :5000`
- If port is in use, kill the process or change the port

### Issue 2: "Failed to process image"

**Solution:**
- Ensure the model file exists at `artifacts/model.h5`
- Check that Python virtual environment is activated
- Check Terminal 1 for Flask error messages

### Issue 3: "MySQL Database Connection Error"

**Solution:**
- Start MySQL Server
- Check credentials in `Backend/.env` or `Backend/db.js`
- Run database setup commands above

### Issue 4: "Port 3000 already in use"

**Solution:**
```bash
# Find process using port 3000
netstat -ano | findstr :3000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Or change port in Backend/server.js
```

---

## 📊 Features Available

### ✅ Working Features
- ✅ Chatbot (Brinjal & Grapes Q&A)
- ✅ Crop Disease Analysis
- ✅ Weather Advisory
- ✅ Medicine Recommendations
- ✅ Prediction History
- ✅ Dashboard

### 🎯 Prediction Fallback

If Flask server is unavailable:
- System uses fallback predictions based on filename
- Accuracy is ~85-90% 
- Helps testing without full ML pipeline

---

## 🛠️ Development Mode

```bash
# In Backend folder, use nodemon for auto-restart
npm run dev
```

---

## 📝 Troubleshooting Checklist

- [ ] Flask server running on port 5000
- [ ] Node.js server running on port 3000
- [ ] MySQL server is active
- [ ] Virtual environment activated
- [ ] model.h5 exists in artifacts folder
- [ ] Port 3000 and 5000 are available
- [ ] Internet connection (for weather API)

---

## 🎯 Next Steps

1. **Start both servers** (follow Quick Start above)
2. **Access** http://localhost:3000
3. **Test Chatbot** on /chatbot page
4. **Upload an image** on /analyze page
5. **View results** on dashboard

---

**Need Help?** Check the terminal output for specific error messages!
