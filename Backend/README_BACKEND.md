# 🌾 DualCrop Smart Advisory System

[![Node.js](https://img.shields.io/badge/Node.js-16%2B-green?style=flat-square)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square)](https://www.python.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?style=flat-square)](https://getbootstrap.com/)
[![MySQL](https://img.shields.io/badge/MySQL-5.7%2B-orange?style=flat-square)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-red?style=flat-square)](LICENSE)

## 📱 Live Demo

Access the application at: **http://localhost:3000**

---

## 🎯 What is DualCrop?

**DualCrop Smart Advisory System** is an AI-powered agricultural technology platform that empowers farmers with:

✅ **Early Disease Detection** - Upload leaf images and get instant AI-powered disease detection
✅ **Weather-Based Advice** - Real-time weather integration with crop recommendations
✅ **Data Analytics** - Beautiful dashboard to track all your analyses
✅ **AI Chatbot** - Intelligent chatbot for instant agricultural advice
✅ **Responsive Design** - Works seamlessly on desktop, tablet, and mobile

---

## 🚀 Key Features

### 🏠 Home Page
- Landing page with project overview
- Feature highlight cards
- Quick navigation buttons

### 🔍 Analyze Page (AI Disease Detection)
- Upload leaf images (JPEG, PNG, GIF)
- Real-time ML-powered predictions
- Confidence score display
- Automatic database storage
- AI-generated advisory recommendations

### 📊 Dashboard
- View all prediction history
- Statistics cards (total analyses, healthy crops, disease count)
- Searchable and sortable predictions table
- Confidence progress bars
- Timestamp tracking

### 🌦️ Weather Advisory
- Real-time weather API integration
- Search weather by city name
- Temperature, humidity, and wind speed display
- Smart crop recommendations based on weather conditions
- Fungal disease risk assessment

### 🤖 Intelligent Chatbot
- Interactive chat interface
- Rule-based agricultural advice
- Topics: crops, diseases, fertilizers, pesticides, weather
- Quick action buttons for common queries

### ℹ️ About Page
- Project overview
- Technology stack details
- Architecture explanation
- Developer information

---

## 🛠️ Tech Stack

### Frontend
```
EJS + Bootstrap 5.3 + Font Awesome 6.4 + Vanilla JavaScript
```

### Backend
```
Node.js + Express.js + Multer + Axios + MySQL2
```

### ML Backend
```
Python + Flask + TensorFlow + Keras
```

### Database
```
MySQL 5.7+
```

---

## 📋 Prerequisites

### System Requirements
- **Node.js**: v16.x or higher
- **Python**: 3.8 or higher  
- **MySQL**: 5.7 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB free space

### Check Installation
```bash
# Check Node.js
node --version

# Check npm
npm --version

# Check Python
python --version

# Check MySQL
mysql --version
```

---

## 🚀 Quick Start

### 1️⃣ Clone Repository
```bash
git clone <repository-url>
cd "DualCrop Smart Advisory System"
```

### 2️⃣ Setup Backend
```bash
cd Backend
npm install
mkdir -p uploads
```

### 3️⃣ Setup Database
```sql
-- Open MySQL
mysql -u root -p

-- Create database and table
CREATE DATABASE dualcrop_db;
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

### 4️⃣ Configure Environment
Edit `Backend/.env`:
```env
PORT=3000
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=dualcrop_db
OPENWEATHER_API_KEY=a6fd3a3e90a4af21c891b1b76eae85eb
```

### 5️⃣ Start Services

**Terminal 1 - Flask API**:
```bash
# From root directory
python app.py
# Expected: Running on http://localhost:5000
```

**Terminal 2 - Express Server**:
```bash
cd Backend
npm run dev
# Expected: ✅ Server running on http://localhost:3000
```

### 6️⃣ Access Application
Open your browser and navigate to:
```
http://localhost:3000
```

---

## 📁 Project Structure

```
DualCrop Smart Advisory System/
├── Backend/
│   ├── views/
│   │   ├── home.ejs              # Home page
│   │   ├── analyze.ejs           # Image upload & analysis
│   │   ├── dashboard.ejs         # Predictions dashboard
│   │   ├── weather.ejs           # Weather advisory
│   │   ├── chatbot.ejs           # AI chatbot
│   │   ├── about.ejs             # About page
│   │   └── 404.ejs               # Error page
│   ├── public/
│   │   ├── css/
│   │   │   └── style.css         # Custom styles
│   │   └── js/
│   │       └── main.js           # Utility scripts
│   ├── uploads/                  # User uploaded images
│   ├── db.js                     # Database config
│   ├── server.js                 # Express server
│   ├── .env                      # Environment variables
│   ├── package.json              # Dependencies
│   ├── SETUP_GUIDE.md            # Setup instructions
│   └── API_DOCUMENTATION.md      # API reference
├── app.py                        # Flask ML backend
├── requirements.txt              # Python dependencies
├── artifacts/
│   ├── model.h5                  # Trained ML model
│   └── history.json              # Training history
├── Dataset/                      # Training data
└── README.md                     # This file
```

---

## 🔌 API Endpoints

### Public Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page |
| GET | `/analyze` | Analyze page |
| GET | `/dashboard` | Dashboard page |
| GET | `/weather` | Weather page |
| GET | `/chatbot` | Chatbot page |
| GET | `/about` | About page |

### API Routes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Upload & analyze image |
| POST | `/api/weather` | Get weather data |
| POST | `/api/chat` | Send chatbot message |

### Sample Requests

**Upload Image for Analysis**:
```bash
curl -X POST http://localhost:3000/analyze \
  -F "image=@path/to/leaf.jpg"
```

**Get Weather Data**:
```bash
curl -X POST http://localhost:3000/api/weather \
  -H "Content-Type: application/json" \
  -d '{"city":"Delhi"}'
```

**Chat with Bot**:
```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Tell me about crop care"}'
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image VARCHAR(255) NOT NULL,           -- Uploaded image filename
    result VARCHAR(100) NOT NULL,          -- Prediction result (disease name)
    confidence FLOAT NOT NULL,             -- Confidence percentage (0-100)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_created_at (created_at)
);
```

---

## 🎓 How to Use

### Analyze a Crop Disease
1. Navigate to **Analyze** page
2. Click "Select Image" and choose a leaf photo
3. Click "Analyze Image"
4. View prediction and confidence score
5. Read AI-generated advisory
6. Results automatically saved to dashboard

### Check Analysis History
1. Go to **Dashboard**
2. View all past analyses in table format
3. See statistics like healthy crops vs. diseases
4. Hover over progress bars to see exact percentages

### Get Weather-Based Advice
1. Navigate to **Weather** page
2. Enter city name (e.g., "Mumbai")
3. View current weather conditions
4. Get personalized crop recommendations

### Chat with AI Assistant
1. Go to **Chatbot** page
2. Ask questions about:
   - Crop care tips
   - Disease management
   - Fertilizer recommendations
   - Pest control
3. Click quick action buttons for instant responses

---

## 🔧 Troubleshooting

### Issue: MySQL Connection Failed
```bash
# Solution: Verify MySQL is running
mysql -u root -p
# If connection succeeds, your MySQL is working

# Check .env file credentials
cat Backend/.env | grep DB_
```

### Issue: Flask API Not Found (500 Error)
```bash
# Solution: Ensure Flask is running
python app.py

# Should output: Running on http://localhost:5000
```

### Issue: Port 3000 Already in Use
```bash
# Option 1: Use different port
PORT=3001 npm start

# Option 2: Kill process on port 3000
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :3000
kill -9 <PID>
```

### Issue: Image Upload Fails
- ✅ Ensure file size < 5MB
- ✅ Check file format (JPEG, PNG, GIF)
- ✅ Verify `uploads/` folder exists
- ✅ Check file permissions

### Issue: Database Table Not Found
```sql
-- Recreate the table
USE dualcrop_db;

DROP TABLE IF EXISTS predictions;

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

## 📊 File Upload Limits

- **Max File Size**: 5MB
- **Supported Formats**: JPEG, PNG, GIF
- **Image Resolution**: Recommended 224x224 or larger
- **Storage**: `Backend/uploads/` directory

---

## 🔐 Security Features

✅ File type validation
✅ File size limits
✅ Image extension checking
✅ SQL injection protection via prepared statements
✅ XSS protection via EJS escaping
✅ CORS headers configured
✅ Error message sanitization

---

## 📈 Performance Tips

### For Production:
- Enable gzip compression
- Minify CSS and JavaScript
- Use CDN for Bootstrap and Font Awesome
- Implement database indexes
- Add caching headers
- Use image optimization

### Optimization:
```bash
# Minify CSS
npm install -g cssnano-cli

# Minify JavaScript
npm install -g terser

# Image optimization
npm install -g imagemin-cli
```

---

## 🧪 Testing

### Test Upload Functionality
```bash
# Create test image (Linux/macOS)
convert -size 224x224 xc:green test_image.png

# Upload
curl -F "image=@test_image.png" http://localhost:3000/analyze
```

### Test Weather API
```bash
curl -X POST http://localhost:3000/api/weather \
  -H "Content-Type: application/json" \
  -d '{"city":"London"}' | json_pp
```

### Test Database Connection
```bash
# From MySQL
USE dualcrop_db;
SELECT COUNT(*) FROM predictions;
```

---

## 🚀 Deployment Guide

### Deploy to Heroku
1. Create Heroku account
2. Install Heroku CLI
3. Configure MySQL addon
4. Update environment variables
5. Deploy repository

```bash
heroku create dualcrop-app
heroku config:set DB_HOST=<heroku-db-host>
git push heroku main
```

### Deploy to AWS
- Use EC2 for application server
- Use RDS for MySQL database
- Use S3 for image storage
- Set up CloudFront CDN

---

## 📞 Support & Documentation

- **Setup Guide**: `Backend/SETUP_GUIDE.md`
- **API Documentation**: `Backend/API_DOCUMENTATION.md`
- **Project README**: `README.md` (root)
- **Code Comments**: Well-documented code with inline comments

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 👨‍💻 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 🙏 Acknowledgments

- Bootstrap 5 team for excellent CSS framework
- Font Awesome for icons
- OpenWeatherMap for weather API
- TensorFlow team for ML framework
- Express.js community

---

## 📧 Contact

**DualCrop Development Team**
- Email: support@dualcrop.com
- Website: www.dualcrop.com
- GitHub: [DualCrop Repository]

---

## 🌱 Future Enhancements

Planned features:
- [ ] User authentication & profiles
- [ ] Multi-language support
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Crop recommendation engine
- [ ] Marketplace integration
- [ ] Real-time notifications
- [ ] Video tutorials

---

## 📊 Statistics

- **Frontend Pages**: 6 (Home, Analyze, Dashboard, Weather, Chatbot, About)
- **API Endpoints**: 6 (3 GET, 3 POST)
- **Database Tables**: 1
- **CSS Lines**: 500+
- **JavaScript Lines**: 400+
- **Backend Routes**: 15+

---

## 🎓 Learning Resources

- [Node.js Best Practices](https://nodejs.org/en/docs/guides/nodejs-web-app-without-a-framework/)
- [Express.js Guide](https://expressjs.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/5.3/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

---

<div align="center">

### Made with ❤️ by DualCrop Development Team

**"Smart Farming for Sustainable Agriculture"**

⭐ If you find this project helpful, please star the repository! ⭐

</div>

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: ✅ Production Ready
