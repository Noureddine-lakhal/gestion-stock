package com.gestionstock.ui;

import com.gestionstock.model.Product;

import javax.swing.*;
import java.awt.*;

public class ProductDialog extends JDialog {
    private JTextField codeField;
    private JTextField nameField;
    private JTextArea descriptionArea;
    private JTextField categoryField;
    private JTextField priceField;
    private JTextField stockField;
    private JTextField minStockField;
    private boolean confirmed = false;
    private Product product;

    public ProductDialog(Frame parent, Product product) {
        super(parent, product == null ? "Add Product" : "Edit Product", true);
        this.product = product;
        initComponents();
        if (product != null) {
            fillFields(product);
        }
    }

    private void initComponents() {
        setSize(400, 500);
        setLocationRelativeTo(getParent());

        JPanel mainPanel = new JPanel(new GridBagLayout());
        mainPanel.setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5);
        gbc.fill = GridBagConstraints.HORIZONTAL;

        int row = 0;

        // Code
        addField(mainPanel, gbc, row++, "Product Code:", codeField = new JTextField(20));

        // Name
        addField(mainPanel, gbc, row++, "Name:", nameField = new JTextField(20));

        // Description
        gbc.gridx = 0;
        gbc.gridy = row;
        mainPanel.add(new JLabel("Description:"), gbc);
        
        descriptionArea = new JTextArea(3, 20);
        descriptionArea.setLineWrap(true);
        JScrollPane descScrollPane = new JScrollPane(descriptionArea);
        gbc.gridx = 1;
        mainPanel.add(descScrollPane, gbc);
        row++;

        // Category
        addField(mainPanel, gbc, row++, "Category:", categoryField = new JTextField(20));

        // Unit Price
        addField(mainPanel, gbc, row++, "Unit Price:", priceField = new JTextField(20));

        // Current Stock
        addField(mainPanel, gbc, row++, "Current Stock:", stockField = new JTextField(20));

        // Min Stock
        addField(mainPanel, gbc, row++, "Min Stock:", minStockField = new JTextField(20));

        // Buttons
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT));
        JButton saveButton = new JButton("Save");
        saveButton.addActionListener(e -> save());
        JButton cancelButton = new JButton("Cancel");
        cancelButton.addActionListener(e -> dispose());
        
        buttonPanel.add(saveButton);
        buttonPanel.add(cancelButton);

        gbc.gridx = 0;
        gbc.gridy = row;
        gbc.gridwidth = 2;
        mainPanel.add(buttonPanel, gbc);

        add(mainPanel);
    }

    private void addField(JPanel panel, GridBagConstraints gbc, int row, String label, JTextField field) {
        gbc.gridx = 0;
        gbc.gridy = row;
        panel.add(new JLabel(label), gbc);
        gbc.gridx = 1;
        panel.add(field, gbc);
    }

    private void fillFields(Product product) {
        codeField.setText(product.getCode());
        nameField.setText(product.getName());
        descriptionArea.setText(product.getDescription());
        categoryField.setText(product.getCategory());
        priceField.setText(String.valueOf(product.getUnitPrice()));
        stockField.setText(String.valueOf(product.getCurrentStock()));
        minStockField.setText(String.valueOf(product.getMinStock()));
    }

    private void save() {
        try {
            String code = codeField.getText().trim();
            String name = nameField.getText().trim();
            String description = descriptionArea.getText().trim();
            String category = categoryField.getText().trim();
            double price = Double.parseDouble(priceField.getText().trim());
            int stock = Integer.parseInt(stockField.getText().trim());
            int minStock = Integer.parseInt(minStockField.getText().trim());

            if (code.isEmpty() || name.isEmpty()) {
                JOptionPane.showMessageDialog(this, "Code and Name are required",
                        "Validation Error", JOptionPane.ERROR_MESSAGE);
                return;
            }

            if (price < 0 || stock < 0 || minStock < 0) {
                JOptionPane.showMessageDialog(this, "Price and quantities cannot be negative",
                        "Validation Error", JOptionPane.ERROR_MESSAGE);
                return;
            }

            if (product == null) {
                product = new Product();
            }
            product.setCode(code);
            product.setName(name);
            product.setDescription(description);
            product.setCategory(category);
            product.setUnitPrice(price);
            product.setCurrentStock(stock);
            product.setMinStock(minStock);

            confirmed = true;
            dispose();

        } catch (NumberFormatException ex) {
            JOptionPane.showMessageDialog(this, "Please enter valid numbers for price and quantities",
                    "Validation Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    public boolean isConfirmed() {
        return confirmed;
    }

    public Product getProduct() {
        return product;
    }
}
