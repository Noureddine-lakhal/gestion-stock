package com.gestionstock;

import com.gestionstock.ui.LoginFrame;
import com.gestionstock.util.DatabaseManager;

import javax.swing.*;

public class Main {
    public static void main(String[] args) {
        // Initialize database
        DatabaseManager.initializeDatabase();

        // Set Look and Feel
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }

        // Start application with login screen
        SwingUtilities.invokeLater(() -> {
            LoginFrame loginFrame = new LoginFrame();
            loginFrame.setVisible(true);
        });

        // Add shutdown hook to close database connection
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            DatabaseManager.closeConnection();
            System.out.println("Application closed.");
        }));
    }
}
