package com.gestionstock.util;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.sql.Statement;

public class DatabaseManager {
    private static final String DB_URL = "jdbc:sqlite:gestion_stock.db";
    // Single-threaded connection for desktop application
    // Note: For multi-threaded environments, implement connection pooling
    private static Connection connection;

    public static synchronized Connection getConnection() throws SQLException {
        if (connection == null || connection.isClosed()) {
            connection = DriverManager.getConnection(DB_URL);
        }
        return connection;
    }

    public static void initializeDatabase() {
        try (Connection conn = getConnection();
             Statement stmt = conn.createStatement()) {

            // Create users table
            stmt.execute("CREATE TABLE IF NOT EXISTS users (" +
                    "id INTEGER PRIMARY KEY AUTOINCREMENT," +
                    "username TEXT UNIQUE NOT NULL," +
                    "password TEXT NOT NULL," +
                    "role TEXT NOT NULL," +
                    "active INTEGER DEFAULT 1)");

            // Create products table
            stmt.execute("CREATE TABLE IF NOT EXISTS products (" +
                    "id INTEGER PRIMARY KEY AUTOINCREMENT," +
                    "code TEXT UNIQUE NOT NULL," +
                    "name TEXT NOT NULL," +
                    "description TEXT," +
                    "category TEXT," +
                    "unit_price REAL NOT NULL," +
                    "current_stock INTEGER DEFAULT 0," +
                    "min_stock INTEGER DEFAULT 0)");

            // Create transactions table
            stmt.execute("CREATE TABLE IF NOT EXISTS transactions (" +
                    "id INTEGER PRIMARY KEY AUTOINCREMENT," +
                    "product_id INTEGER NOT NULL," +
                    "type TEXT NOT NULL," +
                    "quantity INTEGER NOT NULL," +
                    "unit_price REAL NOT NULL," +
                    "transaction_date TEXT NOT NULL," +
                    "user_id TEXT NOT NULL," +
                    "notes TEXT," +
                    "FOREIGN KEY (product_id) REFERENCES products(id))");

            // Create default admin user if not exists using prepared statement
            try (PreparedStatement pstmt = conn.prepareStatement(
                    "INSERT OR IGNORE INTO users (username, password, role, active) VALUES (?, ?, ?, ?)")) {
                pstmt.setString(1, "admin");
                pstmt.setString(2, org.mindrot.jbcrypt.BCrypt.hashpw("admin123", org.mindrot.jbcrypt.BCrypt.gensalt()));
                pstmt.setString(3, "ADMIN");
                pstmt.setInt(4, 1);
                pstmt.executeUpdate();
            }

            System.out.println("Database initialized successfully!");

        } catch (SQLException e) {
            System.err.println("Error initializing database: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public static void closeConnection() {
        try {
            if (connection != null && !connection.isClosed()) {
                connection.close();
            }
        } catch (SQLException e) {
            System.err.println("Error closing connection: " + e.getMessage());
        }
    }
}
