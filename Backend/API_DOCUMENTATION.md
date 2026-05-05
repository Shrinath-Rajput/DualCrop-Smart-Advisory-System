# 📡 DualCrop Smart Advisory System - API Documentation

## Base URL
```
http://localhost:3000
```

## Authentication
Currently, the API does not require authentication. In production, implement JWT tokens.

---

## 📚 Endpoints Reference

### 1️⃣ HOME PAGE
```
GET /
```

**Description**: Render the home page with project overview

**Response**: HTML Page

**Example**:
```bash
curl http://localhost:3000/
```

---

### 2️⃣ ANALYZE - GET PAGE
```
GET /analyze
```

**Description**: Render the analyze page with upload form

**Response**: HTML Page

**Example**:
```bash
curl http://localhost:3000/analyze
```

---

### 3️⃣ ANALYZE - POST (Image Upload)
```
POST /analyze
Content-Type: multipart/form-data
```

**Description**: Upload leaf image for disease detection

**Parameters**:
- `image` (file, required): Image file (JPEG, PNG, GIF) - Max 5MB

**Request Example**:
```bash
curl -X POST http://localhost:3000/analyze \
  -F "image=@path/to/leaf.jpg"
```

**Response**:
```json
{
  "success": true,
  "image": "1234567890-leaf.jpg",
  "prediction": "Grapes___Black_rot",
  "confidence": 92.5
}
```

**Status Codes**:
- `200`: Success
- `400`: No file uploaded
- `500`: Processing error

**Error Response**:
```json
{
  "error": "Failed to process image. Make sure Flask server is running on port 5000.",
  "details": "Error message"
}
```

---

### 4️⃣ DASHBOARD - GET
```
GET /dashboard
```

**Description**: Render dashboard with prediction history

**Response**: HTML Page with predictions data

**Query Parameters**: None

**Example**:
```bash
curl http://localhost:3000/dashboard
```

**Displays**:
- Total analysis count
- Healthy crop count
- Disease detection count
- Average confidence
- Recent predictions table

---

### 5️⃣ WEATHER - GET PAGE
```
GET /weather
```

**Description**: Render weather advisory page

**Response**: HTML Page

**Example**:
```bash
curl http://localhost:3000/weather
```

---

### 6️⃣ WEATHER - POST (Get Weather Data)
```
POST /api/weather
Content-Type: application/json
```

**Description**: Get weather data and crop advisory for a city

**Request Body**:
```json
{
  "city": "Mumbai"
}
```

**Request Example**:
```bash
curl -X POST http://localhost:3000/api/weather \
  -H "Content-Type: application/json" \
  -d '{"city":"Delhi"}'
```

**Response** (Success):
```json
{
  "success": true,
  "city": "Delhi",
  "country": "IN",
  "temperature": 28,
  "humidity": 65,
  "condition": "Partly cloudy",
  "description": "broken clouds",
  "windSpeed": 12.5,
  "feelsLike": 30,
  "advisory": [
    "⚠️ High humidity - Risk of fungal diseases. Apply fungicides.",
    "✅ Wind speed is good for crop health"
  ]
}
```

**Response** (Error):
```json
{
  "error": "Failed to fetch weather data",
  "details": "Error message"
}
```

**Status Codes**:
- `200`: Success
- `400`: City name missing
- `500`: API error

---

### 7️⃣ CHATBOT - GET PAGE
```
GET /chatbot
```

**Description**: Render chatbot page

**Response**: HTML Page

**Example**:
```bash
curl http://localhost:3000/chatbot
```

---

### 8️⃣ CHATBOT - POST (Send Message)
```
POST /api/chat
Content-Type: application/json
```

**Description**: Send message to chatbot and get response

**Request Body**:
```json
{
  "message": "Tell me about crop care"
}
```

**Request Example**:
```bash
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"What about diseases?"}'
```

**Response** (Success):
```json
{
  "success": true,
  "message": "What about diseases?",
  "reply": "🦠 **Disease Management:**\n- Identify symptoms early\n- Use fungicides for fungal diseases\n- Apply insecticides for pests\n- Remove infected leaves"
}
```

**Response** (Error):
```json
{
  "error": "Chatbot error occurred"
}
```

**Supported Keywords**:
- `crop`: Crop care tips
- `disease`: Disease management
- `fertilizer`: Fertilizer guide
- `pesticide`: Pest control
- `hello/hi`: Greeting
- `weather/rain`: Weather advice

**Status Codes**:
- `200`: Success
- `400`: Message missing
- `500`: Processing error

---

### 9️⃣ ABOUT PAGE
```
GET /about
```

**Description**: Render about page with project information

**Response**: HTML Page

**Example**:
```bash
curl http://localhost:3000/about
```

---

### ❌ NOT FOUND
```
GET /any-undefined-route
```

**Description**: 404 error page for undefined routes

**Response**: HTML 404 Page

**Status Code**: `404`

---

## 🔗 Flask API Integration

### Internal Flask Endpoint (Called by Backend)
```
POST http://localhost:5000/api/predict
Content-Type: multipart/form-data
```

**Parameters**:
- `file` (file): Leaf image file

**Response**:
```json
{
  "prediction": "Grapes___Black_rot",
  "confidence": 92.5
}
```

---

## 🗄️ Database Operations

### Get All Predictions
```sql
SELECT id, image, result, confidence, created_at 
FROM predictions 
ORDER BY created_at DESC 
LIMIT 100;
```

### Insert Prediction
```sql
INSERT INTO predictions (image, result, confidence) 
VALUES (?, ?, ?);
```

### Get Statistics
```sql
SELECT 
  COUNT(*) as total,
  SUM(CASE WHEN result LIKE '%healthy%' THEN 1 ELSE 0 END) as healthy,
  SUM(CASE WHEN result NOT LIKE '%healthy%' THEN 1 ELSE 0 END) as diseases,
  AVG(confidence) as avg_confidence
FROM predictions;
```

---

## 📋 Error Handling

### Standard Error Response Format
```json
{
  "error": "Error message",
  "details": "Additional error information"
}
```

### Common Error Codes
| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 400 | Bad Request - Invalid input |
| 404 | Not Found - Resource doesn't exist |
| 500 | Internal Server Error - Server error |

---

## 🔐 Security Headers

Recommended headers to add in production:
```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

---

## 🚀 Usage Examples

### Example 1: Complete Analysis Flow
```bash
# 1. Upload image for analysis
curl -X POST http://localhost:3000/analyze \
  -F "image=@leaf.jpg"

# Response:
# {
#   "success": true,
#   "prediction": "Grapes___Black_rot",
#   "confidence": 92.5
# }

# 2. Check dashboard (data automatically saved)
curl http://localhost:3000/dashboard

# 3. Get weather recommendation
curl -X POST http://localhost:3000/api/weather \
  -H "Content-Type: application/json" \
  -d '{"city":"Delhi"}'
```

### Example 2: Chatbot Interaction
```bash
# Ask about disease management
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Tell me about disease management"}'

# Response:
# {
#   "success": true,
#   "reply": "🦠 **Disease Management:**\n..."
# }
```

### Example 3: Using JavaScript Fetch
```javascript
// Upload image
const formData = new FormData();
formData.append('image', fileInput.files[0]);

const response = await fetch('/analyze', {
  method: 'POST',
  body: formData
});

const data = await response.json();
console.log(data.prediction, data.confidence);
```

---

## 📊 Rate Limiting (Future Implementation)

Recommended rate limits:
```
/analyze: 10 requests per minute
/api/weather: 30 requests per minute
/api/chat: 60 requests per minute
```

---

## 🔄 CORS Configuration

Current CORS settings:
- **Allow Origins**: All (`*`)
- **Allow Methods**: GET, POST, OPTIONS
- **Allow Headers**: Content-Type

For production, restrict to specific domains:
```javascript
cors({
  origin: 'https://yourdomain.com',
  credentials: true
})
```

---

## 📝 Request/Response Examples

### JavaScript Fetch Examples

**Image Upload**:
```javascript
const formData = new FormData();
const fileInput = document.getElementById('imageInput');
formData.append('image', fileInput.files[0]);

fetch('/analyze', {
  method: 'POST',
  body: formData
})
  .then(res => res.json())
  .then(data => {
    console.log('Prediction:', data.prediction);
    console.log('Confidence:', data.confidence);
  });
```

**Weather Request**:
```javascript
const cityName = 'Delhi';

fetch('/api/weather', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ city: cityName })
})
  .then(res => res.json())
  .then(data => {
    console.log('Temperature:', data.temperature);
    console.log('Advisory:', data.advisory);
  });
```

**Chatbot Message**:
```javascript
const userMessage = 'Tell me about crops';

fetch('/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ message: userMessage })
})
  .then(res => res.json())
  .then(data => {
    console.log('Bot Reply:', data.reply);
  });
```

---

## 🧪 Testing with Postman

1. Import endpoints to Postman
2. Set base URL: `http://localhost:3000`
3. Test each endpoint
4. Verify response codes and data

---

## 📞 Support

For API issues, check:
1. Flask server is running
2. MySQL is connected
3. .env file is configured
4. File sizes are within limits
5. Check console for error logs

---

**API Version**: 1.0.0
**Last Updated**: 2024
