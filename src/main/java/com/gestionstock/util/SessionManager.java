package com.gestionstock.util;

import com.gestionstock.model.User;

public class SessionManager {
    // Thread-safe session management for single-user desktop application
    // Note: For multi-threaded environments, consider using ThreadLocal or synchronization
    private static volatile User currentUser;

    public static synchronized void setCurrentUser(User user) {
        currentUser = user;
    }

    public static synchronized User getCurrentUser() {
        return currentUser;
    }

    public static synchronized boolean isLoggedIn() {
        return currentUser != null;
    }

    public static synchronized void logout() {
        currentUser = null;
    }

    public static synchronized boolean isAdmin() {
        return currentUser != null && "ADMIN".equals(currentUser.getRole());
    }
}
