package com.gestionstock.service;

import com.gestionstock.model.Product;
import com.gestionstock.model.Transaction;

import java.io.FileWriter;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

public class ReportService {
    private static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    public String generateStockReport(List<Product> products) {
        StringBuilder report = new StringBuilder();
        report.append("================================\n");
        report.append("    STOCK REPORT\n");
        report.append("================================\n");
        report.append("Generated: ").append(LocalDateTime.now().format(DATE_FORMATTER)).append("\n\n");
        
        report.append(String.format("%-10s %-20s %-15s %-10s %-10s\n", 
                "Code", "Name", "Category", "Stock", "Min Stock"));
        report.append("--------------------------------------------------------------------------------\n");
        
        for (Product product : products) {
            report.append(String.format("%-10s %-20s %-15s %-10d %-10d %s\n",
                    product.getCode(),
                    truncate(product.getName(), 20),
                    truncate(product.getCategory(), 15),
                    product.getCurrentStock(),
                    product.getMinStock(),
                    product.isLowStock() ? "[LOW STOCK]" : ""));
        }
        
        return report.toString();
    }

    public String generateTransactionReport(List<Transaction> transactions) {
        StringBuilder report = new StringBuilder();
        report.append("================================\n");
        report.append("   TRANSACTION REPORT\n");
        report.append("================================\n");
        report.append("Generated: ").append(LocalDateTime.now().format(DATE_FORMATTER)).append("\n\n");
        
        report.append(String.format("%-15s %-20s %-8s %-10s %-12s\n",
                "Date", "Product", "Type", "Quantity", "Total Value"));
        report.append("--------------------------------------------------------------------------------\n");
        
        double totalValue = 0;
        for (Transaction transaction : transactions) {
            report.append(String.format("%-15s %-20s %-8s %-10d $%-11.2f\n",
                    transaction.getTransactionDate().format(DateTimeFormatter.ofPattern("yyyy-MM-dd")),
                    truncate(transaction.getProductName(), 20),
                    transaction.getType(),
                    transaction.getQuantity(),
                    transaction.getTotalValue()));
            totalValue += transaction.getTotalValue();
        }
        
        report.append("--------------------------------------------------------------------------------\n");
        report.append(String.format("Total Value: $%.2f\n", totalValue));
        
        return report.toString();
    }

    public void exportReportToFile(String reportContent, String filename) throws IOException {
        try (FileWriter writer = new FileWriter(filename)) {
            writer.write(reportContent);
        }
    }

    private String truncate(String str, int maxLength) {
        if (str == null) return "";
        return str.length() > maxLength ? str.substring(0, maxLength - 3) + "..." : str;
    }
}
