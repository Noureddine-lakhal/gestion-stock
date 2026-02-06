package com.gestionstock.ui;

import com.gestionstock.model.Product;
import com.gestionstock.service.ReportService;
import com.gestionstock.service.StockService;

import javax.swing.*;
import java.awt.*;
import java.io.File;
import java.util.List;

public class StockReportFrame extends JFrame {
    private JTextArea reportArea;
    private ReportService reportService;
    private StockService stockService;

    public StockReportFrame() {
        this.reportService = new ReportService();
        this.stockService = new StockService();
        initComponents();
        generateReport();
    }

    private void initComponents() {
        setTitle("Stock Report");
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

        // Buttons panel
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT));
        
        JButton refreshButton = new JButton("Refresh");
        refreshButton.addActionListener(e -> generateReport());
        
        JButton printButton = new JButton("Print");
        printButton.addActionListener(e -> printReport());
        
        JButton exportButton = new JButton("Export to File");
        exportButton.addActionListener(e -> exportReport());

        buttonPanel.add(refreshButton);
        buttonPanel.add(printButton);
        buttonPanel.add(exportButton);

        mainPanel.add(buttonPanel, BorderLayout.SOUTH);

        add(mainPanel);
    }

    private void generateReport() {
        try {
            List<Product> products = stockService.getAllProducts();
            String report = reportService.generateStockReport(products);
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
        fileChooser.setSelectedFile(new File("stock_report.txt"));
        
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
