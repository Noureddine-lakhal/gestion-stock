package com.gestionstock.service;

import com.gestionstock.dao.ProductDAO;
import com.gestionstock.dao.TransactionDAO;
import com.gestionstock.model.Product;
import com.gestionstock.model.Transaction;
import com.gestionstock.util.SessionManager;

import java.sql.SQLException;
import java.time.LocalDateTime;
import java.util.List;

public class StockService {
    private final ProductDAO productDAO;
    private final TransactionDAO transactionDAO;

    public StockService() {
        this.productDAO = new ProductDAO();
        this.transactionDAO = new TransactionDAO();
    }

    public void recordEntry(int productId, int quantity, double unitPrice, String notes) throws SQLException {
        // Update product stock
        productDAO.updateStock(productId, quantity);

        // Create transaction record
        Product product = productDAO.getProductById(productId);
        Transaction transaction = new Transaction();
        transaction.setProductId(productId);
        transaction.setProductName(product.getName());
        transaction.setType("ENTRY");
        transaction.setQuantity(quantity);
        transaction.setUnitPrice(unitPrice);
        transaction.setTransactionDate(LocalDateTime.now());
        transaction.setUserId(SessionManager.getCurrentUser().getUsername());
        transaction.setNotes(notes);
        
        transactionDAO.createTransaction(transaction);
    }

    public void recordExit(int productId, int quantity, double unitPrice, String notes) throws SQLException {
        // Check if sufficient stock is available
        Product product = productDAO.getProductById(productId);
        if (product.getCurrentStock() < quantity) {
            throw new IllegalStateException("Insufficient stock. Available: " + product.getCurrentStock());
        }

        // Update product stock (negative quantity for exit)
        productDAO.updateStock(productId, -quantity);

        // Create transaction record
        Transaction transaction = new Transaction();
        transaction.setProductId(productId);
        transaction.setProductName(product.getName());
        transaction.setType("EXIT");
        transaction.setQuantity(quantity);
        transaction.setUnitPrice(unitPrice);
        transaction.setTransactionDate(LocalDateTime.now());
        transaction.setUserId(SessionManager.getCurrentUser().getUsername());
        transaction.setNotes(notes);
        
        transactionDAO.createTransaction(transaction);
    }

    public List<Product> getAllProducts() throws SQLException {
        return productDAO.getAllProducts();
    }

    public List<Product> getLowStockProducts() throws SQLException {
        return productDAO.getLowStockProducts();
    }

    public List<Transaction> getAllTransactions() throws SQLException {
        return transactionDAO.getAllTransactions();
    }

    public List<Transaction> getEntriesTransactions() throws SQLException {
        return transactionDAO.getTransactionsByType("ENTRY");
    }

    public List<Transaction> getExitTransactions() throws SQLException {
        return transactionDAO.getTransactionsByType("EXIT");
    }
}
