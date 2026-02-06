package com.gestionstock.ui;

import com.gestionstock.dao.UserDAO;
import com.gestionstock.model.User;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.util.List;

public class UserManagementFrame extends JFrame {
    private JTable userTable;
    private DefaultTableModel tableModel;
    private UserDAO userDAO;

    public UserManagementFrame() {
        this.userDAO = new UserDAO();
        initComponents();
        loadUsers();
    }

    private void initComponents() {
        setTitle("User Management");
        setSize(700, 500);
        setLocationRelativeTo(null);

        JPanel mainPanel = new JPanel(new BorderLayout(10, 10));
        mainPanel.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));

        // Table
        String[] columns = {"ID", "Username", "Role", "Active"};
        tableModel = new DefaultTableModel(columns, 0) {
            @Override
            public boolean isCellEditable(int row, int column) {
                return false;
            }
        };
        userTable = new JTable(tableModel);
        JScrollPane scrollPane = new JScrollPane(userTable);
        mainPanel.add(scrollPane, BorderLayout.CENTER);

        // Buttons panel
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.LEFT));
        
        JButton addButton = new JButton("Add User");
        addButton.addActionListener(e -> addUser());
        
        JButton editButton = new JButton("Edit User");
        editButton.addActionListener(e -> editUser());
        
        JButton deleteButton = new JButton("Delete User");
        deleteButton.addActionListener(e -> deleteUser());
        
        JButton refreshButton = new JButton("Refresh");
        refreshButton.addActionListener(e -> loadUsers());

        buttonPanel.add(addButton);
        buttonPanel.add(editButton);
        buttonPanel.add(deleteButton);
        buttonPanel.add(refreshButton);

        mainPanel.add(buttonPanel, BorderLayout.SOUTH);

        add(mainPanel);
    }

    private void loadUsers() {
        try {
            tableModel.setRowCount(0);
            List<User> users = userDAO.getAllUsers();
            for (User user : users) {
                tableModel.addRow(new Object[]{
                        user.getId(),
                        user.getUsername(),
                        user.getRole(),
                        user.isActive() ? "Yes" : "No"
                });
            }
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error loading users: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void addUser() {
        UserDialog dialog = new UserDialog(this, null);
        dialog.setVisible(true);
        if (dialog.isConfirmed()) {
            try {
                userDAO.createUser(dialog.getUser());
                loadUsers();
                JOptionPane.showMessageDialog(this, "User added successfully");
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Error adding user: " + ex.getMessage(),
                        "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }

    private void editUser() {
        int selectedRow = userTable.getSelectedRow();
        if (selectedRow == -1) {
            JOptionPane.showMessageDialog(this, "Please select a user to edit",
                    "No Selection", JOptionPane.WARNING_MESSAGE);
            return;
        }

        try {
            int userId = (int) tableModel.getValueAt(selectedRow, 0);
            String username = (String) tableModel.getValueAt(selectedRow, 1);
            String role = (String) tableModel.getValueAt(selectedRow, 2);
            boolean active = "Yes".equals(tableModel.getValueAt(selectedRow, 3));
            
            User user = new User(userId, username, "", role, active);
            
            UserDialog dialog = new UserDialog(this, user);
            dialog.setVisible(true);
            
            if (dialog.isConfirmed()) {
                userDAO.updateUser(dialog.getUser());
                loadUsers();
                JOptionPane.showMessageDialog(this, "User updated successfully");
            }
        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error updating user: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    private void deleteUser() {
        int selectedRow = userTable.getSelectedRow();
        if (selectedRow == -1) {
            JOptionPane.showMessageDialog(this, "Please select a user to delete",
                    "No Selection", JOptionPane.WARNING_MESSAGE);
            return;
        }

        int confirm = JOptionPane.showConfirmDialog(this,
                "Are you sure you want to delete this user?",
                "Confirm Delete", JOptionPane.YES_NO_OPTION);

        if (confirm == JOptionPane.YES_OPTION) {
            try {
                int userId = (int) tableModel.getValueAt(selectedRow, 0);
                userDAO.deleteUser(userId);
                loadUsers();
                JOptionPane.showMessageDialog(this, "User deleted successfully");
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(this, "Error deleting user: " + ex.getMessage(),
                        "Error", JOptionPane.ERROR_MESSAGE);
            }
        }
    }
}
