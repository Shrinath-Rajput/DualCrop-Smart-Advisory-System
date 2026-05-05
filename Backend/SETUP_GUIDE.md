# 🌾 DualCrop Smart Advisory System - Complete Setup Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Tech Stack](#tech-stack)
3. [Prerequisites](#prerequisites)
4. [Installation Steps](#installation-steps)
5. [Database Setup](#database-setup)
6. [Configuration](#configuration)
7. [Running the Application](#running-the-application)
8. [Features](#features)
9. [Troubleshooting](#troubleshooting)
10. [Project Structure](#project-structure)

---

## 🎯 Project Overview

**DualCrop Smart Advisory System** is a full-stack AI-powered agricultural technology platform that helps farmers:
- Detect crop diseases early using AI/ML
- Get weather-based crop recommendations
- Maintain a history of disease analyses
- Interact with an intelligent chatbot for agricultural advice

### Key Components:
- **Frontend**: Beautiful, responsive UI with Bootstrap 5
- **Backend**: Node.js/Express API server
- **ML Engine**: Python Flask with TensorFlow models
- **Database**: MySQL for data persistence

---

## 🛠️ Tech Stack

### Frontend
- **Template Engine**: EJS
- **Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JS (ES6+)

### Backend (Express)
- **Runtime**: Node.js
- **Framework**: Express.js 5.2.1
- **Database Driver**: mysql2 3.22.3
- **File Upload**: multer 1.4.5
- **HTTP Client**: axios 1.7.7
- **Config**: dotenv 16.4.5

### ML Backend
- **Language**: Python 3.8+
- **Framework**: Flask
- **ML Library**: TensorFlow/Keras
- **Image Processing**: OpenCV, NumPy

### Database
- **System**: MySQL 5.7+
- **Client**: mysql2 (Node.js)

---

## 📦 Prerequisites

### Required Software
- **Node.js** 16.x or higher
- **Python** 3.8 or higher
- **MySQL** 5.7 or higher
- **Git** (optional, for cloning)
- **npm** or **yarn** (package managers)

### Optional Tools
- **Visual Studio Code** (recommended IDE)
- **Postman** (for API testing)
- **MySQL Workbench** (for database management)
- **Python Virtual Environment** (for ML backend)

### System Requirements
- RAM: Minimum 4GB (8GB recommended)
- Disk Space: Minimum 2GB
- OS: Windows, macOS, or Linux

---

## 🚀 Installation Steps

### Step 1: Clone/Setup Project

```bash
# Navigate to project directory
cd "DualCrop Smart Advisory System"

# Navigate to Backend folder
cd Backend
```

### Step 2: Install Node Dependencies

```bash
# Install all required npm packages
npm install

# Or if using yarn
yarn install
```

### Step 3: Create Uploads Directory

```bash
# Create uploads folder for image storage
mkdir -p uploads

# For Windows PowerShell:
New-Item -ItemType Directory -Force -Path uploads
```

### Step 4: Install Python Dependencies (For Flask API)

```bash
# Create Python virtual environment (from root project folder)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python packages
pip install flask tensorflow keras pillow numpy opencv-python

# Or from requirements.txt
pip install -r requirements.txt
```

---

## 🗄️ Database Setup

### Step 1: Create Database

```sql
-- Connect to MySQL and run:
CREATE DATABASE dualcrop_db;
```

### Step 2: Create Predictions Table

```sql
USE dualcrop_db;

CREATE TABLE predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image VARCHAR(255) NOT NULL,
    result VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
);
```

### Step 3: Verify Connection

```bash
# Test MySQL connection (optional)
mysql -u root -p dualcrop_db
# If successful, you'll see: mysql>
```

---

## ⚙️ Configuration

### Step 1: Environment Variables

Create or update `.env` file in the Backend directory:

```env
# Server Configuration
PORT=3000
NODE_ENV=development

# MySQL Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=dualcrop_db

# OpenWeather API Key
OPENWEATHER_API_KEY=a6fd3a3e90a4af21c891b1b76eae85eb

# Flask API
FLASK_API_URL=http://localhost:5000
FLASK_API_PREDICT_ENDPOINT=/api/predict

# File Upload
MAX_FILE_SIZE=5242880
UPLOAD_DIR=uploads
```

### Step 2: Verify Configuration Files

- ✅ Check `.env` file exists in Backend folder
- ✅ Check `package.json` has all dependencies
- ✅ Check MySQL is running
- ✅ Check Flask API will run on port 5000

---

## 🎬 Running the Application

### Terminal 1: Start MySQL Server

```bash
# Make sure MySQL service is running
# Windows: MySQL runs as a service automatically
# macOS: brew services start mysql
# Linux: sudo service mysql start
```

### Terminal 2: Start Flask ML Backend

```bash
# From root project directory
# Activate Python environment (if not already)
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

# Run Flask server
python app.py
# Expected: Running on http://localhost:5000
```

### Terminal 3: Start Express Backend

```bash
# From Backend directory
# Development mode with auto-reload
npm run dev

# Or production mode
npm start

# Expected: ✅ Server running on http://localhost:3000
```

### Step 4: Access Application

- **Frontend**: http://localhost:3000
- **Flask API**: http://localhost:5000
- **Analyze Page**: http://localhost:3000/analyze
- **Dashboard**: http://localhost:3000/dashboard
- **Weather**: http://localhost:3000/weather
- **Chatbot**: http://localhost:3000/chatbot

---

## 💡 Features

### 1. Home Page (/)
- Landing page with project overview
- Feature cards highlighting key capabilities
- Call-to-action buttons

### 2. Analyze Page (/analyze)
- Upload leaf images (JPEG, PNG, GIF)
- Real-time image preview
- AI-powered disease detection
- Confidence score display
- Results saved to database
- Advisory recommendations

### 3. Dashboard (/dashboard)
- View all predictions in a table
- Filter and sort data
- Statistics cards (total analyses, healthy crops, diseases)
- Image thumbnails
- Prediction timestamps
- Database integration

### 4. Weather Page (/weather)
- Real-time weather API integration
- Search by city name
- Display: temperature, humidity, wind speed
- Weather-based crop advisory
- Fungal disease risk assessment
- Irrigation recommendations

### 5. Chatbot Page (/chatbot)
- Interactive chat interface
- AI-powered responses
- Quick action buttons
- Topics covered:
  - Crop care
  - Disease management
  - Fertilizer guide
  - Pest control
  - Weather advisory

### 6. About Page (/about)
- Project overview
- Technology stack details
- Architecture explanation
- Team information
- Contact details

---

## 🔧 Troubleshooting

### Error: "Cannot find module 'mysql2'"
```bash
# Solution: Reinstall node modules
npm install
```

### Error: "MySQL connection error"
- Check MySQL is running
- Verify DB_HOST, DB_USER, DB_PASSWORD in .env
- Ensure database 'dualcrop_db' exists

### Error: "Flask API not found"
```bash
# Solution: Ensure Flask is running on separate terminal
python app.py
```

### Error: "Port 3000 already in use"
```bash
# Solution: Use different port
PORT=3001 npm start

# Or kill process on port 3000
# Windows: netstat -ano | findstr :3000
# macOS/Linux: lsof -i :3000
```

### Error: "Image upload fails"
- Check uploads folder exists
- Verify file size < 5MB
- Check file format (JPEG, PNG, GIF)

### Error: "Database table not found"
```sql
-- Solution: Recreate table
USE dualcrop_db;

CREATE TABLE predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image VARCHAR(255) NOT NULL,
    result VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
);
```

---

## 📁 Project Structure

```
DualCrop Smart Advisory System/
├── Backend/
│   ├── views/                  # EJS template files
│   │   ├── home.ejs
│   │   ├── analyze.ejs
│   │   ├── dashboard.ejs
│   │   ├── weather.ejs
│   │   ├── chatbot.ejs
│   │   ├── about.ejs
│   │   └── 404.ejs
│   ├── public/                 # Static files
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       └── main.js
│   ├── uploads/                # User uploaded images
│   ├── db.js                   # Database configuration
│   ├── server.js               # Main Express server
│   ├── .env                    # Environment variables
│   ├── package.json            # Node dependencies
│   └── .gitignore
├── app.py                      # Flask ML backend
├── requirements.txt            # Python dependencies
├── artifacts/                  # ML model and history
│   ├── model.h5
│   └── history.json
├── Dataset/                    # Training data
└── README.md                   # Project documentation
```

---

## 🔐 Security Notes

### Important
- **Change DB_PASSWORD** in production
- **Update SESSION_SECRET** in .env
- **Use HTTPS** in production
- **Validate file uploads** (already implemented)
- **Sanitize user inputs** (use parameterized queries)
- **Implement rate limiting** for APIs
- **Add authentication** if needed

---

## 📊 Database Schema

```sql
-- Predictions Table
CREATE TABLE predictions (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    image            VARCHAR(255) NOT NULL,          -- Image filename
    result           VARCHAR(100) NOT NULL,          -- Disease/Crop name
    confidence       FLOAT NOT NULL,                 -- Confidence percentage
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
);
```

---

## 🚀 Deployment Checklist

- [ ] Set `NODE_ENV=production`
- [ ] Change all default passwords
- [ ] Set secure SESSION_SECRET
- [ ] Enable HTTPS
- [ ] Configure proper CORS
- [ ] Set up database backups
- [ ] Enable error logging
- [ ] Test all APIs thoroughly
- [ ] Optimize images and assets
- [ ] Set up monitoring

---

## 📞 Support & Contact

For issues and support:
- Email: support@dualcrop.com
- GitHub: [DualCrop Repository]
- Website: www.dualcrop.com

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🎓 Learning Resources

- [Node.js Documentation](https://nodejs.org/docs/)
- [Express.js Guide](https://expressjs.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [TensorFlow Guide](https://www.tensorflow.org/guide)

---

**Happy Farming! 🌾** 

Made with ❤️ by DualCrop Development Team
