package com.gestionstock.dao;

import com.gestionstock.model.Product;
import com.gestionstock.util.DatabaseManager;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;

public class ProductDAO {

    public void createProduct(Product product) throws SQLException {
        String sql = "INSERT INTO products (code, name, description, category, unit_price, current_stock, min_stock) " +
                "VALUES (?, ?, ?, ?, ?, ?, ?)";
        try (Connection conn = DatabaseManager.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setString(1, product.getCode());
            pstmt.setString(2, product.getName());
            pstmt.setString(3, product.getDescription());
            pstmt.setString(4, product.getCategory());
            pstmt.setDouble(5, product.getUnitPrice());
            pstmt.setInt(6, product.getCurrentStock());
            pstmt.setInt(7, product.getMinStock());
            pstmt.executeUpdate();
        }
    }

    public List<Product> getAllProducts() throws SQLException {
        List<Product> products = new ArrayList<>();
        String sql = "SELECT * FROM products ORDER BY name";
        
        try (Connection conn = DatabaseManager.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            while (rs.next()) {
                products.add(extractProductFromResultSet(rs));
            }
        }
        return products;
    }

    public Product getProductById(int id) throws SQLException {
        String sql = "SELECT * FROM products WHERE id = ?";
        try (Connection conn = DatabaseManager.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setInt(1, id);
            ResultSet rs = pstmt.executeQuery();
            
            if (rs.next()) {
                return extractProductFromResultSet(rs);
            }
        }
        return null;
    }

    public void updateProduct(Product product) throws SQLException {
        String sql = "UPDATE products SET code = ?, name = ?, description = ?, category = ?, " +
                "unit_price = ?, current_stock = ?, min_stock = ? WHERE id = ?";
        try (Connection conn = DatabaseManager.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setString(1, product.getCode());
            pstmt.setString(2, product.getName());
            pstmt.setString(3, product.getDescription());
            pstmt.setString(4, product.getCategory());
            pstmt.setDouble(5, product.getUnitPrice());
            pstmt.setInt(6, product.getCurrentStock());
            pstmt.setInt(7, product.getMinStock());
            pstmt.setInt(8, product.getId());
            pstmt.executeUpdate();
        }
    }

    public void deleteProduct(int id) throws SQLException {
        String sql = "DELETE FROM products WHERE id = ?";
        try (Connection conn = DatabaseManager.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setInt(1, id);
            pstmt.executeUpdate();
        }
    }

    public void updateStock(int productId, int quantity) throws SQLException {
        String sql = "UPDATE products SET current_stock = current_stock + ? WHERE id = ?";
        try (Connection conn = DatabaseManager.getConnection();
             PreparedStatement pstmt = conn.prepareStatement(sql)) {
            
            pstmt.setInt(1, quantity);
            pstmt.setInt(2, productId);
            pstmt.executeUpdate();
        }
    }

    public List<Product> getLowStockProducts() throws SQLException {
        List<Product> products = new ArrayList<>();
        String sql = "SELECT * FROM products WHERE current_stock <= min_stock ORDER BY name";
        
        try (Connection conn = DatabaseManager.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {
            
            while (rs.next()) {
                products.add(extractProductFromResultSet(rs));
            }
        }
        return products;
    }

    private Product extractProductFromResultSet(ResultSet rs) throws SQLException {
        return new Product(
                rs.getInt("id"),
                rs.getString("code"),
                rs.getString("name"),
                rs.getString("description"),
                rs.getString("category"),
                rs.getDouble("unit_price"),
                rs.getInt("current_stock"),
                rs.getInt("min_stock")
        );
    }
}
