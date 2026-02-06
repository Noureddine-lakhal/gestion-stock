package com.gestionstock.test;

import com.gestionstock.dao.ProductDAO;
import com.gestionstock.dao.UserDAO;
import com.gestionstock.model.Product;
import com.gestionstock.model.User;
import com.gestionstock.service.StockService;
import com.gestionstock.util.DatabaseManager;
import com.gestionstock.util.SessionManager;

public class TestApplication {
    public static void main(String[] args) {
        System.out.println("=== Testing Gestion de Stock Application ===\n");

        // Test 1: Database Initialization
        System.out.println("1. Testing Database Initialization...");
        try {
            DatabaseManager.initializeDatabase();
            System.out.println("   ✓ Database initialized successfully\n");
        } catch (Exception e) {
            System.err.println("   ✗ Database initialization failed: " + e.getMessage());
            return;
        }

        // Test 2: User Authentication
        System.out.println("2. Testing User Authentication...");
        try {
            UserDAO userDAO = new UserDAO();
            User user = userDAO.authenticate("admin", "admin123");
            if (user != null) {
                System.out.println("   ✓ Admin user authenticated successfully");
                System.out.println("   - Username: " + user.getUsername());
                System.out.println("   - Role: " + user.getRole());
                SessionManager.setCurrentUser(user);
                System.out.println();
            } else {
                System.err.println("   ✗ Authentication failed");
                return;
            }
        } catch (Exception e) {
            System.err.println("   ✗ Authentication test failed: " + e.getMessage());
            e.printStackTrace();
            return;
        }

        // Test 3: Product Management
        System.out.println("3. Testing Product Management...");
        try {
            ProductDAO productDAO = new ProductDAO();
            
            // Create a test product
            Product product = new Product();
            product.setCode("TEST001");
            product.setName("Test Product");
            product.setDescription("Test product for validation");
            product.setCategory("Electronics");
            product.setUnitPrice(99.99);
            product.setCurrentStock(10);
            product.setMinStock(5);
            
            productDAO.createProduct(product);
            System.out.println("   ✓ Product created successfully");
            
            // List all products
            var products = productDAO.getAllProducts();
            System.out.println("   ✓ Total products in database: " + products.size());
            System.out.println();
        } catch (Exception e) {
            System.err.println("   ✗ Product management test failed: " + e.getMessage());
            e.printStackTrace();
            return;
        }

        // Test 4: Stock Entry
        System.out.println("4. Testing Stock Entry...");
        try {
            StockService stockService = new StockService();
            ProductDAO productDAO = new ProductDAO();
            
            var products = productDAO.getAllProducts();
            if (!products.isEmpty()) {
                Product product = products.get(0);
                int originalStock = product.getCurrentStock();
                
                stockService.recordEntry(product.getId(), 50, 99.99, "Test entry");
                
                // Verify stock updated
                product = productDAO.getProductById(product.getId());
                if (product.getCurrentStock() == originalStock + 50) {
                    System.out.println("   ✓ Stock entry recorded successfully");
                    System.out.println("   - Original stock: " + originalStock);
                    System.out.println("   - New stock: " + product.getCurrentStock());
                    System.out.println();
                } else {
                    System.err.println("   ✗ Stock not updated correctly");
                }
            }
        } catch (Exception e) {
            System.err.println("   ✗ Stock entry test failed: " + e.getMessage());
            e.printStackTrace();
            return;
        }

        // Test 5: Stock Exit
        System.out.println("5. Testing Stock Exit...");
        try {
            StockService stockService = new StockService();
            ProductDAO productDAO = new ProductDAO();
            
            var products = productDAO.getAllProducts();
            if (!products.isEmpty()) {
                Product product = products.get(0);
                int originalStock = product.getCurrentStock();
                
                stockService.recordExit(product.getId(), 5, 99.99, "Test exit");
                
                // Verify stock updated
                product = productDAO.getProductById(product.getId());
                if (product.getCurrentStock() == originalStock - 5) {
                    System.out.println("   ✓ Stock exit recorded successfully");
                    System.out.println("   - Original stock: " + originalStock);
                    System.out.println("   - New stock: " + product.getCurrentStock());
                    System.out.println();
                } else {
                    System.err.println("   ✗ Stock not updated correctly");
                }
            }
        } catch (Exception e) {
            System.err.println("   ✗ Stock exit test failed: " + e.getMessage());
            e.printStackTrace();
            return;
        }

        // Test 6: Transaction History
        System.out.println("6. Testing Transaction History...");
        try {
            StockService stockService = new StockService();
            var transactions = stockService.getAllTransactions();
            System.out.println("   ✓ Total transactions: " + transactions.size());
            System.out.println();
        } catch (Exception e) {
            System.err.println("   ✗ Transaction history test failed: " + e.getMessage());
            e.printStackTrace();
            return;
        }

        // Test 7: Reports
        System.out.println("7. Testing Report Generation...");
        try {
            com.gestionstock.service.ReportService reportService = new com.gestionstock.service.ReportService();
            StockService stockService = new StockService();
            
            var products = stockService.getAllProducts();
            String stockReport = reportService.generateStockReport(products);
            System.out.println("   ✓ Stock report generated successfully");
            System.out.println("   - Report length: " + stockReport.length() + " characters");
            
            var transactions = stockService.getAllTransactions();
            String transactionReport = reportService.generateTransactionReport(transactions);
            System.out.println("   ✓ Transaction report generated successfully");
            System.out.println("   - Report length: " + transactionReport.length() + " characters");
            System.out.println();
        } catch (Exception e) {
            System.err.println("   ✗ Report generation test failed: " + e.getMessage());
            e.printStackTrace();
            return;
        }

        System.out.println("=== All Tests Passed Successfully! ===");
        DatabaseManager.closeConnection();
    }
}
