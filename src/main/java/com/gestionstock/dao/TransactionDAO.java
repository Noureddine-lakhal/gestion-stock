package com.gestionstock.dao;

import com.gestionstock.model.Transaction;
import com.gestionstock.util.DatabaseManager;

import java.sql.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class TransactionDAO {
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public void createTransaction(Transaction transaction) throws SQLException {
        String sql = "INSERT INTO transactions (product_id, type, quantity, unit_price, transaction_date, user_id, notes) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?)";
        try (Connection conn = DatabaseManager.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setInt(1, transaction.getProductId());
            pstmt.setString(2, transaction.getType());
            pstmt.setInt(3, transaction.getQuantity());
            pstmt.setDouble(4, transaction.getUnitPrice());
            pstmt.setString(5, transaction.getTransactionDate().format(DATE_FORMATTER));
            pstmt.setString(6, transaction.getUserId());
            pstmt.setString(7, transaction.getNotes());
            pstmt.executeUpdate();
        }
    }

    public List<Transaction> getAllTransactions() throws SQLException {
        List<Transaction> transactions = new ArrayList<>();
        String sql = "SELECT t.*, p.name as product_name FROM transactions t " +
                "LEFT JOIN products p ON t.product_id = p.id " +
                "ORDER BY t.transaction_date DESC";
        
        try (Connection conn = DatabaseManager.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            while (rs.next()) {
                transactions.add(extractTransactionFromResultSet(rs));
            }
        }
        return transactions;
    }

    public List<Transaction> getTransactionsByProduct(int productId) throws SQLException {
        List<Transaction> transactions = new ArrayList<>();
        String sql = "SELECT t.*, p.name as product_name FROM transactions t " +
                "LEFT JOIN products p ON t.product_id = p.id " +
                "WHERE t.product_id = ? ORDER BY t.transaction_date DESC";
        
        try (Connection conn = DatabaseManager.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setInt(1, productId);
            ResultSet rs = pstmt.executeQuery();
            
            while (rs.next()) {
                transactions.add(extractTransactionFromResultSet(rs));
            }
        }
        return transactions;
    }

    public List<Transaction> getTransactionsByType(String type) throws SQLException {
        List<Transaction> transactions = new ArrayList<>();
        String sql = "SELECT t.*, p.name as product_name FROM transactions t " +
                "LEFT JOIN products p ON t.product_id = p.id " +
                "WHERE t.type = ? ORDER BY t.transaction_date DESC";
        
        try (Connection conn = DatabaseManager.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setString(1, type);
            ResultSet rs = pstmt.executeQuery();
            
            while (rs.next()) {
                transactions.add(extractTransactionFromResultSet(rs));
            }
        }
        return transactions;
    }

    private Transaction extractTransactionFromResultSet(ResultSet rs) throws SQLException {
        return new Transaction(
                rs.getInt("id"),
                rs.getInt("product_id"),
                rs.getString("product_name"),
                rs.getString("type"),
                rs.getInt("quantity"),
                rs.getDouble("unit_price"),
                LocalDateTime.parse(rs.getString("transaction_date"), DATE_FORMATTER),
                rs.getString("user_id"),
                rs.getString("notes")
        );
    }
}
