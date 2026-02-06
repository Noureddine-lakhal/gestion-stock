package com.gestionstock.ui;

import com.gestionstock.service.StockService;
import com.gestionstock.model.Product;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

public class StockLevelsFrame extends JFrame {
    private JTable stockTable;
    private DefaultTableModel tableModel;
    private StockService stockService;
    private JCheckBox lowStockOnlyCheckBox;

    public StockLevelsFrame() {
        this.stockService = new StockService();
        initComponents();
        loadStockLevels(false);
    }

    private void initComponents() {
        setTitle("Stock Levels");
        setSize(900, 600);
        setLocationRelativeTo(null);

        JPanel mainPanel = new JPanel(new BorderLayout(10, 10));
        mainPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        // Table
        String[] columns = {"Code", "Product Name", "Category", "Current Stock", "Min Stock", "Status"};
        tableModel = new DefaultTableModel(columns, 0) {
            @Override
            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };
        stockTable = new JTable(tableModel);
        JScrollPane scrollPane = new JScrollPane(stockTable);
        mainPanel.add(scrollPane, BorderLayout.CENTER);

        // Control panel
        JPanel controlPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        
        lowStockOnlyCheckBox = new JCheckBox("Show Low Stock Only");
        lowStockOnlyCheckBox.addActionListener(e -> loadStockLevels(lowStockOnlyCheckBox.isSelected()));
        
        JButton refreshButton = new JButton("Refresh");
        refreshButton.addActionListener(e -> loadStockLevels(lowStockOnlyCheckBox.isSelected()));

        controlPanel.add(lowStockOnlyCheckBox);
        controlPanel.add(refreshButton);

        mainPanel.add(controlPanel, BorderLayout.SOUTH);

        add(mainPanel);
    }

    private void loadStockLevels(boolean lowStockOnly) {
        try {
            tableModel.setRowCount(0);
            List<Product> products;
            
            if (lowStockOnly) {
                products = stockService.getLowStockProducts();
            } else {
                products = stockService.getAllProducts();
            }

            for (Product product : products) {
                String status = product.isLowStock() ? "LOW STOCK" : "OK";
                tableModel.addRow(new Object[]{
                        product.getCode(),
                        product.getName(),
                        product.getCategory(),
                        product.getCurrentStock(),
                        product.getMinStock(),
                        status
                });
            }
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error loading stock levels: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }
}
