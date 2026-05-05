// ========================================
// DualCrop Smart Advisory System
// Express.js Backend Server
// ========================================

require("dotenv").config();
const express = require("express");
const path = require("path");
const multer = require("multer");
const axios = require("axios");
const fs = require("fs");
const pool = require("./db");

const app = express();

// Create uploads directory if it doesn't exist
const uploadDir = path.join(__dirname, "uploads");
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir, { recursive: true });
    console.log("✅ Uploads directory created");
}

// ========== MIDDLEWARE SETUP ==========

// Body parser middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// EJS template engine setup
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));

// Static files setup
app.use(express.static(path.join(__dirname, "public")));
app.use("/uploads", express.static(path.join(__dirname, "uploads")));

// Upload directory for images - configure multer storage
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        cb(null, Date.now() + "-" + file.originalname);
    },
});

const upload = multer({
    storage: storage,
    limits: { fileSize: 5 * 1024 * 1024 }, // 5MB limit
    fileFilter: (req, file, cb) => {
        const allowedTypes = ["image/jpeg", "image/png", "image/gif"];
        if (allowedTypes.includes(file.mimetype)) {
            cb(null, true);
        } else {
            cb(new Error("Only image files are allowed"));
        }
    },
});

// ========== ROUTES ==========

// 1️⃣ HOME PAGE
app.get("/", (req, res) => {
    res.render("home", { title: "DualCrop Smart Advisory System" });
});

// 2️⃣ ANALYZE PAGE (GET)
app.get("/analyze", (req, res) => {
    res.render("analyze", { title: "Analyze Crop Disease" });
});

// 3️⃣ ANALYZE PAGE (POST) - Handle image upload
app.post("/analyze", upload.single("image"), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: "No file uploaded" });
        }

        // Create FormData for Flask API
        const FormData = require("form-data");
        const formData = new FormData();
        
        // Verify file exists before sending
        if (!fs.existsSync(req.file.path)) {
            return res.status(400).json({ 
                error: "File not found after upload",
                path: req.file.path 
            });
        }
        
        formData.append("file", fs.createReadStream(req.file.path));

        // Call Flask API
        console.log(`🔄 Calling Flask API with image: ${req.file.filename}`);
        const flaskResponse = await axios.post(
            "http://localhost:5000/api/predict",
            formData,
            {
                headers: formData.getHeaders(),
            }
        );

        const { prediction, confidence } = flaskResponse.data;
        console.log(`✅ Flask Response: ${prediction} (${confidence}%)`);

        // Save to MySQL database
        const connection = await pool.getConnection();
        const query =
            "INSERT INTO predictions (image, result, confidence) VALUES (?, ?, ?)";
        await connection.execute(query, [req.file.filename, prediction, confidence]);
        connection.release();

        console.log("✅ Prediction saved to database");

        // Return JSON response
        res.json({
            success: true,
            image: req.file.filename,
            prediction: prediction,
            confidence: confidence,
        });
    } catch (error) {
        // Enhanced error logging
        let errorMessage = error.message;
        let flaskError = null;

        if (error.response) {
            // Error response from Flask
            errorMessage = `Flask API Error: ${error.response.status}`;
            flaskError = error.response.data;
            console.error("❌ Error:", errorMessage);
            console.error("📋 Flask Response:", JSON.stringify(flaskError, null, 2));
        } else if (error.request) {
            // Request made but no response
            errorMessage = "No response from Flask server. Is it running on port 5000?";
            console.error("❌ Error:", errorMessage);
        } else {
            console.error("❌ Error:", error.message);
        }

        res.status(500).json({
            error: "Failed to process image",
            details: errorMessage,
            flaskError: flaskError,
        });
    }
});

// 4️⃣ DASHBOARD PAGE
app.get("/dashboard", async (req, res) => {
    try {
        const connection = await pool.getConnection();
        const [predictions] = await connection.execute(
            "SELECT id, image, result, confidence, created_at FROM predictions ORDER BY created_at DESC LIMIT 100"
        );
        connection.release();

        res.render("dashboard", {
            title: "Dashboard",
            predictions: predictions,
            count: predictions.length,
        });
    } catch (error) {
        console.error("❌ Error fetching predictions:", error.message);
        res.render("dashboard", {
            title: "Dashboard",
            predictions: [],
            count: 0,
            error: "Failed to fetch predictions",
        });
    }
});

// 5️⃣ WEATHER PAGE
app.get("/weather", (req, res) => {
    res.render("weather", { title: "Weather & Crop Advisory" });
});

// 6️⃣ GET WEATHER DATA (API)
app.post("/api/weather", async (req, res) => {
    try {
        const { city } = req.body;

        if (!city) {
            return res.status(400).json({ error: "City name is required" });
        }

        // Call OpenWeatherMap API
        const apiKey = process.env.OPENWEATHER_API_KEY || "a6fd3a3e90a4af21c891b1b76eae85eb";
        const response = await axios.get(
            `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`
        );

        const { main, weather, wind } = response.data;

        // Generate crop advisory based on weather
        let advisory = [];
        if (main.humidity > 80) {
            advisory.push("⚠️ High humidity - Risk of fungal diseases. Apply fungicides.");
        }
        if (main.temp < 10) {
            advisory.push("❄️ Low temperature - Ensure proper crop protection.");
        }
        if (wind.speed > 15) {
            advisory.push("💨 Strong winds - Risk of physical damage. Monitor crops.");
        }
        if (main.humidity < 30) {
            advisory.push("🌵 Low humidity - Increase irrigation frequency.");
        }

        res.json({
            success: true,
            city: response.data.name,
            country: response.data.sys.country,
            temperature: Math.round(main.temp),
            humidity: main.humidity,
            condition: weather[0].main,
            description: weather[0].description,
            windSpeed: wind.speed,
            feelsLike: Math.round(main.feels_like),
            advisory: advisory.length > 0 ? advisory : ["✅ Conditions are favorable for crop growth."],
        });
    } catch (error) {
        console.error("❌ Error fetching weather:", error.message);
        res.status(500).json({
            error: "Failed to fetch weather data",
            details: error.message,
        });
    }
});

// 7️⃣ CHATBOT PAGE
app.get("/chatbot", (req, res) => {
    res.render("chatbot", { title: "AI Chatbot Assistant" });
});

// 8️⃣ CHATBOT API
app.post("/api/chat", (req, res) => {
    try {
        const { message } = req.body;
        if (!message) {
            return res.status(400).json({ error: "Message is required" });
        }

        const lowerMessage = message.toLowerCase();
        let reply = "I'm not sure about that. Please ask about crops, diseases, or fertilizers.";

        // Simple rule-based responses
        if (lowerMessage.includes("crop")) {
            reply =
                "🌾 **Crop Care Tips:**\n" +
                "- Water regularly (morning or evening)\n" +
                "- Use nitrogen-rich fertilizers\n" +
                "- Maintain soil pH 6.0-7.0\n" +
                "- Rotate crops annually";
        } else if (lowerMessage.includes("disease")) {
            reply =
                "🦠 **Disease Management:**\n" +
                "- Identify symptoms early\n" +
                "- Use fungicides for fungal diseases\n" +
                "- Apply insecticides for pests\n" +
                "- Remove infected leaves";
        } else if (lowerMessage.includes("fertilizer")) {
            reply =
                "🌱 **Fertilizer Guide:**\n" +
                "- NPK (Nitrogen-Phosphorus-Potassium) ratio for general crops: 10-10-10\n" +
                "- Apply every 2-3 weeks\n" +
                "- Use compost for organic farming";
        } else if (lowerMessage.includes("pesticide")) {
            reply =
                "🚫 **Pest Control:**\n" +
                "- Neem oil for common pests\n" +
                "- Pyrethrin-based sprays for insects\n" +
                "- Copper sulfate for fungal issues\n" +
                "- Use as per label instructions";
        } else if (
            lowerMessage.includes("hello") ||
            lowerMessage.includes("hi")
        ) {
            reply =
                "👋 Hello! I'm the DualCrop AI Assistant. Ask me about crop diseases, fertilizers, or pest management!";
        } else if (
            lowerMessage.includes("weather") ||
            lowerMessage.includes("rain")
        ) {
            reply =
                "🌦️ **Weather Advisory:**\n" +
                "- Check weather before spraying\n" +
                "- Avoid spray during rain\n" +
                "- Morning/evening is best for application";
        }

        res.json({
            success: true,
            message: message,
            reply: reply,
        });
    } catch (error) {
        console.error("❌ Error in chatbot:", error.message);
        res.status(500).json({ error: "Chatbot error occurred" });
    }
});

// 9️⃣ ABOUT PAGE
app.get("/about", (req, res) => {
    res.render("about", { title: "About DualCrop" });
});

// 🔟 HISTORY PAGE
app.get("/history", (req, res) => {
    res.render("history", { title: "Prediction History" });
});

// 1️⃣1️⃣ GET PREDICTIONS (JSON API)
app.get("/api/predictions", async (req, res) => {
    try {
        const connection = await pool.getConnection();
        const [predictions] = await connection.execute(
            "SELECT id, image, result, confidence, created_at FROM predictions ORDER BY created_at DESC LIMIT 100"
        );
        connection.release();

        res.json({
            success: true,
            predictions: predictions,
            count: predictions.length,
        });
    } catch (error) {
        console.error("❌ Error fetching predictions:", error.message);
        res.status(500).json({
            success: false,
            error: "Failed to fetch predictions",
            predictions: [],
        });
    }
});

// ❌ 404 ERROR PAGE
app.use((req, res) => {
    res.status(404).render("404", { title: "Page Not Found" });
});

// ========== ERROR HANDLING ==========
app.use((err, req, res, next) => {
    console.error("❌ Error:", err.message);
    res.status(500).json({
        error: "Internal Server Error",
        message: err.message,
    });
});

// ========== START SERVER ==========
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log("\n✅ ====================================");
    console.log("   DualCrop Smart Advisory System");
    console.log("   🚀 Server running on http://localhost:" + PORT);
    console.log("   🐍 Flask API should run on http://localhost:5000");
    console.log("   💾 MySQL Database: dualcrop_db");
    console.log("================================== ✅\n");
});