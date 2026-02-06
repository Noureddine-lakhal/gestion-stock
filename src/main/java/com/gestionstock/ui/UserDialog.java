package com.gestionstock.ui;

import com.gestionstock.model.User;

import javax.swing.*;
import java.awt.*;

public class UserDialog extends JDialog {
    private JTextField usernameField;
    private JPasswordField passwordField;
    private JComboBox<String> roleComboBox;
    private JCheckBox activeCheckBox;
    private boolean confirmed = false;
    private User user;
    private boolean isEdit;

    public UserDialog(Frame parent, User user) {
        super(parent, user == null ? "Add User" : "Edit User", true);
        this.user = user;
        this.isEdit = user != null;
        initComponents();
        if (user != null) {
            fillFields(user);
        }
    }

    private void initComponents() {
        setSize(400, 300);
        setLocationRelativeTo(getParent());

        JPanel mainPanel = new JPanel(new GridBagLayout());
        mainPanel.setBorder(BorderFactory.createEmptyBorder(15, 15, 15, 15));
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.insets = new Insets(5, 5, 5, 5);
        gbc.fill = GridBagConstraints.HORIZONTAL;

        int row = 0;

        // Username
        gbc.gridx = 0;
        gbc.gridy = row;
        mainPanel.add(new JLabel("Username:"), gbc);
        
        usernameField = new JTextField(20);
        gbc.gridx = 1;
        mainPanel.add(usernameField, gbc);
        row++;

        // Password
        gbc.gridx = 0;
        gbc.gridy = row;
        String passwordLabel = isEdit ? "New Password (leave blank to keep current):" : "Password:";
        mainPanel.add(new JLabel(passwordLabel), gbc);
        
        passwordField = new JPasswordField(20);
        gbc.gridx = 1;
        mainPanel.add(passwordField, gbc);
        row++;

        // Role
        gbc.gridx = 0;
        gbc.gridy = row;
        mainPanel.add(new JLabel("Role:"), gbc);
        
        roleComboBox = new JComboBox<>(new String[]{"ADMIN", "USER"});
        gbc.gridx = 1;
        mainPanel.add(roleComboBox, gbc);
        row++;

        // Active
        gbc.gridx = 0;
        gbc.gridy = row;
        mainPanel.add(new JLabel("Active:"), gbc);
        
        activeCheckBox = new JCheckBox();
        activeCheckBox.setSelected(true);
        gbc.gridx = 1;
        mainPanel.add(activeCheckBox, gbc);
        row++;

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

    private void fillFields(User user) {
        usernameField.setText(user.getUsername());
        roleComboBox.setSelectedItem(user.getRole());
        activeCheckBox.setSelected(user.isActive());
    }

    private void save() {
        try {
            String username = usernameField.getText().trim();
            String password = new String(passwordField.getPassword());
            String role = (String) roleComboBox.getSelectedItem();
            boolean active = activeCheckBox.isSelected();

            if (username.isEmpty()) {
                JOptionPane.showMessageDialog(this, "Username is required",
                        "Validation Error", JOptionPane.ERROR_MESSAGE);
                return;
            }

            if (!isEdit && password.isEmpty()) {
                JOptionPane.showMessageDialog(this, "Password is required for new users",
                        "Validation Error", JOptionPane.ERROR_MESSAGE);
                return;
            }

            if (user == null) {
                user = new User();
            }
            user.setUsername(username);
            if (!password.isEmpty()) {
                user.setPassword(password);
            }
            user.setRole(role);
            user.setActive(active);

            confirmed = true;
            dispose();

        } catch (Exception ex) {
            JOptionPane.showMessageDialog(this, "Error: " + ex.getMessage(),
                    "Error", JOptionPane.ERROR_MESSAGE);
        }
    }

    public boolean isConfirmed() {
        return confirmed;
    }

    public User getUser() {
        return user;
    }
}
