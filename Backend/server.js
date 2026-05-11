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
const { getSmartChatbotResponseInLanguage } = require("./language-responses");

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

// ========== CLASS NAME MAPPING ==========
// Map raw class names from model to display names for UI
const classNameMapping = {
    "brinjal_Healthy Leaf": "Brinjal Healthy Leaf",
    "Grapes_Grape": "Grapes Healthy",
    "Grapes_Grape___Black_rot": "Grapes Black Rot",
    "Grapes_Grape___Esca_(Black_Measles)": "Grapes Esca (Black Measles)",
    "Grapes_Grape___healthy": "Grapes Healthy",
    "Grapes_Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Grapes Leaf Blight"
};

function getDisplayName(rawPrediction) {
    return classNameMapping[rawPrediction] || rawPrediction;
}

function getRawPredictionKey(displayName) {
    for (const [raw, display] of Object.entries(classNameMapping)) {
        if (display === displayName) {
            return raw;
        }
    }
    return displayName;
}

// ========== PREDICTION FALLBACK (MOCK DATA) ==========
function getFallbackPrediction(filename) {
    // Fallback predictions based on filename pattern - using raw class names now
    const fallbackPredictions = {
        "healthy": { prediction: "brinjal_Healthy Leaf", confidence: 92.5 },
        "black_rot": { prediction: "Grapes_Grape___Black_rot", confidence: 88.3 },
        "esca": { prediction: "Grapes_Grape___Esca_(Black_Measles)", confidence: 85.6 },
        "leaf_blight": { prediction: "Grapes_Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", confidence: 87.9 },
        "rot": { prediction: "Grapes_Grape___Black_rot", confidence: 85.2 },
    };

    const lowerFilename = filename.toLowerCase();
    for (const [key, value] of Object.entries(fallbackPredictions)) {
        if (lowerFilename.includes(key)) {
            return value;
        }
    }

    // Default fallback
    return { prediction: "Grapes_Grape", confidence: 50.0 };
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

        // Get medicine recommendation using raw prediction name
        const medicineRec = medicineRecommendations[prediction] || medicineRecommendations["Unknown"];

        // Generate detailed comprehensive recommendation
        const detailedRec = generateDetailedRecommendation(prediction, confidence);

        // Convert raw prediction to display name for UI
        const displayPrediction = getDisplayName(prediction);

        // Save to MySQL database (use display name for human readability)
        try {
            const connection = await pool.getConnection();
            const query =
                "INSERT INTO predictions (image, result, confidence) VALUES (?, ?, ?)";
            await connection.execute(query, [req.file.filename, displayPrediction, confidence]);
            connection.release();
            console.log("✅ Prediction saved to database");
        } catch (dbError) {
            console.warn("⚠️ Database save failed:", dbError.message);
            // Continue anyway, database is optional for prediction
        }

        // ✅ Keep uploaded file for dashboard display
        console.log("✅ Image saved to: /uploads/" + req.file.filename);

        // Return JSON response with detailed recommendations
        res.json({
            success: true,
            image: req.file.filename,
            prediction: displayPrediction,  // Show display name to user
            rawPrediction: prediction,       // Keep raw prediction for debugging
            confidence: confidence,
            medicine: medicineRec,
            recommendation: detailedRec,     // NEW: Comprehensive recommendation
            flaskAvailable: flaskAvailable,
            note: flaskAvailable ? "Prediction from Flask AI Model" : "Prediction from fallback system"
        });

    } catch (error) {
        console.error("❌ Critical Error:", error.message);

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
            "SELECT id, image, result AS prediction, confidence, created_at FROM predictions ORDER BY created_at DESC LIMIT 100"
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

// ========== ENHANCED RECOMMENDATION ENGINE ==========
// Generate detailed, comprehensive recommendations based on disease
function generateDetailedRecommendation(prediction, confidence) {
    const recommendations = {
        "brinjal_Healthy Leaf": {
            status: "✅ HEALTHY",
            severity: "LOW",
            color: "success",
            summary: "Your brinjal crop is in excellent condition",
            detailed_analysis: "The plant shows no signs of major diseases. Maintain current care practices.",
            treatment: {
                immediate: "No immediate treatment required",
                prevention: [
                    "🛡️ Apply Neem oil spray every 15 days for pest prevention",
                    "💧 Maintain consistent irrigation (daily in summer)",
                    "🌿 Use organic NPK 10-10-10 fertilizer every 30 days",
                    "🧹 Remove fallen leaves and debris to prevent fungal growth"
                ],
                organic_alternatives: [
                    "Spray solution: Mix 5% Neem oil with 1% Potassium soap",
                    "Biological control: Release Trichoderma fungi",
                    "Manual control: Hand-pick any visible pests daily"
                ],
                cost_effective: [
                    "Use local cow dung compost instead of fertilizer",
                    "Mix crushed garlic and chili with water for pest spray",
                    "Save seeds for next season from healthy plants"
                ]
            },
            fertilizer: {
                type: "Balanced NPK",
                recommendation: "Apply 10-10-10 NPK every 30 days",
                amount: "500-600g per plant",
                timing: "Every 4 weeks throughout growing season"
            },
            irrigation: {
                frequency: "Daily in summer, alternate days in monsoon",
                method: "Drip or soaker hose",
                amount: "20-25 liters per plant per day",
                best_time: "Early morning or evening"
            },
            companion_plants: [
                "🌿 Marigold - Repels pests",
                "🌿 Basil - Improves plant vigor",
                "🌿 Garlic - Natural pest deterrent"
            ],
            expected_yield: "4-5 kg per plant (60-70 tons per hectare)",
            harvest_ready: "In 70-90 days from transplanting"
        },
        "Grapes_Grape": {
            status: "✅ HEALTHY",
            severity: "LOW",
            color: "success",
            summary: "Your grapes are in excellent health",
            detailed_analysis: "No disease symptoms detected. Excellent condition for fruit development.",
            treatment: {
                immediate: "No treatment needed",
                prevention: [
                    "🛡️ Apply sulfur powder spray every 10-14 days",
                    "💧 Drip irrigation - 50-60 liters per plant daily",
                    "🌿 Balanced NPK 12-8-10 fertilizer every 20 days",
                    "✂️ Prune excess shoots for air circulation"
                ],
                organic_alternatives: [
                    "Sulfur powder mixed with water spray",
                    "Bordeaux mixture (1%) as preventive",
                    "Beneficial insects like ladybugs"
                ],
                cost_effective: [
                    "Use composted grape waste for fertilizer",
                    "Water mulching with dried leaves to retain moisture",
                    "Share pest management resources with neighboring farmers"
                ]
            },
            fertilizer: {
                type: "High Potassium blend",
                recommendation: "NPK 12-8-10, apply every 20 days",
                amount: "2-3 kg per mature plant",
                timing: "During growing and fruiting season"
            },
            irrigation: {
                frequency: "Daily drip irrigation",
                method: "Drip irrigation system (RECOMMENDED)",
                amount: "50-60 liters per plant daily",
                best_time: "Early morning (4-6 AM)"
            },
            trellising: [
                "🌳 Maintain grape trellis at 6-8 feet height",
                "🌳 Proper canopy management for light exposure",
                "🌳 Remove excess lateral shoots monthly"
            ],
            expected_yield: "8-10 kg per plant (25-30 tons per hectare)",
            harvest_ready: "In 5-7 years from planting"
        },
        "Grapes_Grape___healthy": {
            status: "✅ HEALTHY",
            severity: "LOW",
            color: "success",
            summary: "Your grapes are in excellent health",
            detailed_analysis: "No disease symptoms detected. Excellent condition for fruit development.",
            treatment: {
                immediate: "No treatment needed",
                prevention: [
                    "🛡️ Apply sulfur powder spray every 10-14 days",
                    "💧 Drip irrigation - 50-60 liters per plant daily",
                    "🌿 Balanced NPK 12-8-10 fertilizer every 20 days"
                ],
                organic_alternatives: [
                    "Sulfur powder spray for fungal prevention",
                    "Bordeaux mixture every 15 days"
                ],
                cost_effective: [
                    "Use composted organic matter",
                    "Water mulching technique",
                    "Community pest management"
                ]
            },
            fertilizer: {
                type: "High Potassium blend",
                recommendation: "NPK 12-8-10",
                amount: "2-3 kg per plant",
                timing: "Every 20 days during season"
            },
            irrigation: {
                frequency: "Daily drip irrigation",
                amount: "50-60 liters per plant",
                best_time: "Early morning"
            },
            expected_yield: "8-10 kg per plant",
            harvest_ready: "In 5-7 years"
        },
        "Grapes_Grape___Black_rot": {
            status: "🔴 DISEASED",
            severity: "HIGH",
            color: "danger",
            summary: "Black Rot infection detected - Immediate action required",
            detailed_analysis: "Black rot is a serious fungal disease that affects berries and leaves. It thrives in humid conditions. Quick action is essential to prevent crop loss.",
            treatment: {
                immediate: [
                    "🚨 Remove all infected berries and leaves immediately",
                    "🚨 Cut affected branches 30cm below visible symptoms",
                    "🚨 Burn or bury removed parts (DO NOT compost)",
                    "🚨 Disinfect pruning tools with bleach solution (1:10 ratio)"
                ],
                chemical: {
                    medicine: ["Bordeaux Mixture 1% (CuSO4 + CaOH)", "Mancozeb 75% WP", "Copper Hydroxide 77%"],
                    dosage: "1-1.5 gm per liter",
                    spraying_interval: "Every 7-10 days",
                    duration: "Continue for 4-6 weeks or until harvest"
                },
                organic_alternatives: [
                    "Bordeaux mixture (1% solution) - Most effective",
                    "Copper sulfate spray - Every 7 days",
                    "Bacillus subtilis biological fungicide"
                ],
                preventive: [
                    "✋ Reduce humidity through proper pruning",
                    "✋ Improve canopy air circulation",
                    "✋ Remove fallen leaves and debris daily",
                    "✋ Avoid overhead irrigation (use drip)",
                    "✋ Space plants properly for air flow"
                ]
            },
            application_schedule: {
                week_1: "Bordeaux Mixture - 3 sprays (days 1, 4, 7)",
                week_2: "Mancozeb - 2 sprays (days 10, 14)",
                week_3_onwards: "Alternate between Bordeaux and Mancozeb every 7 days"
            },
            irrigation: {
                change: "Use drip irrigation (mandatory)",
                timing: "Only early morning, never evening",
                frequency: "40-50 liters per plant daily"
            },
            cost_effective: [
                "Use Bordeaux mixture (cheaper than synthetic)",
                "Buy fungicides in bulk with neighboring farmers",
                "Make own Bordeaux: CuSO4 (1kg) + CaOH (1.5kg) per 100L water"
            ],
            cost_estimate: "₹800-1200 per plant for full treatment",
            expected_recovery: "2-3 weeks with proper application",
            yield_impact: "30-50% loss if untreated"
        },
        "Grapes_Grape___Esca_(Black_Measles)": {
            status: "🟠 SERIOUS",
            severity: "CRITICAL",
            color: "danger",
            summary: "Esca (Black Measles) detected - Very serious condition",
            detailed_analysis: "Esca is a wood-rotting disease that is very difficult to treat. Once infected, the plant may decline slowly. Prevention and early removal are key.",
            treatment: {
                immediate: [
                    "⚠️ This disease is HARD to cure - focus on PREVENTION",
                    "⚠️ Remove infected branches (cut 50cm below symptoms)",
                    "⚠️ Apply wound dressing immediately after cutting",
                    "⚠️ Maintain overall plant health through good irrigation"
                ],
                chemical: {
                    note: "No effective chemical cure available",
                    option1: "Sodium Hypochlorite 5% - Apply to cut wounds",
                    option2: "Benomyl (if available in your region)",
                    option3: "Trichoderma fungi - Biological control"
                },
                cultural_control: [
                    "🌳 Remove diseased vines completely if heavily infected",
                    "🌳 Apply wound sealant (paint/paste) to all cuts",
                    "🌳 Maintain high plant vigor through nutrition",
                    "🌳 Avoid any wounding of the plant",
                    "🌳 Don't propagate from infected vines"
                ],
                preventive: [
                    "Proper drainage to prevent root stress",
                    "Balanced irrigation - not too much water",
                    "Avoid physical damage to trunk and branches",
                    "Sterilize all pruning tools between plants",
                    "Use disease-free planting material"
                ]
            },
            long_term_strategy: [
                "Monitor plant for symptom progression",
                "Keep infected plant in isolation (don't spread)",
                "If decline continues, consider replanting",
                "Plant resistant or tolerant varieties next time",
                "Maintain distance between plantings"
            ],
            cost_effective: [
                "Focus on prevention rather than cure",
                "Proper spacing saves money on treatment",
                "Good hygiene costs less than fungicides",
                "Share equipment sterilization with other farmers"
            ],
            prognosis: "50-70% of infected plants show slow decline",
            timeline: "Symptoms may take 2-5 years to manifest completely"
        },
        "Grapes_Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
            status: "🟡 MODERATE",
            severity: "MEDIUM",
            color: "warning",
            summary: "Leaf Blight detected - Needs prompt treatment",
            detailed_analysis: "Leaf blight affects grape foliage, reducing photosynthesis and weakening the plant. Can be controlled with regular fungicide sprays.",
            treatment: {
                immediate: [
                    "🔧 Remove all heavily infected leaves",
                    "🔧 Thin out canopy to improve air circulation",
                    "🔧 Clean up fallen leaves and debris",
                    "🔧 Increase spacing between vines if needed"
                ],
                chemical: {
                    primary: ["Chlorothalonil 75% WP", "Mancozeb 75% WP"],
                    alternate: ["Triadimefon 25% EC", "Propiconazole 25% EC"],
                    dosage: "2 gm per liter (Chlorothalonil) or 1.5 gm per liter (Mancozeb)",
                    spraying_interval: "Every 10-14 days",
                    duration: "Continue from fruit set until harvest"
                },
                application_schedule: {
                    phase1: "First 2 weeks: Spray every 7 days (heavy infection)",
                    phase2: "Weeks 3-8: Spray every 10 days (maintenance)",
                    phase3: "Weeks 9-onwards: Spray every 14 days (preventive)"
                },
                organic_alternatives: [
                    "Sulfur powder spray - Every 10 days",
                    "Copper-based fungicide (Copper Hydroxide)",
                    "Bacillus subtilis - Biological control",
                    "Neem oil + Potassium soap mix"
                ],
                preventive: [
                    "✅ Proper canopy management - Remove excess growth",
                    "✅ Space plants 2-2.5m apart for air flow",
                    "✅ Use drip irrigation (avoid wetting leaves)",
                    "✅ Remove infected leaves as they appear",
                    "✅ Don't work in wet vineyard to prevent spread"
                ]
            },
            seasonal_variation: {
                monsoon: "HIGH RISK - Spray every 7 days",
                summer: "MEDIUM RISK - Spray every 10 days",
                winter: "LOW RISK - Spray every 14 days"
            },
            cost_estimate: "₹400-600 per plant for full season treatment",
            expected_recovery: "1-2 weeks after starting treatment",
            yield_protection: "Prevent 30-40% yield loss with timely treatment"
        }
    };

    const rec = recommendations[prediction];
    if (rec) {
        rec.confidence = confidence.toFixed(1);
        rec.confidence_level = confidence > 85 ? "Very High" : confidence > 70 ? "High" : confidence > 50 ? "Medium" : "Low";
        rec.recommendation_generated_at = new Date().toISOString();
    }
    
    return rec || {
        status: "❓ UNKNOWN",
        severity: "UNKNOWN",
        summary: "Unable to identify the condition. Please provide a clearer image.",
        treatment: {
            immediate: "Please upload a clear image with proper lighting",
            prevention: [
                "🔍 Take close-up photo of affected area",
                "🔍 Ensure good natural lighting",
                "🔍 Include both healthy and diseased parts",
                "🔍 Keep image in focus"
            ]
        }
    };
}

// Create aliases for raw class names by pointing to display name keys
medicineRecommendations["brinjal_Healthy Leaf"] = medicineRecommendations["Brinjal Healthy Leaf"];
medicineRecommendations["Grapes_Grape"] = medicineRecommendations["Grapes Healthy"];
medicineRecommendations["Grapes_Grape___healthy"] = medicineRecommendations["Grapes Healthy"];
medicineRecommendations["Grapes_Grape___Black_rot"] = medicineRecommendations["Grapes Black Rot"];
medicineRecommendations["Grapes_Grape___Esca_(Black_Measles)"] = medicineRecommendations["Grapes Esca (Black Measles)"];
medicineRecommendations["Grapes_Grape___Leaf_blight_(Isariopsis_Leaf_Spot)"] = medicineRecommendations["Grapes Leaf Blight"];

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

// 8️⃣ CHATBOT API - ADVANCED AI RESPONSE ENGINE
app.post("/api/chat", (req, res) => {
    try {
        const { message, language = 'en' } = req.body;
        if (!message) {
            return res.status(400).json({ error: "Message is required" });
        }

        const lowerMessage = message.toLowerCase().trim();
        let reply;
        
        // Use English detailed responses, fallback to language-specific for other languages
        if (language === 'en') {
            reply = getSmartChatbotResponse(lowerMessage);
        } else {
            reply = getSmartChatbotResponseInLanguage(lowerMessage, language);
        }

        res.json({
            success: true,
            message: message,
            reply: reply,
            language: language
        });
    } catch (error) {
        console.error("❌ Error in chatbot:", error.message);
        res.status(500).json({ error: "Chatbot error occurred" });
    }
});

// ===== SMART CHATBOT RESPONSE FUNCTION =====
function getSmartChatbotResponse(message) {
    // Extract keywords
    const words = message.split(/[\s,?!.]+/).filter(w => w.length > 0);
    
    // Detect crop type
    const isBrinjal = hasBrinjalKeyword(message);
    const isGrape = hasGrapeKeyword(message);
    
    // Detect question type - improved detection
    const isWhyQuestion = message.includes("why") || message.includes("importance") || message.includes("benefit");
    const isUseQuestion = message.includes("use") || message.includes("uses") || message.includes("purpose");
    const isHowQuestion = message.includes("how") || message.includes("can i") || message.includes("should i") || message.includes("grow") || message.includes("cultivate");
    const isWhatQuestion = message.includes("what") || message.includes("which") || message.includes("tell");
    const isWhenQuestion = message.includes("when") || message.includes("time") || message.includes("best time");
    
    // Detect topics
    const isDiseaseQuestion = hasKeyword(message, ["disease", "pest", "rot", "blight", "spot", "virus", "yellowing", "wilting", "affected", "sick", "problem", "damage", "infected", "treatment", "medicine"]);
    const isCareQuestion = hasKeyword(message, ["care", "grow", "growing", "cultivate", "plant", "plantation", "maintain", "management", "farming", "how to grow", "how to plant", "cultivation"]);
    const isFertilizerQuestion = hasKeyword(message, ["fertilizer", "fertilise", "npk", "nutrient", "nutrition", "feed", "feeding", "manure", "compost", "fertilization"]);
    const isYieldQuestion = hasKeyword(message, ["yield", "production", "harvest", "crop yield", "profit", "income", "economics"]);
    const isTemperatureQuestion = hasKeyword(message, ["temperature", "temp", "heat", "weather", "climate", "cold", "frost", "celsius"]);
    const isWaterQuestion = hasKeyword(message, ["water", "irrigation", "watering", "rain", "moisture", "dry", "drought"]);
    
    // Greeting
    if (hasKeyword(message, ["hello", "hi", "hey", "greetings", "namaste", "good morning", "good afternoon", "good evening"])) {
        return "👋 **Hello!** Welcome to DualCrop AI Assistant.\n\n" +
            "I'm here to help you with:\n" +
            "🍆 **Brinjal** - Growing, diseases, fertilizers\n" +
            "🍇 **Grapes** - Cultivation, diseases, care\n\n" +
            "What would you like to know today?";
    }

    // Help request
    if (hasKeyword(message, ["help", "guide", "tutorial", "how to use", "explain"])) {
        return "📖 **DualCrop AI Assistant Guide:**\n\n" +
            "🍆 **Ask about Brinjal:**\n" +
            "- How to grow brinjal?\n" +
            "- What diseases affect brinjal?\n" +
            "- What fertilizer for brinjal?\n" +
            "- Why grow brinjal?\n" +
            "- What is use of brinjal?\n\n" +
            "🍇 **Ask about Grapes:**\n" +
            "- How to cultivate grapes?\n" +
            "- Tell me about grape diseases\n" +
            "- What fertilizer for grapes?\n" +
            "- Best time to plant grapes?\n" +
            "- Why grow grapes?\n\n" +
            "💡 **Other Topics:**\n" +
            "- Weather advisory\n" +
            "- Pest control methods\n" +
            "- Irrigation techniques";
    }

    // ===== BRINJAL RESPONSES =====
    if (isBrinjal) {
        // Why/Importance/Use questions
        if (isWhyQuestion || isUseQuestion) {
            return "🍆 **Why Grow Brinjal? Uses & Benefits:**\n\n" +
                "✅ **Economic Benefits:**\n" +
                "- High market demand & good prices\n" +
                "- Multiple harvests per year (6-8 months)\n" +
                "- Good profit margin (₹3-5 lakh per hectare)\n" +
                "- Year-round availability in markets\n" +
                "- Quick returns on investment\n\n" +
                "✅ **Agricultural Benefits:**\n" +
                "- Warm-season vegetable crop\n" +
                "- Suitable for diverse climates\n" +
                "- Good soil improvement potential\n" +
                "- Companion planting benefits\n" +
                "- Less pest pressure than other crops\n\n" +
                "✅ **Nutritional & Health Benefits:**\n" +
                "- Rich in vitamins (A, B, C)\n" +
                "- Minerals: Potassium, Manganese, Copper\n" +
                "- Low calories (25 cal/100g)\n" +
                "- High dietary fiber\n" +
                "- Antioxidants & anti-inflammatory properties\n" +
                "- Good for digestion & heart health\n\n" +
                "✅ **Industrial Uses:**\n" +
                "- Food industry (fresh & processed)\n" +
                "- Pickle & preserve production\n" +
                "- Export market for fresh produce";
        }
        // Disease questions
        else if (isDiseaseQuestion) {
            return "🍆 **Brinjal Common Diseases & Treatment:**\n\n" +
                "🔴 **Shoot and Fruit Borer** (Most Common)\n" +
                "- Symptom: Holes in fruits & shoots\n" +
                "- Medicine: Spinosad 45% SC (0.5 ml/L)\n" +
                "- Spray: Every 7-10 days\n" +
                "- Best Time: Early morning or evening\n\n" +
                "🔴 **Leaf Spot Disease**\n" +
                "- Symptom: Brown/gray spots on leaves\n" +
                "- Medicine: Mancozeb 75% WP (2 gm/L)\n" +
                "- Spray: Every 10-14 days\n" +
                "- Prevention: Remove infected leaves\n\n" +
                "🔴 **Yellow Mosaic Virus**\n" +
                "- Symptom: Yellow patterns on leaves\n" +
                "- Cause: Whitefly transmission\n" +
                "- Control: Remove whiteflies with Neem oil (3-5 ml/L)\n" +
                "- Prevention: Destroy infected plants immediately\n" +
                "- Vector Control: Spray for whiteflies\n\n" +
                "🔴 **Damping Off (Seedling)**\n" +
                "- Symptom: Seedlings wilt at soil level\n" +
                "- Medicine: Trichoderma (bio-fungicide)\n" +
                "- Prevention: Use sterile soil, proper drainage\n\n" +
                "💡 **Prevention Tips:**\n" +
                "- Use healthy, certified seeds\n" +
                "- Maintain field hygiene\n" +
                "- Regular monitoring (weekly)\n" +
                "- Remove diseased plants immediately\n" +
                "- Crop rotation (2-3 years)";
        }
        // Care/Growing questions
        else if (isCareQuestion || isHowQuestion) {
            return "🍆 **How to Grow Brinjal - Complete Guide:**\n\n" +
                "🌡️ **Climate & Temperature:**\n" +
                "- Optimal: 20-30°C\n" +
                "- Requires warmth & sunlight\n" +
                "- Avoid frost areas\n" +
                "- Min: 15°C, Max: 35°C\n\n" +
                "🌱 **Planting Guide:**\n" +
                "- Sowing: June-August\n" +
                "- Spacing: 60cm x 45cm (Row x Plant)\n" +
                "- Transplanting: 30-40 days after sowing\n" +
                "- Seeds per hectare: 500-600g\n" +
                "- Seed rate: 400-500g/hectare\n" +
                "- Depth: 2-3 cm\n\n" +
                "💧 **Watering Schedule:**\n" +
                "- Summer: Daily or alternate days\n" +
                "- Winter: Every 3-4 days\n" +
                "- Total requirement: 600-800mm per season\n" +
                "- 25-35 irrigations needed\n" +
                "- Drip irrigation recommended\n\n" +
                "🛟 **Soil Requirements:**\n" +
                "- Well-drained loamy soil\n" +
                "- pH: 5.5-7.5\n" +
                "- Good organic matter (5-10 tons/hectare)\n" +
                "- Avoid waterlogged areas\n\n" +
                "⏱️ **Harvest Time:**\n" +
                "- 70-90 days after transplanting\n" +
                "- Pick when glossy, before maturity\n" +
                "- Multiple pickings for 6-8 months\n" +
                "- Yield: 25-30 tons/hectare\n\n" +
                "💡 **Additional Care:**\n" +
                "- Mulching helps retain moisture\n" +
                "- Staking for support in windy areas\n" +
                "- Pruning for better yield\n" +
                "- Regular weeding (4-5 times)";
        }
        // Fertilizer questions
        else if (isFertilizerQuestion) {
            return "🍆 **Brinjal Fertilizer Schedule:**\n\n" +
                "📋 **Initial Application (At Planting):**\n" +
                "- FYM: 20-25 tons/hectare\n" +
                "- Neem cake: 1-2 tons/hectare\n" +
                "- NPK 12-32-16: 50 kg/hectare\n" +
                "- Bone meal: 500 kg/hectare\n\n" +
                "📈 **Maintenance Fertilizer (Monthly):**\n" +
                "- NPK 10-10-10: Every 2-3 weeks\n" +
                "- Urea 46% N: 20 kg/hectare\n" +
                "- Potash: 15 kg/hectare\n" +
                "- Micronutrients: Zn, B, Fe as needed\n\n" +
                "🌿 **Organic Approach:**\n" +
                "- Vermicompost: 5 tons/hectare\n" +
                "- Bio-fertilizers (Azospirillum)\n" +
                "- Foliar spray: 2-3 times during season\n" +
                "- Cow dung compost: 10 tons/hectare\n\n" +
                "💡 **Application Tips:**\n" +
                "- Apply fertilizer after irrigation\n" +
                "- Avoid direct contact with stems\n" +
                "- Best time: Early morning or evening\n" +
                "- Split applications for better absorption\n" +
                "- Liquid fertilizers work faster";
        }
        // Yield/profit questions
        else if (isYieldQuestion) {
            return "🍆 **Brinjal Yield & Economics:**\n\n" +
                "📊 **Expected Yield:**\n" +
                "- Per hectare: 25-30 tons fresh fruit\n" +
                "- Per plant: 2-3 kg over season\n" +
                "- Multiple harvests: 6-8 months duration\n" +
                "- Harvesting period: 4-5 pickings\n\n" +
                "💰 **Economics (Per Hectare):**\n" +
                "- Total investment: ₹80,000-1,00,000\n" +
                "- Annual revenue: ₹3-5 lakhs\n" +
                "- Net profit: ₹2-4 lakhs\n" +
                "- ROI: 200-300%\n" +
                "- Payback period: 6-8 months\n\n" +
                "📈 **Profit Factors:**\n" +
                "- Market timing (peak season = higher prices)\n" +
                "- Quality of produce (size, color, freshness)\n" +
                "- Proper disease management\n" +
                "- Irrigation efficiency\n" +
                "- Transportation & storage\n\n" +
                "💹 **Market Prices:**\n" +
                "- Peak season: ₹15-25 per kg\n" +
                "- Off-season: ₹25-40 per kg\n" +
                "- Average: ₹20 per kg\n\n" +
                "🎯 **To Maximize Yield:**\n" +
                "- Use quality seeds\n" +
                "- Proper spacing & pruning\n" +
                "- Timely disease management\n" +
                "- Regular monitoring & care\n" +
                "- Use drip irrigation";
        }
        // Water/irrigation questions
        else if (isWaterQuestion) {
            return "🍆 **Brinjal Water Management:**\n\n" +
                "💧 **Irrigation Schedule:**\n" +
                "- **Summer:** Daily or alternate days\n" +
                "- **Winter:** Every 3-4 days\n" +
                "- **Monsoon:** Only if drought\n" +
                "- **Frequency:** 25-35 irrigations per season\n\n" +
                "📊 **Water Requirements:**\n" +
                "- Total per season: 600-800mm\n" +
                "- 50-60 liters per plant per day (summer)\n" +
                "- Critical stages: Flowering & fruiting\n\n" +
                "🌊 **Irrigation Methods:**\n" +
                "- **Drip Irrigation:** Most efficient (50-60% water saving)\n" +
                "- **Furrow:** Traditional, 40-50% saving\n" +
                "- **Sprinkler:** 25-30% water saving\n" +
                "- **Manual:** 10-20% water saving\n\n" +
                "⏰ **Best Timing:**\n" +
                "- Early morning: 4-7 AM (best)\n" +
                "- Late evening: 4-6 PM (acceptable)\n" +
                "- Avoid: Midday irrigation\n" +
                "- Reduce: During rainy season\n\n" +
                "⚠️ **Signs of Water Stress:**\n" +
                "- Wilting during day\n" +
                "- Leaf yellowing\n" +
                "- Flower/fruit drop\n" +
                "- Stunted growth";
        }
        // Temperature questions
        else if (isTemperatureQuestion) {
            return "🍆 **Brinjal Temperature Management:**\n\n" +
                "🌡️ **Optimal Temperature:**\n" +
                "- Growing: 20-30°C (ideal)\n" +
                "- Minimum: 15°C\n" +
                "- Maximum: 35°C\n" +
                "- Frost: Kills the plant\n\n" +
                "🔥 **Heat Stress Management:**\n" +
                "- Temperature >32°C: Provide shade\n" +
                "- Increase irrigation frequency\n" +
                "- Use mulching (5-10 cm)\n" +
                "- Avoid excessive pruning\n" +
                "- Plant windbreaks\n\n" +
                "❄️ **Cold/Frost Management:**\n" +
                "- Avoid frost-prone areas\n" +
                "- Sow in appropriate season\n" +
                "- Use plastic mulch\n" +
                "- Avoid early sowing\n\n" +
                "🌤️ **Weather Impact:**\n" +
                "- High humidity: Disease risk\n" +
                "- Low humidity: Pest risk\n" +
                "- Strong winds: Damage crops";
        }
        // Default brinjal response
        else {
            return "🍆 **All About Brinjal Cultivation:**\n\n" +
                "**Quick Information:**\n" +
                "- Growing season: 6-8 months\n" +
                "- Optimal temperature: 20-30°C\n" +
                "- Yield: 25-30 tons per hectare\n" +
                "- Profit: ₹2-4 lakhs per hectare\n" +
                "- ROI: 200-300%\n\n" +
                "**Ask me about:**\n" +
                "✅ What is use of brinjal?\n" +
                "✅ How to grow brinjal?\n" +
                "✅ Brinjal diseases & treatment?\n" +
                "✅ Fertilizer requirements?\n" +
                "✅ Water & temperature management?\n" +
                "✅ Expected yield & profit?";
        }
    }

    // ===== GRAPES RESPONSES =====
    else if (isGrape) {
        // Why/Importance/Use questions
        if (isWhyQuestion || isUseQuestion) {
            return "🍇 **Why Grow Grapes? Uses & Benefits:**\n\n" +
                "✅ **Economic Benefits:**\n" +
                "- Premium fruit with high value\n" +
                "- Multiple uses: Fresh, Wine, Juice, Raisins\n" +
                "- Excellent export market\n" +
                "- Sustained income for 30-40 years\n" +
                "- Profit: ₹5-8 lakhs per hectare\n" +
                "- Long-term asset\n\n" +
                "✅ **Agricultural Benefits:**\n" +
                "- Perennial crop (long-term investment)\n" +
                "- Suitable for various climates\n" +
                "- Good land utilization\n" +
                "- Minimal pest/disease issues (with care)\n" +
                "- Improves soil quality over time\n\n" +
                "✅ **Nutritional & Health Benefits:**\n" +
                "- Rich in antioxidants\n" +
                "- Contains resveratrol (heart health)\n" +
                "- Good source of vitamins & minerals\n" +
                "- Improve eye health\n" +
                "- Anti-cancer properties\n" +
                "- Boosts immunity\n\n" +
                "✅ **Industrial & Commercial Uses:**\n" +
                "- Wine production\n" +
                "- Juice & beverage industry\n" +
                "- Raisins & dried fruit\n" +
                "- Fresh market\n" +
                "- Export to premium markets\n" +
                "- Cosmetics & health products";
        }
        // Disease questions
        else if (isDiseaseQuestion) {
            return "🍇 **Grape Diseases Management:**\n\n" +
                "🔴 **Black Rot** (Most Serious)\n" +
                "- Symptoms: Dark spots on berries, concentric rings\n" +
                "- Medicine: Bordeaux Mixture 1% + Mancozeb 75% WP\n" +
                "- Dosage: 1.5 gm/liter\n" +
                "- Spray: Every 7-10 days from flowering\n" +
                "- Management: Remove infected berries\n\n" +
                "🔴 **Esca (Black Measles)**\n" +
                "- Symptoms: Wilting shoots, slow decline\n" +
                "- Prevention: No spray effective\n" +
                "- Treatment: Remove & burn infected parts\n" +
                "- Control: Maintain vine vigor\n" +
                "- Prune 30cm below visible symptoms\n\n" +
                "🔴 **Leaf Blight**\n" +
                "- Symptoms: Brown spots with yellow halo\n" +
                "- Medicine: Chlorothalonil 75% WP\n" +
                "- Dosage: 2 gm/liter\n" +
                "- Spray: Every 10-14 days\n" +
                "- Best: Start from fruit set stage\n\n" +
                "🔴 **Powdery Mildew**\n" +
                "- Symptoms: White powder on leaves & berries\n" +
                "- Medicine: Sulfur 80% WP\n" +
                "- Dosage: 2.5-3 gm/liter\n" +
                "- Spray: Every 10-14 days\n\n" +
                "💡 **Prevention:**\n" +
                "- Good canopy management\n" +
                "- Proper pruning & spacing\n" +
                "- Remove diseased leaves promptly\n" +
                "- Avoid overhead irrigation";
        }
        // Care/Growing questions
        else if (isCareQuestion || isHowQuestion) {
            return "🍇 **How to Cultivate Grapes - Complete Guide:**\n\n" +
                "🌡️ **Climate Requirements:**\n" +
                "- Optimal: 10-30°C\n" +
                "- Rainfall: 500-1000mm annually\n" +
                "- Avoid excessive humidity\n" +
                "- Sunny location (12+ hours)\n\n" +
                "🌱 **Planting Guide:**\n" +
                "- Season: December-February\n" +
                "- Spacing: 2m x 2m (trellis) or 1.5m x 2m (pergola)\n" +
                "- Cuttings or rooted vines\n" +
                "- Plant in trenches 60x60x60cm\n" +
                "- Depth: 40-50 cm\n\n" +
                "💧 **Irrigation Requirements:**\n" +
                "- Drip irrigation recommended: 50-60 L/plant/day\n" +
                "- Frequency: Every 2-3 days in summer\n" +
                "- Total: 600-1000mm per season\n" +
                "- Reduce during monsoon\n\n" +
                "🛟 **Soil Requirements:**\n" +
                "- Well-drained loamy soil\n" +
                "- pH: 6.5-7.5\n" +
                "- Good drainage essential\n" +
                "- Organic matter: 5-10 tons/hectare\n\n" +
                "✂️ **Pruning & Training:**\n" +
                "- Essential for quality & yield\n" +
                "- Main pruning: January-February\n" +
                "- Green pruning: May-June\n" +
                "- Remove weak/diseased shoots\n" +
                "- Train on trellis or pergola\n\n" +
                "⏱️ **Yield Timeline:**\n" +
                "- Fruit setting: 2-3 years\n" +
                "- Full production: 5-7 years\n" +
                "- Production period: 30-40 years\n" +
                "- Mature yield: 30-50 tons/hectare";
        }
        // Fertilizer questions
        else if (isFertilizerQuestion) {
            return "🍇 **Grapes Fertilizer & Nutrition:**\n\n" +
                "📋 **Initial Application (At Planting):**\n" +
                "- FYM: 25-30 tons/hectare\n" +
                "- Bone meal: 500 kg/hectare\n" +
                "- NPK 12-8-10: Initial dose\n\n" +
                "📈 **Young Vines (1-3 years):**\n" +
                "- NPK 12-8-10: 200g per vine per month\n" +
                "- Split in 3-4 applications\n" +
                "- Focus on vegetative growth\n" +
                "- Reduce flowering for vine establishment\n\n" +
                "📈 **Bearing Vines (>3 years):**\n" +
                "- NPK 12-8-10: 500-1000g per vine per season\n" +
                "- Split Applications:\n" +
                "  • After budbreak: Full NPK\n" +
                "  • At flowering: N only\n" +
                "  • After fruit set: NPK\n\n" +
                "🌿 **Organic Options:**\n" +
                "- Vermicompost: 5-10 tons/hectare\n" +
                "- Neem cake: 1-2 tons/hectare\n" +
                "- Bio-fertilizers: Azospirillum, Phosphobacteria\n" +
                "- Cow dung: 10-15 tons/hectare\n\n" +
                "💡 **Application Method:**\n" +
                "- Fertigation through drip system (Best)\n" +
                "- Soil application for traditional vineyards\n" +
                "- Foliar spray for micronutrients";
        }
        // Yield/profit questions
        else if (isYieldQuestion) {
            return "🍇 **Grapes Yield & Profitability:**\n\n" +
                "📊 **Expected Yield:**\n" +
                "- Per hectare: 30-50 tons fresh grapes\n" +
                "- Per vine: 10-15 kg annually\n" +
                "- Full production: 5-7 years\n" +
                "- Peak production: Year 7-40\n\n" +
                "💰 **Economics (Per Hectare):**\n" +
                "- Initial investment: ₹2-3 lakhs\n" +
                "- Annual revenue (mature): ₹6-10 lakhs\n" +
                "- Annual costs: ₹1-2 lakhs\n" +
                "- Net profit: ₹5-8 lakhs per year\n" +
                "- ROI: 250-300%\n" +
                "- Payback period: 3-5 years\n\n" +
                "📈 **Production Timeline:**\n" +
                "- Year 1-2: Establishment (no yield)\n" +
                "- Year 3: Light yield (5-10%)\n" +
                "- Year 4-5: Partial yield (30-50%)\n" +
                "- Year 6+: Full production (30-50 tons)\n\n" +
                "💹 **Market Prices:**\n" +
                "- Peak season: ₹25-40 per kg\n" +
                "- Off-season: ₹40-60 per kg\n" +
                "- Export quality: ₹60-100 per kg\n\n" +
                "🎯 **Maximize Profitability:**\n" +
                "- Choose good market-oriented varieties\n" +
                "- Proper canopy management\n" +
                "- Disease prevention\n" +
                "- Timely harvesting\n" +
                "- Drip irrigation efficiency";
        }
        // Temperature questions
        else if (isTemperatureQuestion) {
            return "🍇 **Grapes & Temperature Management:**\n\n" +
                "🌡️ **Optimal Temperature Range:**\n" +
                "- Growing season: 10-30°C\n" +
                "- Ideal: 20-25°C\n" +
                "- Too hot (>35°C): Berry cracking\n" +
                "- Too cold (<10°C): Growth stops\n\n" +
                "❄️ **Winter (Dormancy Period):**\n" +
                "- Chilling hours needed: 100-400 hours\n" +
                "- Below 15°C: Vine goes dormant\n" +
                "- Helps fruit ripening\n" +
                "- Break dormancy: Requires cold\n\n" +
                "🔥 **Heat Stress Management:**\n" +
                "- Temperature >35°C: Provide shade\n" +
                "- Increase irrigation (drip system)\n" +
                "- Mulching helps regulate soil\n" +
                "- Prune to improve air circulation\n" +
                "- Berry shading cloth\n\n" +
                "❄️ **Frost Protection:**\n" +
                "- Avoid frost-prone areas\n" +
                "- Use frost-hardy rootstocks\n" +
                "- Plant on elevated areas\n" +
                "- Overhead sprinkling if frost imminent";
        }
        // When to plant
        else if (isWhenQuestion) {
            return "🍇 **Best Time to Plant Grapes:**\n\n" +
                "📅 **Planting Season:**\n" +
                "- **Best Time:** December to February\n" +
                "- Reason: Winter dormancy, good establishment\n" +
                "- Temperature: 15-20°C ideal\n" +
                "- Avoid: Summer & monsoon planting\n\n" +
                "🌱 **Growth Timeline:**\n" +
                "- Dormancy: October-December\n" +
                "- Budbreak: February-March\n" +
                "- Flowering: April-May\n" +
                "- Fruit set: May-June\n" +
                "- Harvest: August-October\n\n" +
                "📊 **Production Timeline:**\n" +
                "- Year 1: Establishment only\n" +
                "- Year 2: Light flowering\n" +
                "- Year 3: First harvest (5-10%)\n" +
                "- Year 4-5: Partial production\n" +
                "- Year 6+: Full production\n\n" +
                "💡 **Tips:**\n" +
                "- Avoid planting during hot months\n" +
                "- Rain before planting helps establishment\n" +
                "- Prepare land 1-2 months before";
        }
        // Default grape response
        else {
            return "🍇 **All About Grape Cultivation:**\n\n" +
                "**Quick Information:**\n" +
                "- Perennial crop (30-40 years productive)\n" +
                "- Optimal temp: 10-30°C\n" +
                "- Yield: 30-50 tons per hectare\n" +
                "- Profit: ₹5-8 lakhs per hectare\n" +
                "- ROI: 250-300%\n" +
                "- Full production: 5-7 years\n\n" +
                "**Ask me about:**\n" +
                "✅ What is use of grapes?\n" +
                "✅ How to cultivate grapes?\n" +
                "✅ Grape diseases & treatment?\n" +
                "✅ Fertilizer requirements?\n" +
                "✅ When to plant grapes?\n" +
                "✅ Expected yield & profit?";
        }
    }

    // ===== GENERAL RESPONSES =====
    else if (hasKeyword(message, ["fertilizer", "npk", "nutrient"])) {
        return "🌱 **Fertilizer Guide:**\n\n" +
            "📋 **Common NPK Ratios:**\n" +
            "- General crops: 10-10-10\n" +
            "- Vegetable crops: 12-32-16 (initial)\n" +
            "- Fruit crops: 12-8-10\n\n" +
            "💡 **What NPK Means:**\n" +
            "- **N (Nitrogen):** Leaf & stem growth\n" +
            "- **P (Phosphorus):** Root & flower development\n" +
            "- **K (Potassium):** Fruit quality & disease resistance\n\n" +
            "🎯 **For Brinjal & Grapes:**\n" +
            "- Ask: \"What fertilizer for brinjal?\"\n" +
            "- Ask: \"What fertilizer for grapes?\"";
    }
    else if (hasKeyword(message, ["disease", "pest", "problem", "sick", "damage", "treatment"])) {
        return "🦠 **Disease Management Guide:**\n\n" +
            "📋 **Common Steps:**\n" +
            "1. Identify the disease/pest\n" +
            "2. Remove infected parts\n" +
            "3. Apply appropriate fungicide/insecticide\n" +
            "4. Follow spraying schedule\n\n" +
            "🎯 **For Specific Crops:**\n" +
            "- Ask: \"What diseases affect brinjal?\"\n" +
            "- Ask: \"Tell me about grape diseases\"\n" +
            "- Ask: \"How to treat grape black rot?\"";
    }
    else if (hasKeyword(message, ["water", "irrigation", "rain", "watering"])) {
        return "💧 **Water Management Guide:**\n\n" +
            "📋 **General Irrigation Tips:**\n" +
            "- Water early morning or evening\n" +
            "- Avoid watering in peak heat\n" +
            "- Check soil moisture before watering\n" +
            "- Drip irrigation is most efficient\n\n" +
            "🎯 **Crop-Specific:**\n" +
            "- Ask: \"Water management for brinjal\"\n" +
            "- Ask: \"How much water do grapes need?\"";
    }

    // Default fallback
    return "🤔 I'm not sure about that. Let me help you better!\n\n" +
        "**Try asking:**\n\n" +
        "🍆 **Brinjal:**\n" +
        "- What is use of brinjal?\n" +
        "- How to grow brinjal?\n" +
        "- Brinjal diseases?\n" +
        "- Fertilizer requirements?\n\n" +
        "🍇 **Grapes:**\n" +
        "- Why grow grapes?\n" +
        "- How to cultivate grapes?\n" +
        "- Grape diseases?\n" +
        "- When to plant grapes?\n\n" +
        "💡 **Or type:** Help for more options";
}

// ===== HELPER FUNCTIONS =====
function hasBrinjalKeyword(text) {
    const keywords = ["brinjal", "binjal", "eggplant", "baingan", "aubergine", "eggplan"];
    return keywords.some(k => text.includes(k));
}

function hasGrapeKeyword(text) {
    const keywords = ["grape", "grapes", "wine", "vineyard", "vine", "angur", "drakshasava"];
    return keywords.some(k => text.includes(k));
}

function hasKeyword(text, keywords) {
    return keywords.some(k => text.includes(k));
}

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