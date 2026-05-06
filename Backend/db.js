const mysql = require("mysql2/promise");

const pool = mysql.createPool({
    uri: process.env.DATABASE_URL,
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0,
});

async function testConnection() {
    try {
        const connection = await pool.getConnection();
        console.log("✅ MySQL Database Connected Successfully!");
        connection.release();
    } catch (error) {
        console.error("❌ MySQL Connection Error:", error);
    }
}

testConnection();

module.exports = pool;