from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox, QApplication, QGroupBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from business.stock_manager import StockManager
from ui.translations import get_text
import os
import sys

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.stock_manager = StockManager()
        self.current_lang = 'ar'  # Set Arabic as default
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(get_text('login', self.current_lang))
        # Set initial size to half the available screen and allow resizing
        # Always open at a large, visually balanced size
        # Force a large, modern login dialog size
        self.resize(700, 700)
        self.setMinimumSize(700, 700)

        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #F8FAFC, stop:1 #E2E8F0);
            }
            QLabel#titleLabel {
                color: #1E293B;
                font-size: 26px;
                font-weight: bold;
                margin-bottom: 8px;
            }
            QLabel#subtitleLabel {
                color: #64748B;
                font-size: 16px;
                margin-bottom: 18px;
            }
            QLabel {
                color: #1F2937;
                font-size: 15px;
            }
            QLineEdit {
                padding: 12px;
                border: 1.5px solid #CBD5E1;
                border-radius: 10px;
                background: #F9FAFB;
                font-size: 15px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2563EB, stop:1 #1D4ED8);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 0;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background: #1D4ED8;
            }
            QComboBox {
                background: white;
                border: 1.5px solid #CBD5E1;
                border-radius: 8px;
                padding: 7px;
                font-size: 15px;
            }
            QGroupBox#loginCard {
                background: white;
                border: 2px solid #E2E8F0;
                border-radius: 18px;
                padding: 32px 32px 24px 32px;
                margin-top: 30px;
                box-shadow: 0 4px 24px #0001;
            }
        """)

        # Outer layout
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Centered card
        card = QGroupBox()
        card.setObjectName("loginCard")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(18)
        card_layout.setContentsMargins(32, 32, 32, 32)

        # Logo
        logo_label = QLabel()
        logo_label.setFixedSize(110, 110)
        logo_label.setStyleSheet("border-radius: 55px; background: #F1F5F9; margin-bottom: 8px;")
        logo_path = None
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'logo.jpg'),
            os.path.join(os.path.dirname(sys.executable), 'logo.jpg'),
            os.path.join(os.path.dirname(sys.argv[0]), 'logo.jpg'),
            'logo.jpg'
        ]
        try:
            from utils import resource_path
            possible_paths.insert(0, resource_path('logo.jpg'))
        except Exception:
            pass
        for path in possible_paths:
            if os.path.exists(path):
                logo_path = path
                break
        if logo_path:
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        card_layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        # Title and subtitle
        title_label = QLabel(get_text('login', self.current_lang))
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)
        subtitle_label = QLabel("مديرية التشغيل لولاية تيارت")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle_label)

        # Language selector
        lang_layout = QHBoxLayout()
        lang_layout.setSpacing(8)
        lang_label = QLabel(get_text('language', self.current_lang))
        lang_label.setObjectName("language_label")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['AR', 'EN', 'FR'])
        self.lang_combo.setCurrentText(self.current_lang.upper())
        self.lang_combo.currentTextChanged.connect(self.change_language)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        lang_layout.addStretch()
        card_layout.addLayout(lang_layout)

        # Username
        user_row = QHBoxLayout()
        self.username_label = QLabel(get_text('username', self.current_lang))
        self.username_label.setFixedWidth(90)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(get_text('username', self.current_lang))
        user_row.addWidget(self.username_label)
        user_row.addWidget(self.username_input)
        card_layout.addLayout(user_row)

        # Password
        pass_row = QHBoxLayout()
        self.password_label = QLabel(get_text('password', self.current_lang))
        self.password_label.setFixedWidth(90)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText(get_text('password', self.current_lang))
        self.password_input.setEchoMode(QLineEdit.Password)
        pass_row.addWidget(self.password_label)
        pass_row.addWidget(self.password_input)
        card_layout.addLayout(pass_row)

        # Error label (hidden by default)
        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #DC2626; font-size: 14px; margin-top: 4px;")
        self.error_label.setVisible(False)
        card_layout.addWidget(self.error_label)

        # Login button
        self.login_button = QPushButton(get_text('login_button', self.current_lang))
        self.login_button.clicked.connect(self.login)
        card_layout.addWidget(self.login_button)

        card_layout.addStretch()
        outer_layout.addStretch()
        outer_layout.addWidget(card, alignment=Qt.AlignCenter)
        outer_layout.addStretch()
        self.setLayout(outer_layout)

    def change_language(self, lang):
        try:
            if not lang:
                return
            updating_combo = False
            if hasattr(self, 'lang_combo'):
                if self.lang_combo.currentText().lower() != lang.lower():
                    updating_combo = True
                    self.lang_combo.blockSignals(True)
                    self.lang_combo.setCurrentText(lang.upper())
            self.current_lang = lang.lower()
            self.apply_direction()
            self.retranslate_ui()
            if hasattr(self, 'lang_combo') and updating_combo:
                self.lang_combo.blockSignals(False)
        except Exception as e:
            print(f"LoginDialog language switch error: {e}")

    def retranslate_ui(self):
        try:
            lang = self.current_lang
            self.setWindowTitle(get_text('login', lang))
            if hasattr(self, 'username_label'):
                self.username_label.setText(get_text('username', lang))
            if hasattr(self, 'username_input'):
                self.username_input.setPlaceholderText(get_text('username', lang))
            if hasattr(self, 'password_label'):
                self.password_label.setText(get_text('password', lang))
            if hasattr(self, 'password_input'):
                self.password_input.setPlaceholderText(get_text('password', lang))
            if hasattr(self, 'login_button'):
                self.login_button.setText(get_text('login_button', lang))
            # Language label
            lang_label = None
            for widget in self.findChildren(QLabel):
                if widget.objectName() == 'language_label':
                    lang_label = widget
                    break
            if lang_label:
                lang_label.setText(get_text('language', lang))
            # Title label
            for widget in self.findChildren(QLabel):
                if widget.objectName() == 'titleLabel':
                    widget.setText(get_text('login', lang))
                if widget.objectName() == 'subtitleLabel':
                    widget.setText(get_text('subtitle', lang) if 'subtitle' in lang else "مديرية التشغيل لولاية تيارت")
        except Exception as e:
            print(f"LoginDialog retranslate error: {e}")

    def update_texts(self):
        self.setWindowTitle(get_text('login', self.current_lang))
        self.username_label.setText(get_text('username', self.current_lang))
        self.password_label.setText(get_text('password', self.current_lang))
        self.login_button.setText(get_text('login_button', self.current_lang))

    def apply_direction(self):
        dir = Qt.RightToLeft if self.current_lang == 'ar' else Qt.LeftToRight
        app = QApplication.instance()
        if app:
            app.setLayoutDirection(dir)
        self.setLayoutDirection(dir)
        for widget in self.findChildren((QLineEdit, QLabel, QComboBox)):
            try:
                widget.setLayoutDirection(dir)
            except Exception:
                pass
            if isinstance(widget, QLineEdit):
                widget.setAlignment(Qt.AlignRight | Qt.AlignVCenter if dir == Qt.RightToLeft else Qt.AlignLeft | Qt.AlignVCenter)
            if isinstance(widget, QLabel):
                widget.setAlignment(Qt.AlignRight | Qt.AlignVCenter if dir == Qt.RightToLeft else Qt.AlignLeft | Qt.AlignVCenter)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.error_label.setVisible(False)
        result = self.stock_manager.authenticate(username, password)
        if result:
            self.user_id, self.user_role = result
            self.accept()
        else:
            self.error_label.setText(get_text('invalid_credentials', self.current_lang))
            self.error_label.setVisible(True)