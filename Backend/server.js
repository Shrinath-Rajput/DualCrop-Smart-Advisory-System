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

// ========== PREDICTION FALLBACK (MOCK DATA) ==========
function getFallbackPrediction(filename) {
    // Fallback predictions based on filename pattern
    const fallbackPredictions = {
        "healthy": { prediction: "Brinjal Healthy Leaf", confidence: 92.5 },
        "black_rot": { prediction: "Grapes Black Rot", confidence: 88.3 },
        "esca": { prediction: "Grapes Esca (Black Measles)", confidence: 85.6 },
        "leaf_blight": { prediction: "Grapes Leaf Blight", confidence: 87.9 },
        "rot": { prediction: "Grapes Black Rot", confidence: 85.2 },
    };

    const lowerFilename = filename.toLowerCase();
    for (const [key, value] of Object.entries(fallbackPredictions)) {
        if (lowerFilename.includes(key)) {
            return value;
        }
    }

    // Default fallback
    return { prediction: "Unknown", confidence: 50.0 };
}

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

        console.log(`📤 File uploaded: ${req.file.filename}`);
        
        let prediction = null;
        let confidence = null;
        let flaskAvailable = true;

        // Try to call Flask API
        try {
            const FormData = require("form-data");
            const formData = new FormData();
            
            // Verify file exists before sending
            if (!fs.existsSync(req.file.path)) {
                throw new Error("File not found after upload");
            }
            
            formData.append("file", fs.createReadStream(req.file.path));

            console.log(`🔄 Attempting Flask API call...`);
            const flaskResponse = await axios.post(
                "http://localhost:5000/api/predict",
                formData,
                {
                    headers: formData.getHeaders(),
                    timeout: 10000, // 10 second timeout
                }
            );

            prediction = flaskResponse.data.prediction;
            confidence = flaskResponse.data.confidence;
            console.log(`✅ Flask Response: ${prediction} (${confidence}%)`);

        } catch (flaskError) {
            // Flask is not available, use fallback
            flaskAvailable = false;
            console.warn(`⚠️ Flask API unavailable, using fallback prediction`);
            
            const fallback = getFallbackPrediction(req.file.filename);
            prediction = fallback.prediction;
            confidence = fallback.confidence;
            
            console.log(`📊 Fallback Prediction: ${prediction} (${confidence}%)`);
        }

        // Get medicine recommendation
        const medicineRec = medicineRecommendations[prediction] || medicineRecommendations["Unknown"];

        // Save to MySQL database
        try {
            const connection = await pool.getConnection();
            const query =
                "INSERT INTO predictions (image, result, confidence) VALUES (?, ?, ?)";
            await connection.execute(query, [req.file.filename, prediction, confidence]);
            connection.release();
            console.log("✅ Prediction saved to database");
        } catch (dbError) {
            console.warn("⚠️ Database save failed:", dbError.message);
            // Continue anyway, database is optional for prediction
        }

        // Clean up uploaded file
        try {
            if (fs.existsSync(req.file.path)) {
                fs.unlinkSync(req.file.path);
            }
        } catch (cleanupError) {
            console.warn("⚠️ File cleanup failed:", cleanupError.message);
        }

        // Return JSON response with medicine recommendation
        res.json({
            success: true,
            image: req.file.filename,
            prediction: prediction,
            confidence: confidence,
            medicine: medicineRec,
            flaskAvailable: flaskAvailable,
            note: flaskAvailable ? "Prediction from Flask AI Model" : "Prediction from fallback system"
        });

    } catch (error) {
        console.error("❌ Critical Error:", error.message);
        
        // Clean up uploaded file
        try {
            if (req.file && fs.existsSync(req.file.path)) {
                fs.unlinkSync(req.file.path);
            }
        } catch (cleanupError) {
            console.warn("⚠️ File cleanup failed:", cleanupError.message);
        }

        res.status(500).json({
            success: false,
            error: "Failed to process image",
            details: error.message,
            hint: "Make sure the file is a valid image (JPG, PNG, GIF)"
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

// ========== MEDICINE RECOMMENDATIONS DATABASE ==========
const medicineRecommendations = {
    "Brinjal Healthy Leaf": {
        healthy: {
            medicine: "No medicine required",
            description: "✅ Plant is healthy",
            preventive: [
                "🛡️ Neem oil spray every 15 days for preventive care",
                "🌿 Use organic fertilizer (NPK 10-10-10)",
                "💧 Maintain proper irrigation schedule"
            ]
        },
        high_humidity: {
            medicine: ["Copper Hydroxide 77% WP", "Mancozeb 75% WP"],
            dosage: "2-2.5 ml per liter of water",
            spraying_interval: "7-10 days",
            description: "🍆 Brinjal - High humidity fungal protection"
        },
        low_humidity: {
            medicine: ["Sulfur 80% WP", "Potassium Sulfate"],
            dosage: "2 gm per liter",
            spraying_interval: "10-14 days",
            description: "🍆 Brinjal - Drought management & pest control"
        },
        high_temp: {
            medicine: ["Neem Oil 3%", "Trichoderma"],
            dosage: "3-5 ml per liter",
            spraying_interval: "7 days",
            description: "🍆 Brinjal - Heat stress protection"
        }
    },
    "Grapes Healthy": {
        healthy: {
            medicine: "No medicine required",
            description: "✅ Grapes are healthy",
            preventive: [
                "🛡️ Sulfur powder spray every 10-14 days",
                "🌿 Balanced fertilizer (NPK 12-8-10)",
                "💧 Drip irrigation recommended"
            ]
        },
        disease: {
            medicine: ["Bordeaux mixture", "Copper Sulfate"],
            dosage: "1% solution",
            spraying_interval: "7-10 days",
            description: "🍇 Grapes - General disease protection"
        }
    },
    "Grapes Black Rot": {
        medicine: ["Bordeaux Mixture 1% (CuSO4 + CaOH)", "Mancozeb 75% WP"],
        dosage: "1.5 gm per liter or 1% solution",
        spraying_interval: "7-10 days",
        description: "🍇 Grapes Black Rot Treatment",
        instructions: [
            "1️⃣ Remove infected berries and leaves",
            "2️⃣ Improve air circulation by pruning",
            "3️⃣ Spray from flowering to fruit development stage",
            "4️⃣ Apply Bordeaux paste to pruned wounds",
            "5️⃣ Repeat every 7-10 days in humid conditions"
        ]
    },
    "Grapes Esca (Black Measles)": {
        medicine: ["Sodium Hypochlorite 5%", "Benomyl (if available)", "Trichoderma"],
        dosage: "Apply neat to cut wounds",
        spraying_interval: "Prevention during dormancy",
        description: "🍇 Grapes Esca (Black Measles) Treatment",
        instructions: [
            "1️⃣ No effective spray treatment - mostly preventive",
            "2️⃣ Prune infected branches (cut 30cm below symptoms)",
            "3️⃣ Apply Sodium Hypochlorite to cut surfaces",
            "4️⃣ Disinfect pruning tools between cuts",
            "5️⃣ Remove and burn infected wood",
            "6️⃣ Maintain vine vigor with proper irrigation"
        ]
    },
    "Grapes Leaf Blight": {
        medicine: ["Chlorothalonil 75% WP", "Mancozeb 75% WP", "Triadimefon"],
        dosage: "2 gm per liter (Chlorothalonil) or 1.5 gm per liter (Mancozeb)",
        spraying_interval: "10-14 days",
        description: "🍇 Grapes Leaf Blight Treatment",
        instructions: [
            "1️⃣ Start spraying from fruit set stage",
            "2️⃣ Remove infected leaves",
            "3️⃣ Improve canopy management for air circulation",
            "4️⃣ Spray during dry weather",
            "5️⃣ Alternate fungicides to prevent resistance",
            "6️⃣ Continue until harvest"
        ]
    },
    "Unknown": {
        medicine: "Manual inspection required",
        description: "❓ Unable to identify - Please check the leaf manually",
        instructions: [
            "1️⃣ Take a clear photo of the affected area",
            "2️⃣ Ensure good lighting",
            "3️⃣ Include both healthy and affected parts",
            "4️⃣ Try uploading again"
        ]
    }
};

// ========== WEATHER-BASED MEDICINE ADVISOR ==========
function getWeatherBasedMedicine(cropType, weatherData) {
    let weatherMedicine = null;
    let weatherAdvice = [];

    if (weatherData.humidity > 80) {
        weatherAdvice.push("⚠️ High Humidity (>80%) - Fungal disease risk HIGH");
        if (cropType.includes("Brinjal")) {
            weatherMedicine = medicineRecommendations["Brinjal Healthy Leaf"]["high_humidity"];
        } else if (cropType.includes("Grapes")) {
            weatherMedicine = medicineRecommendations["Grapes Black Rot"]; // Black Rot thrives in humidity
        }
    } else if (weatherData.humidity < 30) {
        weatherAdvice.push("🌵 Low Humidity (<30%) - Pest & mite risk HIGH");
        if (cropType.includes("Brinjal")) {
            weatherMedicine = medicineRecommendations["Brinjal Healthy Leaf"]["low_humidity"];
        }
    }

    if (!weatherMedicine && weatherData.temperature > 35) {
        weatherAdvice.push("🔥 High Temperature (>35°C) - Heat stress risk");
        if (cropType.includes("Brinjal")) {
            weatherMedicine = medicineRecommendations["Brinjal Healthy Leaf"]["high_temp"];
        }
    } else if (!weatherMedicine && weatherData.temperature < 10) {
        weatherAdvice.push("❄️ Low Temperature (<10°C) - Cold stress risk");
    }

    if (weatherData.windSpeed > 20) {
        weatherAdvice.push("💨 High Wind Speed (>20 km/h) - Physical damage risk");
    }

    // Default to healthy prevention if no condition matched
    if (!weatherMedicine) {
        if (cropType.includes("Brinjal")) {
            weatherMedicine = medicineRecommendations["Brinjal Healthy Leaf"]["healthy"];
        } else if (cropType.includes("Grapes")) {
            weatherMedicine = medicineRecommendations["Grapes Healthy"]["healthy"];
        }
    }

    return { weatherMedicine, weatherAdvice };
}

// 5️⃣ WEATHER PAGE
app.get("/weather", (req, res) => {
    res.render("weather", { title: "Weather & Crop Advisory" });
});

// 6️⃣ GET WEATHER DATA (API) - Enhanced with fallback
app.post("/api/weather", async (req, res) => {
    try {
        const { city } = req.body;

        if (!city) {
            return res.status(400).json({ error: "City name is required" });
        }

        let weatherData = null;
        let weatherSource = "mock";

        // Try OpenWeatherMap API first
        try {
            const apiKey = process.env.OPENWEATHER_API_KEY;
            if (apiKey) {
                const response = await axios.get(
                    `https://api.openweathermap.org/data/2.5/weather?q=${city}&appid=${apiKey}&units=metric`,
                    { timeout: 5000 }
                );
                weatherData = response.data;
                weatherSource = "openweathermap";
            }
        } catch (apiError) {
            console.log("⚠️ OpenWeatherMap API unavailable, using mock data");
        }

        // Fallback to mock weather data
        if (!weatherData) {
            weatherSource = "mock";
            weatherData = {
                name: city.charAt(0).toUpperCase() + city.slice(1),
                sys: { country: "IN" },
                main: {
                    temp: 28 + Math.random() * 15,
                    feels_like: 30 + Math.random() * 12,
                    humidity: 50 + Math.random() * 40,
                },
                weather: [{ main: "Partly Cloudy", description: "partly cloudy" }],
                wind: { speed: 5 + Math.random() * 15 },
            };
        }

        const { main, weather, wind } = weatherData;

        // Generate comprehensive crop advisory
        let advisory = [];
        let cropMedicines = {
            "Brinjal": [],
            "Grapes": []
        };

        // Brinjal recommendations
        const brinjal_rec = getWeatherBasedMedicine("Brinjal", main);
        if (brinjal_rec.weatherMedicine) {
            cropMedicines["Brinjal"] = brinjal_rec.weatherMedicine;
        }

        // Grapes recommendations
        const grapes_rec = getWeatherBasedMedicine("Grapes", main);
        if (grapes_rec.weatherMedicine) {
            cropMedicines["Grapes"] = grapes_rec.weatherMedicine;
        }

        // Generic advisories
        if (main.humidity > 80) {
            advisory.push("⚠️ High humidity (>80%) - Risk of fungal diseases. Apply fungicides.");
        }
        if (main.temp < 10) {
            advisory.push("❄️ Low temperature (<10°C) - Ensure proper crop protection.");
        }
        if (wind.speed > 15) {
            advisory.push("💨 Strong winds (>15 km/h) - Risk of physical damage. Monitor crops.");
        }
        if (main.humidity < 30) {
            advisory.push("🌵 Low humidity (<30%) - Increase irrigation frequency. Watch for pests.");
        }
        if (main.temp > 35) {
            advisory.push("🔥 High temperature (>35°C) - Increase irrigation and provide shade if possible.");
        }

        res.json({
            success: true,
            source: weatherSource,
            city: weatherData.name,
            country: weatherData.sys.country,
            temperature: Math.round(main.temp),
            humidity: Math.round(main.humidity),
            condition: weather[0].main,
            description: weather[0].description,
            windSpeed: Math.round(wind.speed * 10) / 10,
            feelsLike: Math.round(main.feels_like),
            advisory: advisory.length > 0 ? advisory : ["✅ Conditions are favorable for crop growth."],
            cropMedicines: cropMedicines,
        });
    } catch (error) {
        console.error("❌ Error fetching weather:", error.message);
        res.status(500).json({
            error: "Failed to fetch weather data",
            details: error.message,
        });
    }
});

// 6️⃣b MEDICINE RECOMMENDATION API
app.post("/api/medicine", async (req, res) => {
    try {
        const { crop, disease, humidity, temperature } = req.body;

        if (!crop || !disease) {
            return res.status(400).json({ error: "Crop and disease information required" });
        }

        let recommendation = medicineRecommendations[disease] || medicineRecommendations["Unknown"];
        let weatherMedicine = null;

        if (humidity && temperature) {
            const weatherRec = getWeatherBasedMedicine(crop, { humidity, temperature, windSpeed: 0 });
            weatherMedicine = weatherRec.weatherMedicine;
        }

        res.json({
            success: true,
            disease: disease,
            crop: crop,
            recommendation: recommendation,
            weatherBasedMedicine: weatherMedicine,
        });
    } catch (error) {
        console.error("❌ Error in medicine recommendation:", error.message);
        res.status(500).json({
            error: "Failed to get medicine recommendation",
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

        // ===== BRINJAL-SPECIFIC RESPONSES =====
        if (lowerMessage.includes("brinjal")) {
            if (
                lowerMessage.includes("disease") ||
                lowerMessage.includes("pest") ||
                lowerMessage.includes("sick")
            ) {
                reply =
                    "🍆 **Brinjal Common Diseases & Treatment:**\n\n" +
                    "🔸 **Shoot and Fruit Borer:**\n" +
                    "- Medicine: Spinosad 45% SC\n" +
                    "- Dosage: 0.5 ml/liter\n" +
                    "- Interval: 7-10 days\n\n" +
                    "🔸 **Leaf Spot:**\n" +
                    "- Medicine: Mancozeb 75% WP\n" +
                    "- Dosage: 2 gm/liter\n" +
                    "- Interval: 10-14 days\n\n" +
                    "🔸 **Yellow Mosaic Virus:**\n" +
                    "- Control vector (whitefly) with Neem oil\n" +
                    "- Dosage: 3-5 ml/liter\n" +
                    "- Remove infected plants immediately";
            } else if (lowerMessage.includes("care") || lowerMessage.includes("grow")) {
                reply =
                    "🍆 **Brinjal Care Guide:**\n\n" +
                    "🌡️ **Temperature:** 20-30°C\n" +
                    "💧 **Watering:** Daily in summer, alternate days in winter\n" +
                    "🌱 **Spacing:** 60cm x 45cm\n" +
                    "🛟 **Soil:** Well-drained, fertile loam\n" +
                    "🌾 **Fertilizer:** NPK 12-32-16 (initial), 10-10-10 (maintenance)\n" +
                    "⏱️ **Harvest:** 70-90 days after transplanting\n\n" +
                    "💡 **Tips:**\n" +
                    "- Mulch to retain moisture\n" +
                    "- Stake for support\n" +
                    "- Prune regularly for better yield";
            } else if (lowerMessage.includes("fertilizer")) {
                reply =
                    "🍆 **Brinjal Fertilizer Recommendations:**\n\n" +
                    "🌱 **Initial Stage:**\n" +
                    "- NPK 12-32-16 (50 kg/hectare)\n\n" +
                    "📈 **Maintenance (after 45 days):**\n" +
                    "- NPK 10-10-10 every 2-3 weeks\n" +
                    "- Urea 46% N (20 kg/hectare) for boost\n\n" +
                    "🌿 **Organic Options:**\n" +
                    "- Vermicompost 5 tons/hectare\n" +
                    "- Neem cake 1 ton/hectare\n\n" +
                    "💧 **Application:** Apply after irrigation for better absorption";
            } else {
                reply =
                    "🍆 **About Brinjal:**\n" +
                    "Brinjal (Eggplant) is a warm-season vegetable crop with high market demand.\n\n" +
                    "Ask me about:\n" +
                    "- 🦠 Diseases & pests\n" +
                    "- 🌱 Care & cultivation\n" +
                    "- 🧪 Fertilizer recommendations";
            }
        }
        // ===== GRAPES-SPECIFIC RESPONSES =====
        else if (lowerMessage.includes("grape")) {
            if (
                lowerMessage.includes("black rot") ||
                (lowerMessage.includes("rot") && lowerMessage.includes("grape"))
            ) {
                reply =
                    "🍇 **Grapes Black Rot Treatment:**\n\n" +
                    "🔸 **Symptoms:**\n" +
                    "- Brown/black spots on berries\n" +
                    "- Concentric rings on fruit\n" +
                    "- Mummified berries\n\n" +
                    "💊 **Medicine:**\n" +
                    "- Bordeaux Mixture 1% (CuSO4 + CaOH)\n" +
                    "- Mancozeb 75% WP\n\n" +
                    "📋 **Application:**\n" +
                    "- Dosage: 1.5 gm/liter\n" +
                    "- Interval: 7-10 days\n" +
                    "- Start from flowering stage\n\n" +
                    "✂️ **Management:**\n" +
                    "1. Remove infected berries & leaves\n" +
                    "2. Improve air circulation by pruning\n" +
                    "3. Apply Bordeaux paste to pruned wounds";
            } else if (
                lowerMessage.includes("esca") ||
                lowerMessage.includes("black measles")
            ) {
                reply =
                    "🍇 **Grapes Esca (Black Measles) Treatment:**\n\n" +
                    "⚠️ **Warning:** No effective spray treatment\n\n" +
                    "🔸 **Symptoms:**\n" +
                    "- Wilting of shoots\n" +
                    "- Dark streaks in wood\n" +
                    "- Slow decline\n\n" +
                    "💊 **Treatment (Mostly Preventive):**\n" +
                    "- Sodium Hypochlorite 5%\n" +
                    "- Apply to cut wounds (neat)\n\n" +
                    "✂️ **Management:**\n" +
                    "1. Prune infected branches (30cm below symptoms)\n" +
                    "2. Disinfect pruning tools between cuts\n" +
                    "3. Apply Sodium Hypochlorite to cuts\n" +
                    "4. Remove & burn infected wood\n" +
                    "5. Maintain vine vigor";
            } else if (lowerMessage.includes("leaf blight")) {
                reply =
                    "🍇 **Grapes Leaf Blight Treatment:**\n\n" +
                    "🔸 **Symptoms:**\n" +
                    "- Brown spots with yellow halo\n" +
                    "- Premature leaf fall\n" +
                    "- Berries cracked\n\n" +
                    "💊 **Medicine:**\n" +
                    "- Chlorothalonil 75% WP\n" +
                    "- Mancozeb 75% WP\n" +
                    "- Triadimefon\n\n" +
                    "📋 **Application:**\n" +
                    "- Dosage: 2 gm/liter (Chlorothalonil) or 1.5 gm/liter (Mancozeb)\n" +
                    "- Interval: 10-14 days\n" +
                    "- Start from fruit set stage\n\n" +
                    "💡 **Tips:**\n" +
                    "- Improve canopy management\n" +
                    "- Alternate fungicides to prevent resistance\n" +
                    "- Continue until harvest";
            } else if (lowerMessage.includes("care") || lowerMessage.includes("grow")) {
                reply =
                    "🍇 **Grapes Care Guide:**\n\n" +
                    "🌡️ **Temperature:** 10-30°C\n" +
                    "💧 **Watering:** Drip irrigation recommended, 50-60 liters/day per plant\n" +
                    "🌱 **Spacing:** 2m x 2m (trellised), 1.5m x 2m (pergola)\n" +
                    "🛟 **Soil:** Well-drained loam, pH 6.5-7.5\n" +
                    "🌾 **Fertilizer:** NPK 12-8-10\n" +
                    "⏱️ **Yield:** Fruit set at 2-3 years\n\n" +
                    "💡 **Tips:**\n" +
                    "- Pruning essential for quality\n" +
                    "- Thinning of berries improves size\n" +
                    "- Avoid overhead irrigation";
            } else if (lowerMessage.includes("fertilizer")) {
                reply =
                    "🍇 **Grapes Fertilizer Recommendations:**\n\n" +
                    "🌱 **Young Vines (1-3 years):**\n" +
                    "- NPK 12-8-10\n" +
                    "- 200g per vine per month\n\n" +
                    "📈 **Bearing Vines (>3 years):**\n" +
                    "- NPK 12-8-10\n" +
                    "- 500-1000g per vine per season\n\n" +
                    "🌿 **Split Application:**\n" +
                    "- Start: After budbreak\n" +
                    "- During bloom: N only\n" +
                    "- After fruit set: Full NPK\n\n" +
                    "💧 **Application Method:**\n" +
                    "- Fertigation through drip system\n" +
                    "- Soil application for annual vines";
            } else if (lowerMessage.includes("healthy")) {
                reply =
                    "🍇 **Grapes Healthy Maintenance:**\n\n" +
                    "✅ **Preventive Measures:**\n" +
                    "- Sulfur powder spray every 10-14 days\n" +
                    "- Dosage: 2.5-3 gm/liter\n" +
                    "- Best for powdery mildew prevention\n\n" +
                    "🛡️ **Disease Prevention:**\n" +
                    "- Bordeaux mixture 1% for general protection\n" +
                    "- Copper Sulfate for fungal issues\n\n" +
                    "💡 **Key Practices:**\n" +
                    "- Maintain good air circulation\n" +
                    "- Remove diseased leaves promptly\n" +
                    "- Monitor regularly for pests";
            } else {
                reply =
                    "🍇 **About Grapes:**\n" +
                    "Grapes are premium fruit crops with diverse varieties and uses.\n\n" +
                    "Ask me about:\n" +
                    "- 🦠 Diseases: Black Rot, Esca, Leaf Blight\n" +
                    "- 🌱 Care & cultivation\n" +
                    "- 🧪 Fertilizer recommendations\n" +
                    "- 💪 Healthy plant maintenance";
            }
        }
        // ===== GENERAL RESPONSES =====
        else if (lowerMessage.includes("crop") && !lowerMessage.includes("brinjal") && !lowerMessage.includes("grape")) {
            reply =
                "🌾 **Crop Care Tips:**\n" +
                "- Water regularly (morning or evening)\n" +
                "- Use nitrogen-rich fertilizers\n" +
                "- Maintain soil pH 6.0-7.0\n" +
                "- Rotate crops annually\n\n" +
                "🎯 **Specific Crops:**\n" +
                "- Ask about **Brinjal** care\n" +
                "- Ask about **Grapes** cultivation";
        } else if (lowerMessage.includes("disease")) {
            reply =
                "🦠 **Disease Management Tips:**\n" +
                "- Identify symptoms early\n" +
                "- Use fungicides for fungal diseases\n" +
                "- Apply insecticides for pests\n" +
                "- Remove infected leaves\n\n" +
                "🎯 **Specific Diseases:**\n" +
                "- Ask about **Brinjal** diseases\n" +
                "- Ask about **Grapes** diseases (Black Rot, Esca, Leaf Blight)";
        } else if (lowerMessage.includes("fertilizer")) {
            reply =
                "🌱 **Fertilizer Guide:**\n" +
                "- NPK (Nitrogen-Phosphorus-Potassium) ratio for general crops: 10-10-10\n" +
                "- Apply every 2-3 weeks\n" +
                "- Use compost for organic farming\n\n" +
                "🎯 **Crop-Specific:**\n" +
                "- Ask about **Brinjal** fertilizer\n" +
                "- Ask about **Grapes** fertilizer";
        } else if (lowerMessage.includes("pesticide") || lowerMessage.includes("pest")) {
            reply =
                "🚫 **Pest Control:**\n" +
                "- Neem oil for common pests\n" +
                "- Pyrethrin-based sprays for insects\n" +
                "- Copper sulfate for fungal issues\n" +
                "- Use as per label instructions\n\n" +
                "💡 **Tips:**\n" +
                "- Spray early morning or late evening\n" +
                "- Avoid spraying in rain\n" +
                "- Wear protective gear";
        } else if (
            lowerMessage.includes("hello") ||
            lowerMessage.includes("hi") ||
            lowerMessage.includes("hey")
        ) {
            reply =
                "👋 Hello! I'm the DualCrop AI Assistant.\n\n" +
                "I can help you with:\n" +
                "🍆 **Brinjal** - care, diseases, fertilizers\n" +
                "🍇 **Grapes** - care, diseases, fertilizers\n" +
                "🦠 Disease identification & treatment\n" +
                "🌱 Crop care & management\n" +
                "🧪 Fertilizer recommendations\n\n" +
                "What would you like to know?";
        } else if (
            lowerMessage.includes("weather") ||
            lowerMessage.includes("rain") ||
            lowerMessage.includes("temperature")
        ) {
            reply =
                "🌦️ **Weather Advisory:**\n" +
                "- Check weather before spraying\n" +
                "- Avoid spray during rain\n" +
                "- Morning/evening is best for application\n" +
                "- Temperature >35°C: Increase irrigation\n" +
                "- Humidity >80%: Risk of fungal disease\n\n" +
                "💡 **Crop-Specific:**\n" +
                "- Brinjal: 20-30°C optimal\n" +
                "- Grapes: 10-30°C optimal";
        } else if (lowerMessage.includes("help")) {
            reply =
                "📖 **How to use DualCrop AI Assistant:**\n\n" +
                "Ask questions about:\n" +
                "🍆 **Brinjal** - diseases, care, fertilizers\n" +
                "🍇 **Grapes** - Black Rot, Esca, Leaf Blight\n" +
                "🌾 General crop care tips\n" +
                "💊 Medicine & treatment recommendations\n\n" +
                "Example questions:\n" +
                "- What about brinjal diseases?\n" +
                "- How to treat grape black rot?\n" +
                "- What fertilizer for grapes?";
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