package com.gestionstock.ui;

import com.gestionstock.model.Transaction;
import com.gestionstock.service.ReportService;
import com.gestionstock.service.StockService;

import javax.swing.*;
import java.awt.*;
import java.io.File;
import java.util.List;

public class TransactionReportFrame extends JFrame {
    private JTextArea reportArea;
    private JComboBox<String> filterComboBox;
    private ReportService reportService;
    private StockService stockService;

    public TransactionReportFrame() {
        this.reportService = new ReportService();
        this.stockService = new StockService();
        initComponents();
        generateReport("ALL");
    }

    private void initComponents() {
        setTitle("Transaction Report");
        setSize(800, 600);
        setLocationRelativeTo(null);

        JPanel mainPanel = new JPanel(new BorderLayout(10, 10));
        mainPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        // Report area
        reportArea = new JTextArea();
        reportArea.setEditable(false);
        reportArea.setFont(new Font("Courier New", Font.PLAIN, 12));
        JScrollPane scrollPane = new JScrollPane(reportArea);
        mainPanel.add(scrollPane, BorderLayout.CENTER);

        // Control panel
        JPanel controlPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        
        controlPanel.add(new JLabel("Filter:"));
        filterComboBox = new JComboBox<>(new String[]{"ALL", "ENTRY", "EXIT"});
        filterComboBox.addActionListener(e -> generateReport((String) filterComboBox.getSelectedItem()));
        controlPanel.add(filterComboBox);

        // Buttons panel
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT));
        
        JButton refreshButton = new JButton("Refresh");
        refreshButton.addActionListener(e -> generateReport((String) filterComboBox.getSelectedItem()));
        
        JButton printButton = new JButton("Print");
        printButton.addActionListener(e -> printReport());
        
        JButton exportButton = new JButton("Export to File");
        exportButton.addActionListener(e -> exportReport());

        buttonPanel.add(refreshButton);
        buttonPanel.add(printButton);
        buttonPanel.add(exportButton);

        JPanel bottomPanel = new JPanel(new BorderLayout());
        bottomPanel.add(controlPanel, BorderLayout.WEST);
        bottomPanel.add(buttonPanel, BorderLayout.EAST);

        mainPanel.add(bottomPanel, BorderLayout.SOUTH);

        add(mainPanel);
    }

    private void generateReport(String filter) {
        try {
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

            String report = reportService.generateTransactionReport(transactions);
            reportArea.setText(report);
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error generating report: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void printReport() {
        try {
            reportArea.print();
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error printing report: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void exportReport() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setDialogTitle("Save Report");
        fileChooser.setSelectedFile(new File("transaction_report.txt"));
        
        int userSelection = fileChooser.showSaveDialog(this);
        
        if (userSelection == JFileChooser.APPROVE_OPTION) {
            try {
                File fileToSave = fileChooser.getSelectedFile();
                reportService.exportReportToFile(reportArea.getText(), fileToSave.getAbsolutePath());
                JOptionPane.showMessageDialog(this, "Report exported successfully");
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Error exporting report: " + ex.getMessage(),
                        "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }
}
