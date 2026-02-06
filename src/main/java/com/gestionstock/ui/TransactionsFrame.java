package com.gestionstock.ui;

import com.gestionstock.service.StockService;
import com.gestionstock.model.Transaction;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.time.format.DateTimeFormatter;
import java.util.List;

public class TransactionsFrame extends JFrame {
    private JTable transactionTable;
    private DefaultTableModel tableModel;
    private StockService stockService;
    private JComboBox<String> filterComboBox;

    public TransactionsFrame() {
        this.stockService = new StockService();
        initComponents();
        loadTransactions("ALL");
    }

    private void initComponents() {
        setTitle("Transaction History");
        setSize(1000, 600);
        setLocationRelativeTo(null);

        JPanel mainPanel = new JPanel(new BorderLayout(10, 10));
        mainPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        // Table
        String[] columns = {"ID", "Date", "Product", "Type", "Quantity", "Unit Price", "Total Value", "User"};
        tableModel = new DefaultTableModel(columns, 0) {
            @Override
            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };
        transactionTable = new JTable(tableModel);
        JScrollPane scrollPane = new JScrollPane(transactionTable);
        mainPanel.add(scrollPane, BorderLayout.CENTER);

        // Control panel
        JPanel controlPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        
        controlPanel.add(new JLabel("Filter:"));
        filterComboBox = new JComboBox<>(new String[]{"ALL", "ENTRY", "EXIT"});
        filterComboBox.addActionListener(e -> loadTransactions((String) filterComboBox.getSelectedItem()));
        
        JButton refreshButton = new JButton("Refresh");
        refreshButton.addActionListener(e -> loadTransactions((String) filterComboBox.getSelectedItem()));

        controlPanel.add(filterComboBox);
        controlPanel.add(refreshButton);

        mainPanel.add(controlPanel, BorderLayout.SOUTH);

        add(mainPanel);
    }

    private void loadTransactions(String filter) {
        try {
            tableModel.setRowCount(0);
            List<Transaction> transactions;
            
            switch (filter) {
                case "ENTRY":
                    transactions = stockService.getEntriesTransactions();
                    break;
                case "EXIT":
                    transactions = stockService.getExitTransactions();
                    break;
                default:
                    transactions = stockService.getAllTransactions();
            }

            DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm");
            
            for (Transaction transaction : transactions) {
                tableModel.addRow(new Object[]{
                        transaction.getId(),
                        transaction.getTransactionDate().format(formatter),
                        transaction.getProductName(),
                        transaction.getType(),
                        transaction.getQuantity(),
                        String.format("%.2f", transaction.getUnitPrice()),
                        String.format("%.2f", transaction.getTotalValue()),
                        transaction.getUserId()
                });
            }
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error loading transactions: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }
}
