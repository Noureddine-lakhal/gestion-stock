package com.gestionstock.ui;

import com.gestionstock.dao.ProductDAO;
import com.gestionstock.model.Product;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

public class ProductManagementFrame extends JFrame {
    private JTable productTable;
    private DefaultTableModel tableModel;
    private ProductDAO productDAO;

    public ProductManagementFrame() {
        this.productDAO = new ProductDAO();
        initComponents();
        loadProducts();
    }

    private void initComponents() {
        setTitle("Manage Products");
        setSize(900, 600);
        setLocationRelativeTo(null);

        JPanel mainPanel = new JPanel(new BorderLayout(10, 10));
        mainPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        // Table
        String[] columns = {"ID", "Code", "Name", "Description", "Category", "Unit Price", "Stock", "Min Stock"};
        tableModel = new DefaultTableModel(columns, 0) {
            @Override
            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };
        productTable = new JTable(tableModel);
        JScrollPane scrollPane = new JScrollPane(productTable);
        mainPanel.add(scrollPane, BorderLayout.CENTER);

        // Buttons panel
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        
        JButton addButton = new JButton("Add Product");
        addButton.addActionListener(e -> addProduct());
        
        JButton editButton = new JButton("Edit Product");
        editButton.addActionListener(e -> editProduct());
        
        JButton deleteButton = new JButton("Delete Product");
        deleteButton.addActionListener(e -> deleteProduct());
        
        JButton refreshButton = new JButton("Refresh");
        refreshButton.addActionListener(e -> loadProducts());

        buttonPanel.add(addButton);
        buttonPanel.add(editButton);
        buttonPanel.add(deleteButton);
        buttonPanel.add(refreshButton);

        mainPanel.add(buttonPanel, BorderLayout.SOUTH);

        add(mainPanel);
    }

    private void loadProducts() {
        try {
            tableModel.setRowCount(0);
            List<Product> products = productDAO.getAllProducts();
            for (Product product : products) {
                tableModel.addRow(new Object[]{
                        product.getId(),
                        product.getCode(),
                        product.getName(),
                        product.getDescription(),
                        product.getCategory(),
                        String.format("%.2f", product.getUnitPrice()),
                        product.getCurrentStock(),
                        product.getMinStock()
                });
            }
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error loading products: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void addProduct() {
        ProductDialog dialog = new ProductDialog(this, null);
        dialog.setVisible(true);
        if (dialog.isConfirmed()) {
            try {
                productDAO.createProduct(dialog.getProduct());
                loadProducts();
                JOptionPane.showMessageDialog(this, "Product added successfully");
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Error adding product: " + ex.getMessage(),
                        "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private void editProduct() {
        int selectedRow = productTable.getSelectedRow();
        if (selectedRow == -1) {
            JOptionPane.showMessageDialog(this, "Please select a product to edit",
                    "No Selection", JOptionPane.WARNING_MESSAGE);
            return;
        }

        try {
            int productId = (int) tableModel.getValueAt(selectedRow, 0);
            Product product = productDAO.getProductById(productId);
            
            ProductDialog dialog = new ProductDialog(this, product);
            dialog.setVisible(true);
            
            if (dialog.isConfirmed()) {
                productDAO.updateProduct(dialog.getProduct());
                loadProducts();
                JOptionPane.showMessageDialog(this, "Product updated successfully");
            }
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error updating product: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void deleteProduct() {
        int selectedRow = productTable.getSelectedRow();
        if (selectedRow == -1) {
            JOptionPane.showMessageDialog(this, "Please select a product to delete",
                    "No Selection", JOptionPane.WARNING_MESSAGE);
            return;
        }

        int confirm = JOptionPane.showConfirmDialog(this,
                "Are you sure you want to delete this product?",
                "Confirm Delete", JOptionPane.YES_NO_OPTION);

        if (confirm == JOptionPane.YES_OPTION) {
            try {
                int productId = (int) tableModel.getValueAt(selectedRow, 0);
                productDAO.deleteProduct(productId);
                loadProducts();
                JOptionPane.showMessageDialog(this, "Product deleted successfully");
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Error deleting product: " + ex.getMessage(),
                        "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }
}
