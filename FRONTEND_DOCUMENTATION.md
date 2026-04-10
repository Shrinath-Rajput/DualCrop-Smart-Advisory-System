# 🌾 DualCrop Smart Advisory System - Frontend Documentation

## 📁 Frontend Structure

```
templates/
├── base.html          # Base template with header, nav, footer
├── index.html         # Home page - Image upload & prediction
├── dashboard.html     # Dashboard - Statistics & metrics
├── history.html       # Prediction history browser
├── about.html         # About page - Project information
└── 404.html          # 404 error page
```

---

## 🎨 Pages Overview

### 1. **base.html** - Base Template
**Purpose:** Provides common layout for all pages

**Features:**
- Navigation bar with links to all pages
- Logo and branding
- Footer with copyright
- Global styling and header/footer styling

**Components:**
- Header with navigation
- Dynamic page content block
- Footer
- Active link highlighting

**Usage:** Extended by all other templates using Jinja2 `{% extends %}`

---

### 2. **index.html** - Home Page (Main Feature)
**Purpose:** Image upload and disease prediction interface

**Features:**
- Drag & drop file upload
- Image preview
- Real-time prediction
- Confidence score display
- File validation (type & size)
- Error handling

**Key Elements:**
- Upload area with drag-drop support
- Image preview section
- Analyze & Clear buttons
- Prediction results display
- Disease class statistics

**JavaScript Functions:**
- `handleFileSelect()` - Process uploaded file
- `showResult()` - Display prediction results
- `showError()` - Show error messages
- `loadClassCount()` - Fetch disease classes

**Storage:**
- Saves predictions to localStorage for history

---

### 3. **dashboard.html** - Analytics Dashboard
**Purpose:** Display system statistics and metrics

**Features:**
- Total predictions count
- Model accuracy score
- Disease classes count
- System uptime
- Model configuration details
- Recent activity log

**Key Metrics:**
- Dashboard cards showing stats
- Model information section
- Recent activity timeline
- Configuration details

**JavaScript:**
- `loadDashboardData()` - Load stats from API

---

### 4. **history.html** - Prediction History
**Purpose:** Browse and manage past predictions

**Features:**
- List all past predictions with thumbnails
- Date and time stamps
- Confidence scores
- Delete individual predictions
- Clear all history option
- Filter by date range (Today, Week, Month)

**Key Elements:**
- History item cards with images
- Prediction details (class, date, time, confidence)
- Delete buttons
- Filter options

**JavaScript Functions:**
- `loadHistory()` - Load predictions from localStorage
- `deletePrediction()` - Remove single prediction
- `clearAllHistory()` - Clear all history
- `filterHistory()` - Filter by date

**Storage:**
- Reads from localStorage['predictions']

---

### 5. **about.html** - Project Information
**Purpose:** Display project details, team info, and support

**Sections:**
- Mission statement
- Key features with cards
- Supported crops and diseases
- Technology stack
- Development team
- Project timeline
- Support & contact information
- License & attribution

**Features:**
- Feature cards with emojis
- Team member cards
- Technology badges
- Timeline of development phases
- Contact information

---

### 6. **404.html** - Error Page
**Purpose:** Display 404 page not found errors

**Features:**
- Large 404 error code
- Error message
- Description
- Link back to home

---

## 🎯 Navigation Flow

```
base.html (header + nav + footer)
│
├── index.html        (Home - Upload & Predict)
├── dashboard.html    (Analytics & Stats)
├── history.html      (Past Predictions)
└── about.html        (Project Info)
```

---

## 💾 Data Storage

### LocalStorage Usage
The frontend uses browser localStorage to persist data:

```javascript
{
  predictions: [
    {
      filename: "image.jpg",
      image: "data:image/jpeg;base64,...",
      predicted_class: "Grapes_Grape___Black_rot",
      confidence: 0.98,
      timestamp: 1234567890000
    },
    ...
  ]
}
```

---

## 🌐 API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Home page |
| `/dashboard` | GET | Dashboard page |
| `/history` | GET | History page |
| `/about` | GET | About page |
| `/api/info` | GET | App info |
| `/api/classes` | GET | Disease classes |
| `/api/predict` | POST | Single image prediction |
| `/api/health` | GET | Health check |

---

## 🎨 Design System

### Colors
- **Primary Gradient:** #667eea → #764ba2 (Purple)
- **Success:** #10b981 (Green)
- **Error:** #ef4444 (Red)
- **Background:** #f8f9ff (Light blue)
- **Text:** #333 (Dark gray)

### Typography
- **Font:** Segoe UI, Tahoma, Geneva, Verdana, sans-serif
- **Headings:** Bold, larger size
- **Body:** Regular weight, 14-16px

### Components
- **Buttons:** Gradient background, hover effects
- **Cards:** White background, subtle shadows, rounded corners
- **Input:** Styled file input with validation
- **Results:** Colored boxes (green success, red error)

---

## 📱 Responsive Design

All pages are fully responsive for:
- **Desktop:** Full layout with multi-column grids
- **Tablet:** Adjusted spacing and grid columns
- **Mobile:** Single column, touch-friendly buttons

**Breakpoint:** 600px (Mobile adjustments)

---

## 🔄 Jinja2 Template Features

### Template Inheritance
```html
{% extends "base.html" %}
{% block title %}Page Title{% endblock %}
{% block content %}...{% endblock %}
```

### Active Navigation
```html
{% block nav_home %}active{% endblock %}  <!-- Highlights current page -->
```

### Conditional Content
```html
{% if condition %}
    ...content...
{% endif %}
```

---

## 🚀 Running the Frontend

1. **Start Flask Server:**
   ```bash
   python app.py
   ```

2. **Access in Browser:**
   ```
   http://localhost:5000
   ```

3. **Navigate Using:**
   - Top navigation menu
   - Direct URLs: /dashboard, /history, /about

---

## 📊 File Sizes

| File | Size (approx) |
|------|---------------|
| base.html | ~8 KB |
| index.html | ~15 KB |
| dashboard.html | ~8 KB |
| history.html | ~12 KB |
| about.html | ~16 KB |
| 404.html | ~5 KB |
| **Total** | **~64 KB** |

---

## ✨ Future Enhancements

1. **Real-time Notifications** - Alert user of new features
2. **Dark Mode** - Toggle between light/dark themes
3. **Export Results** - Download predictions as PDF/CSV
4. **Advanced Filters** - Filter history by disease type
5. **Mobile App** - React Native/Flutter adaptation
6. **PWA Support** - Progressive web app features (offline mode)
7. **Analytics Dashboard** - More detailed charts and graphs
8. **Admin Panel** - Model management and monitoring
9. **Multi-language Support** - Localization (Hindi, etc.)
10. **API Documentation** - Interactive Swagger UI

---

## 🐛 Troubleshooting

### Page Not Loading
- Check browser console for errors
- Ensure Flask server is running
- Clear browser cache

### Predictions Not Showing
- Check localStorage quota (usually 5-10MB per domain)
- Verify API endpoint is responding
- Check network tab in developer tools

### Styling Issues
- Hard refresh (Ctrl+Shift+R)
- Check if CSS is being loaded
- Verify no conflicting CSS

### Navigation Not Working
- Ensure Flask routes are properly mapped
- Check URL paths match route definitions
- Verify Jinja2 template syntax

---

## 📝 Best Practices

1. **Performance:**
   - Minimize localStorage usage
   - Use efficient image formats (JPEG preferred)
   - Lazy-load external resources

2. **Accessibility:**
   - Use semantic HTML tags
   - Add ARIA labels where needed
   - Ensure color contrast is sufficient

3. **Security:**
   - Validate file types on frontend AND backend
   - Sanitize user input
   - Don't store sensitive data in localStorage

4. **User Experience:**
   - Provide clear feedback for all actions
   - Show loading states during API calls
   - Handle errors gracefully

---

## 📞 Support

For issues or questions about the frontend:
- Check the troubleshooting section
- Review browser console errors
- Consult the main project documentation
- Contact the development team

---

**Version:** 1.0.0  
**Last Updated:** April 2, 2026  
**Status:** ✅ Production Ready
