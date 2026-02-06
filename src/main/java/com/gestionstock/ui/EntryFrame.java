package com.gestionstock.ui;

import com.gestionstock.dao.ProductDAO;
import com.gestionstock.model.Product;
import com.gestionstock.service.StockService;

import javax.swing.*;
import java.awt.*;
import java.util.List;

public class EntryFrame extends JFrame {
    private JComboBox<String> productComboBox;
    private JTextField quantityField;
    private JTextField priceField;
    private JTextArea notesArea;
    private ProductDAO productDAO;
    private StockService stockService;
    private List<Product> products;

    public EntryFrame() {
        this.productDAO = new ProductDAO();
        this.stockService = new StockService();
        initComponents();
    }

    private void initComponents() {
        setTitle("Record Stock Entry");
        setSize(500, 400);
        setLocationRelativeTo(null);

        JPanel mainPanel = new JPanel(new GridBagLayout());
        mainPanel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5);
        gbc.fill = GridBagConstraints.HORIZONTAL;

        // Title
        JLabel titleLabel = new JLabel("Record Stock Entry");
        titleLabel.setFont(new Font("Arial", Font.BOLD, 18));
        gbc.gridx = 0;
        gbc.gridy = 0;
        gbc.gridwidth = 2;
        mainPanel.add(titleLabel, gbc);

        gbc.gridwidth = 1;

        // Product selection
        gbc.gridy = 1;
        gbc.gridx = 0;
        mainPanel.add(new JLabel("Product:"), gbc);

        productComboBox = new JComboBox<>();
        loadProducts();
        gbc.gridx = 1;
        mainPanel.add(productComboBox, gbc);

        // Quantity
        gbc.gridy = 2;
        gbc.gridx = 0;
        mainPanel.add(new JLabel("Quantity:"), gbc);

        quantityField = new JTextField(20);
        gbc.gridx = 1;
        mainPanel.add(quantityField, gbc);

        // Unit Price
        gbc.gridy = 3;
        gbc.gridx = 0;
        mainPanel.add(new JLabel("Unit Price:"), gbc);

        priceField = new JTextField(20);
        gbc.gridx = 1;
        mainPanel.add(priceField, gbc);

        // Notes
        gbc.gridy = 4;
        gbc.gridx = 0;
        mainPanel.add(new JLabel("Notes:"), gbc);

        notesArea = new JTextArea(4, 20);
        notesArea.setLineWrap(true);
        JScrollPane scrollPane = new JScrollPane(notesArea);
        gbc.gridx = 1;
        mainPanel.add(scrollPane, gbc);

        // Buttons
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT));
        JButton saveButton = new JButton("Record Entry");
        saveButton.addActionListener(e -> recordEntry());
        JButton cancelButton = new JButton("Cancel");
        cancelButton.addActionListener(e -> dispose());

        buttonPanel.add(saveButton);
        buttonPanel.add(cancelButton);

        gbc.gridy = 5;
        gbc.gridx = 0;
        gbc.gridwidth = 2;
        mainPanel.add(buttonPanel, gbc);

        add(mainPanel);
    }

    private void loadProducts() {
        try {
            products = productDAO.getAllProducts();
            productComboBox.removeAllItems();
            for (Product product : products) {
                productComboBox.addItem(product.getCode() + " - " + product.getName());
            }
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error loading products: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void recordEntry() {
        try {
            int selectedIndex = productComboBox.getSelectedIndex();
            if (selectedIndex == -1) {
                JOptionPane.showMessageDialog(this, "Please select a product",
                        "Validation Error", JOptionPane.ERROR_MESSAGE);
                return;
            }

            int quantity = Integer.parseInt(quantityField.getText().trim());
            double price = Double.parseDouble(priceField.getText().trim());
            String notes = notesArea.getText().trim();

            if (quantity <= 0 || price < 0) {
                JOptionPane.showMessageDialog(this, "Please enter valid quantity and price",
                        "Validation Error", JOptionPane.ERROR_MESSAGE);
                return;
            }

            Product product = products.get(selectedIndex);
            stockService.recordEntry(product.getId(), quantity, price, notes);

            JOptionPane.showMessageDialog(this, "Stock entry recorded successfully");
            dispose();

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Please enter valid numbers for quantity and price",
                    "Validation Error", JOptionPane.ERROR_MESSAGE);
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error recording entry: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }
}
