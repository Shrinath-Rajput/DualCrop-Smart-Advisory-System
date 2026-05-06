// ========================================
// MySQL Database Configuration
// ========================================

const mysql = require("mysql2/promise");

// Create connection pool
const pool = mysql.createPool({
    host: process.env.DB_HOST || "localhost",
    user: process.env.DB_USER || "root",
    password: process.env.DB_PASSWORD || "shrinath1814",
    database: process.env.DB_NAME || "dualcrop_db",
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0,
});

// Test database connection
pool.getConnection()
    .then((connection) => {
        console.log("✅ MySQL Database Connected Successfully!");
        connection.release();
    })
    .catch((error) => {
        console.error("❌ MySQL Connection Error:", error.message);
        console.log("📝 Please ensure MySQL is running and the database exists.");
        console.log("📝 Create database with: CREATE DATABASE dualcrop_db;");
    });

module.exports = pool;