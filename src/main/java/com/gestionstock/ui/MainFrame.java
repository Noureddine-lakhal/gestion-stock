package com.gestionstock.ui;

import com.gestionstock.util.SessionManager;

import javax.swing.*;
import java.awt.*;

public class MainFrame extends JFrame {

    public MainFrame() {
        initComponents();
    }

    private void initComponents() {
        setTitle("Gestion de Stock - Main Menu");
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setSize(800, 600);
        setLocationRelativeTo(null);

        // Create menu bar
        JMenuBar menuBar = new JMenuBar();

        // File menu
        JMenu fileMenu = new JMenu("File");
        JMenuItem logoutItem = new JMenuItem("Logout");
        logoutItem.addActionListener(e -> logout());
        JMenuItem exitItem = new JMenuItem("Exit");
        exitItem.addActionListener(e -> System.exit(0));
        fileMenu.add(logoutItem);
        fileMenu.add(exitItem);
        menuBar.add(fileMenu);

        // Products menu
        JMenu productsMenu = new JMenu("Products");
        JMenuItem manageProductsItem = new JMenuItem("Manage Products");
        manageProductsItem.addActionListener(e -> openProductsPanel());
        JMenuItem viewStockItem = new JMenuItem("View Stock Levels");
        viewStockItem.addActionListener(e -> openStockLevelsPanel());
        productsMenu.add(manageProductsItem);
        productsMenu.add(viewStockItem);
        menuBar.add(productsMenu);

        // Transactions menu
        JMenu transactionsMenu = new JMenu("Transactions");
        JMenuItem recordEntryItem = new JMenuItem("Record Entry");
        recordEntryItem.addActionListener(e -> openEntryPanel());
        JMenuItem recordExitItem = new JMenuItem("Record Exit");
        recordExitItem.addActionListener(e -> openExitPanel());
        JMenuItem viewTransactionsItem = new JMenuItem("View Transactions");
        viewTransactionsItem.addActionListener(e -> openTransactionsPanel());
        transactionsMenu.add(recordEntryItem);
        transactionsMenu.add(recordExitItem);
        transactionsMenu.add(viewTransactionsItem);
        menuBar.add(transactionsMenu);

        // Reports menu
        JMenu reportsMenu = new JMenu("Reports");
        JMenuItem stockReportItem = new JMenuItem("Stock Report");
        stockReportItem.addActionListener(e -> openStockReportPanel());
        JMenuItem transactionReportItem = new JMenuItem("Transaction Report");
        transactionReportItem.addActionListener(e -> openTransactionReportPanel());
        reportsMenu.add(stockReportItem);
        reportsMenu.add(transactionReportItem);
        menuBar.add(reportsMenu);

        // Users menu (admin only)
        if (SessionManager.isAdmin()) {
            JMenu usersMenu = new JMenu("Users");
            JMenuItem manageUsersItem = new JMenuItem("Manage Users");
            manageUsersItem.addActionListener(e -> openUsersPanel());
            usersMenu.add(manageUsersItem);
            menuBar.add(usersMenu);
        }

        setJMenuBar(menuBar);

        // Main panel with welcome message
        JPanel mainPanel = new JPanel(new BorderLayout());
        
        JLabel welcomeLabel = new JLabel("Welcome, " + SessionManager.getCurrentUser().getUsername() + "!");
        welcomeLabel.setFont(new Font("Arial", Font.BOLD, 20));
        welcomeLabel.setHorizontalAlignment(JLabel.CENTER);
        welcomeLabel.setBorder(BorderFactory.createEmptyBorder(20, 0, 20, 0));
        mainPanel.add(welcomeLabel, BorderLayout.NORTH);

        // Dashboard buttons
        JPanel dashboardPanel = new JPanel(new GridLayout(2, 3, 20, 20));
        dashboardPanel.setBorder(BorderFactory.createEmptyBorder(50, 50, 50, 50));

        dashboardPanel.add(createDashboardButton("Manage Products", e -> openProductsPanel()));
        dashboardPanel.add(createDashboardButton("Record Entry", e -> openEntryPanel()));
        dashboardPanel.add(createDashboardButton("Record Exit", e -> openExitPanel()));
        dashboardPanel.add(createDashboardButton("View Stock", e -> openStockLevelsPanel()));
        dashboardPanel.add(createDashboardButton("Transactions", e -> openTransactionsPanel()));
        dashboardPanel.add(createDashboardButton("Reports", e -> openStockReportPanel()));

        mainPanel.add(dashboardPanel, BorderLayout.CENTER);

        add(mainPanel);
    }

    private JButton createDashboardButton(String text, java.awt.event.ActionListener listener) {
        JButton button = new JButton(text);
        button.setFont(new Font("Arial", Font.BOLD, 14));
        button.addActionListener(listener);
        return button;
    }

    private void logout() {
        SessionManager.logout();
        dispose();
        new LoginFrame().setVisible(true);
    }

    private void openProductsPanel() {
        new ProductManagementFrame().setVisible(true);
    }

    private void openStockLevelsPanel() {
        new StockLevelsFrame().setVisible(true);
    }

    private void openEntryPanel() {
        new EntryFrame().setVisible(true);
    }

    private void openExitPanel() {
        new ExitFrame().setVisible(true);
    }

    private void openTransactionsPanel() {
        new TransactionsFrame().setVisible(true);
    }

    private void openStockReportPanel() {
        new StockReportFrame().setVisible(true);
    }

    private void openTransactionReportPanel() {
        new TransactionReportFrame().setVisible(true);
    }

    private void openUsersPanel() {
        new UserManagementFrame().setVisible(true);
    }
}
