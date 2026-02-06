import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from database.init_db import create_database
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow



def main():
    app = QApplication(sys.argv)
    app.setApplicationName("gestion de stock")
    app.setApplicationDisplayName("gestion de stock")
    # Create database if not exists
    create_database()

    # Show login dialog
    login_dialog = LoginDialog()
    if login_dialog.exec_() == LoginDialog.Accepted:
        user_id = login_dialog.user_id
        user_role = login_dialog.user_role
        lang = login_dialog.current_lang

        # Show main window
        main_window = MainWindow(user_id, user_role, lang)
        main_window.showMaximized()
        app.setActiveWindow(main_window)
        main_window.show()
        app.exec_()
    sys.exit(0)

if __name__ == '__main__':
    main()