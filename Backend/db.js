// ========================================
// MySQL Database Configuration
// ========================================

const mysql = require("mysql2/promise");

// Create connection pool
const pool = mysql.createPool({
    host: process.env.MYSQLHOST,
    user: process.env.MYSQLUSER,
    password: process.env.MYSQLPASSWORD,
    database: process.env.MYSQLDATABASE,
    port: process.env.MYSQLPORT,

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
    });

module.exports = pool;