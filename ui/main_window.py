import sys
import os
# Ensure project root is in sys.path for module imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QTableWidget, QTableWidgetItem,
                             QPushButton, QLineEdit, QLabel, QComboBox, QMessageBox, QTabWidget, QDialog,
                             QFormLayout, QDialogButtonBox, QFileDialog, QTextEdit, QInputDialog, QSizePolicy, QSpinBox,
                             QStackedWidget, QListWidget, QListWidgetItem, QSplitter, QFrame, QGraphicsBlurEffect,
                             QGroupBox, QDateEdit, QCheckBox, QScrollArea, QAbstractItemView) 
from PyQt5.QtGui import QPixmap, QPainter, QFont, QIcon, QPalette, QBrush, QLinearGradient, QColor, QPdfWriter, QFontDatabase
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint, QRect, QSize, QThread, pyqtSignal
from business.stock_manager import StockManager
from ui.translations import get_text
import os
from PyQt5.QtWidgets import QHeaderView

class LoadWorker(QThread):
    finished = pyqtSignal(list)

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        data = self.func()
        self.finished.emit(data)


def set_dialog_half_size(dialog):
    """Resize the dialog to half the available screen size and allow resizing by the user.
    Sets a sensible minimum size to avoid too-small windows."""
    try:
        screen = QApplication.primaryScreen()
        if screen:
            rect = screen.availableGeometry()
            w = max(400, rect.width() // 2)
            h = max(300, rect.height() // 2)
            # Set initial size and allow resizing
            dialog.resize(w, h)
            dialog.setMinimumSize(400, 300)
    except Exception:
        # Fallback: do nothing
        pass

class MainWindow(QMainWindow):
    def update_logs_table_headers(self):
        if hasattr(self, 'logs_table'):
            self.logs_table.setHorizontalHeaderLabels([
                get_text('date', self.current_lang),
                get_text('user', self.current_lang),
                get_text('action', self.current_lang)
            ])

    def get_stock_button_text(self):
        # Safely get total number of products; fall back to 0 on error
        count = 0
        try:
            count = self.stock_manager.get_total_products()
        except Exception:
            pass
        return f"📦 {get_text('stock', self.current_lang)} ({count})"

    def show_loading(self, message=None):
        if hasattr(self, '_loading_overlay') and self._loading_overlay:
            def retranslate_ui(self):
                return
        overlay = QWidget(self)
        overlay.setStyleSheet("background: rgba(0,0,0,0.35);")
        overlay.setGeometry(0, 0, self.width(), self.height())
        overlay.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        overlay.setAttribute(Qt.WA_DeleteOnClose, False)
        overlay.setObjectName('_loading_overlay')
        spinner = QLabel(overlay)
        spinner.setAlignment(Qt.AlignCenter)
        spinner.setStyleSheet("color: white; font-size: 32px; font-weight: bold;")
        spinner.setText("⏳" + ("\n" + message if message else "\nجاري التحميل ..."))
        spinner.setGeometry(0, 0, overlay.width(), overlay.height())
        overlay.show()
        self._loading_overlay = overlay

    def hide_loading(self):
        if hasattr(self, '_loading_overlay') and self._loading_overlay:
            self._loading_overlay.hide()

    def __init__(self, user_id, user_role, lang):
        super().__init__()
        # Always default to Arabic if not provided
        self.current_lang = lang.lower() if lang else "ar"
        if self.current_lang == "ar":
            self.setLayoutDirection(Qt.RightToLeft)
        else:
            self.setLayoutDirection(Qt.LeftToRight)
        self.stock_manager = StockManager()
        self.user_id = user_id
        self.user_role = user_role
        self.setWindowTitle(get_text('admin_panel' if self.user_role == 'admin' else 'user_panel', self.current_lang))
        self.setMinimumSize(1200, 800)
        self.resize(1600, 1000)

        # Load Cairo font
        font_db = QFontDatabase()
        if font_db.families().__contains__('Cairo'):
            self.arabic_font = QFont('Cairo', 16, QFont.Bold)
        else:
            self.arabic_font = QFont('Arial', 16, QFont.Bold)

        # Initialize button references to None to avoid attribute errors
        self.add_user_button = None
        self.edit_user_button = None
        self.delete_user_button = None
        self.add_product_button = None
        self.edit_product_button = None
        self.delete_product_button = None
        self.print_button = None
        self.export_button = None
        self.take_button = None
        self.search_name_button = None
        self.open_inventory_button = None
        self.search_button = None
        self.search_input = None
        self.backup_button = None
        self.restore_button = None
        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main horizontal layout: sidebar | main area
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sidebar
        self.create_sidebar()
        main_layout.addWidget(self.sidebar, 0)  # Fixed width

        # Main area
        self.create_main_area()
        main_layout.addWidget(self.main_widget, 1)  # Stretch

        # Create pages
        self.create_pages()

        # Show dashboard by default
        self.show_page('dashboard')

    def create_sidebar(self):
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(280)
        self.sidebar.setStyleSheet("""
            QWidget {
                background: #1E293B;
                color: white;
                border-right: 2px solid #475569;
            }
        """)
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        # Logo
        logo_label = QLabel()
        # Use resource helper so logo works both in dev and when bundled with PyInstaller
        try:
            from utils import resource_path
            logo_path = resource_path('logo.jpg')
        except Exception:
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'logo.jpg')
        pixmap = QPixmap(logo_path)
        # helpful debug prints (can be removed later)
        print("LOGO PATH:", logo_path)
        print("LOGO VALID:", not pixmap.isNull())
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        # App title (dashboard label, translated)
        self.sidebar_title_label = QLabel(get_text('dashboard', self.current_lang))
        self.sidebar_title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.sidebar_title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.sidebar_title_label, alignment=Qt.AlignCenter)

        # Spacer
        layout.addSpacing(30)

        # Buttons
        self.dashboard_btn = self.create_sidebar_button("🏠 " + get_text('dashboard', self.current_lang))
        self.dashboard_btn.clicked.connect(lambda: self.show_page('dashboard'))
        layout.addWidget(self.dashboard_btn)


                # Logs table headers
        self.update_logs_table_headers()
        if self.user_role == 'admin':
            self.users_btn = self.create_sidebar_button("👥 " + get_text('users', self.current_lang))
            self.users_btn.clicked.connect(lambda: self.show_page('users'))
            layout.addWidget(self.users_btn)

        self.stock_btn = self.create_sidebar_button(self.get_stock_button_text())
        self.stock_btn.clicked.connect(lambda: self.show_page('stock'))
        layout.addWidget(self.stock_btn)


        

        if self.user_role == 'admin':
            self.logs_btn = self.create_sidebar_button("📝 " + get_text('logs', self.current_lang))
            self.logs_btn.clicked.connect(lambda: self.show_page('logs'))
            layout.addWidget(self.logs_btn)

            self.backup_btn = self.create_sidebar_button("💾 " + get_text('backup', self.current_lang))
            self.backup_btn.clicked.connect(lambda: self.show_page('backup'))
            layout.addWidget(self.backup_btn)

        # Spacer
        layout.addStretch()

        # Language selector
        lang_layout = QVBoxLayout()
        lang_label = QLabel(get_text('language', self.current_lang))
        lang_label.setObjectName("language_label")
        lang_label.setStyleSheet("color: white; font-weight: bold;")
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['AR', 'EN', 'FR'])
        self.lang_combo.setCurrentText(self.current_lang.upper())
        self.lang_combo.currentTextChanged.connect(self.change_language)
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid #64748B;
                border-radius: 8px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        layout.addLayout(lang_layout)

        # Logout button
        self.logout_button = QPushButton("🚪 " + get_text('logout', self.current_lang))
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setStyleSheet("""
            QPushButton {
                background: #DC2626;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #B91C1C;
            }
        """)
        layout.addWidget(self.logout_button)

        # Update sidebar counts (e.g., inventory total)
        self.update_sidebar_counts()

    def create_main_area(self):
        self.main_widget = QWidget()
        layout = QVBoxLayout(self.main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Top header
        header = QLabel("مديرية التشغيل لولاية تيارت")
        header.setFont(self.arabic_font)
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                color: #1E293B;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
                background: rgba(255, 255, 255, 0.9);
                border-radius: 16px;
                border: 2px solid #E2E8F0;
            }
        """)
        layout.addWidget(header)

        # Content stack
        self.content_stack = QStackedWidget()
        # Content stack
        self.content_stack = QStackedWidget()
        layout.addWidget(self.content_stack)

    def create_pages(self):
        self.dashboard_page = self.create_dashboard_page()
        self.content_stack.addWidget(self.dashboard_page)

        if self.user_role == 'admin':
            self.users_page = self.create_users_page()
            self.content_stack.addWidget(self.users_page)

        self.stock_page = self.create_stock_page()
        self.content_stack.addWidget(self.stock_page)

        self.search_page = self.create_search_page()
        self.content_stack.addWidget(self.search_page)

        self.inventory_page = self.create_inventory_page()
        self.content_stack.addWidget(self.inventory_page)

       
        if self.user_role == 'admin':
            self.logs_page = self.create_logs_page()
            self.content_stack.addWidget(self.logs_page)

            self.backup_page = self.create_backup_page()
            self.backup_page = self.create_backup_page()
            self.content_stack.addWidget(self.backup_page)

    def show_page(self, page_name):
        if page_name == 'dashboard':
            self.content_stack.setCurrentWidget(self.dashboard_page)
        elif page_name == 'users' and self.user_role == 'admin':
            self.content_stack.setCurrentWidget(self.users_page)
        elif page_name == 'stock':
            self.content_stack.setCurrentWidget(self.stock_page)
        elif page_name == 'search':
            self.content_stack.setCurrentWidget(self.search_page)
        elif page_name == 'inventory':
            self.content_stack.setCurrentWidget(self.inventory_page)
    
        elif page_name == 'logs' and self.user_role == 'admin':
            self.content_stack.setCurrentWidget(self.logs_page)
        elif page_name == 'backup' and self.user_role == 'admin':
            self.content_stack.setCurrentWidget(self.backup_page)
        else:
            # If not admin, redirect to dashboard
            self.content_stack.setCurrentWidget(self.dashboard_page)

    def create_dashboard_page(self):
        page = QWidget()
        self.dashboard_layout = QVBoxLayout(page)
        self.dashboard_layout.setContentsMargins(30, 30, 30, 30)
        self.dashboard_layout.setSpacing(30)

        # Top summary cards (horizontal)
        self.summary_layout = QHBoxLayout()
        self.summary_layout.setSpacing(24)
        total_products, total_categories = self.stock_manager.get_statistics(self.user_id, self.user_role)
        try:
            total_users = len(self.stock_manager.get_users())
        except Exception:
            total_users = '-'
        try:
            today_activity = self.stock_manager.get_today_activity()
        except Exception:
            today_activity = '-'

        self.total_products_label = self.create_dashboard_card("📦", get_text('total_products', self.current_lang), str(total_products), "#2563EB")
        self.total_categories_label = self.create_dashboard_card("🗂️", get_text('total_categories', self.current_lang), str(total_categories), "#F59E42")
        self.total_users_label = self.create_dashboard_card("👥", get_text('users', self.current_lang), str(total_users), "#10B981")
        self.today_activity_label = self.create_dashboard_card("📈", get_text('today_activity', self.current_lang), str(today_activity), "#059669")
        self.summary_layout.addWidget(self.total_products_label)
        self.summary_layout.addWidget(self.total_categories_label)
        self.summary_layout.addWidget(self.total_users_label)
        self.summary_layout.addWidget(self.today_activity_label)
        self.dashboard_layout.addLayout(self.summary_layout)

        # Placeholder for future: charts/graphs
        self.chart_label = QLabel(get_text('stats_charts_placeholder', self.current_lang) if 'stats_charts_placeholder' in globals() else "[Charts and graphs coming soon]")
        self.chart_label.setAlignment(Qt.AlignCenter)
        self.chart_label.setStyleSheet("font-size: 18px; color: #64748B; margin-top: 40px;")
        self.dashboard_layout.addWidget(self.chart_label)

        self.dashboard_layout.addStretch()
        page.setStyleSheet("background: white;")
        # Add retranslate_ui for dashboard page
        def dashboard_retranslate_ui(lang):
            align = Qt.AlignRight if lang == 'ar' else Qt.AlignLeft
            if hasattr(self, 'dashboard_layout'):
                self.dashboard_layout.setAlignment(align)
            if hasattr(self, 'summary_layout'):
                self.summary_layout.setAlignment(align)
            if hasattr(self, 'total_products_label'):
                self.total_products_label.findChildren(QLabel)[1].setText(get_text('total_products', lang))
            if hasattr(self, 'total_categories_label'):
                self.total_categories_label.findChildren(QLabel)[1].setText(get_text('total_categories', lang))
            if hasattr(self, 'total_users_label'):
                self.total_users_label.findChildren(QLabel)[1].setText(get_text('users', lang))
            if hasattr(self, 'today_activity_label'):
                self.today_activity_label.findChildren(QLabel)[1].setText(get_text('today_activity', lang))
            if hasattr(self, 'chart_label'):
                self.chart_label.setText(get_text('stats_charts_placeholder', lang) if 'stats_charts_placeholder' in globals() else "[Charts and graphs coming soon]")
        page.retranslate_ui = dashboard_retranslate_ui
        return page

    def create_dashboard_card(self, icon, title, value, color):
        card = QGroupBox()
        card.setStyleSheet(f"""
            QGroupBox {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color}CC, stop:1 white);
                border: 2px solid {color};
                border-radius: 22px;
                padding: 24px 18px 18px 18px;
                min-width: 220px;
                max-width: 320px;
                min-height: 170px;
                box-shadow: 0 4px 24px #0002;
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(10)
        # أيقونة كبيرة
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 48px; margin-bottom: 8px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        # العنوان
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 20px; color: {color}; font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        # الرقم
        value_label = QLabel(value)
        value_label.setStyleSheet("font-size: 40px; font-weight: bold; color: #1E293B; margin-top: 8px;")
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        return card

    def create_sidebar_button(self, text):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background: #334155;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                text-align: left;
            }
            QPushButton:hover {
                background: #475569;
            }
            QPushButton:pressed {
                background: #64748B;
            }
        """)
        btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return btn

    def create_page_header(self, title_key):
        header = QWidget()
        layout = QVBoxLayout(header)
        layout.setAlignment(Qt.AlignCenter)

        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'logo.jpg')
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        # Arabic title
        title_label = QLabel("مديرية التشغيل لولاية تيارت")
        title_label.setFont(self.arabic_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        # Page title
        page_title = QLabel(get_text(title_key, self.current_lang))
        page_title.setFont(QFont("Arial", 18, QFont.Bold))
        page_title.setAlignment(Qt.AlignCenter)
        layout.addWidget(page_title, alignment=Qt.AlignCenter)

        return header

  #  def create_top_bar(self):
  #      self.top_bar = QFrame()
   #     self.top_bar.setFixedHeight(140)
    #    self.top_bar.setFrameStyle(QFrame.NoFrame)
     #   layout = QHBoxLayout(self.top_bar)
      #  layout.setContentsMargins(20, 10, 20, 10)

        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(__file__), '..', 'logo.jpg')
        pixmap = QPixmap(logo_path)
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        # Arabic text
        text_label = QLabel("مديرية التشغيل لولاية تيارت")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setFont(self.arabic_font)
        layout.addWidget(text_label, alignment=Qt.AlignCenter)

        # Spacer
        layout.addStretch()

        # Language selector
        lang_layout = QHBoxLayout()
        lang_label = QLabel(get_text('language', self.current_lang))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(['EN', 'AR', 'FR'])
        self.lang_combo.setCurrentText(self.current_lang.upper())
        self.lang_combo.currentTextChanged.connect(self.change_language)
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)

        # Logout button
        self.logout_button = QPushButton(get_text('logout', self.current_lang))
        self.logout_button.clicked.connect(self.logout)
        self.logout_button.setFixedSize(120, 45)
        lang_layout.addWidget(self.logout_button)

        layout.addLayout(lang_layout)

    def create_admin_layout(self):
        self.admin_widget = QWidget()
        layout = QVBoxLayout(self.admin_widget)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.create_users_tab()
        self.create_stock_tab()
        self.create_search_tab()
        self.create_inventory_tab()
        
        self.create_logs_tab()
        self.create_backup_tab()

    def create_user_layout(self):
        self.user_widget = QWidget()
        layout = QVBoxLayout(self.user_widget)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # --- USERS TAB (for user role) ---
        users_tab = QWidget()
        users_layout = QVBoxLayout(users_tab)

        # Header
        header = self.create_page_header('manage_users')
        # Store reference to the QLabel inside header for retranslate
        self.users_tab_title_label = None
        for child in header.findChildren(QLabel):
            if child.text() == get_text('manage_users', self.current_lang):
                self.users_tab_title_label = child
                break
        users_layout.addWidget(header)

        # Main card
        main_card = QGroupBox("")
        card_layout = QVBoxLayout(main_card)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels([
            get_text('username', self.current_lang),
            get_text('role', self.current_lang),
            get_text('actions', self.current_lang)
        ])
        card_layout.addWidget(self.users_table)
        users_layout.addWidget(main_card)

        # Buttons card (always create and assign attributes)
        buttons_card = QGroupBox("")
        buttons_layout = QHBoxLayout(buttons_card)
        buttons_layout.setSpacing(20)
        buttons_layout.setContentsMargins(20, 20, 20, 20)

        self.add_user_button = QPushButton("➕ " + get_text('add_user', self.current_lang))
        self.add_user_button.clicked.connect(self.add_user)
        self.edit_user_button = QPushButton("✏️ " + get_text('edit_user', self.current_lang))
        self.edit_user_button.clicked.connect(self.edit_user)
        self.delete_user_button = QPushButton("🗑️ " + get_text('delete_user', self.current_lang))
        self.delete_user_button.clicked.connect(self.delete_user)
        buttons_layout.addWidget(self.add_user_button)
        buttons_layout.addWidget(self.edit_user_button)
        buttons_layout.addWidget(self.delete_user_button)

        users_layout.addWidget(buttons_card)

        self.tabs.addTab(users_tab, get_text('manage_users', self.current_lang))
        self.load_users()

        self.create_stock_tab()
        self.create_search_tab()
        self.create_inventory_tab()

    def create_users_page(self):
        page = QWidget()
        page.setStyleSheet("background: white;")
        main_layout = QVBoxLayout(page)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(0)

        # Main card fills all available space
        card = QGroupBox()
        card.setStyleSheet("""
            QGroupBox {
                background: white;
                border: 2px solid #E2E8F0;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        card_layout.setContentsMargins(10, 10, 10, 10)

        # Title (store reference for retranslate)
        self.users_title_label = QLabel(get_text('manage_users', self.current_lang))
        self.users_title_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.users_title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.users_title_label)

        # Table (expands)
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels([
            get_text('username', self.current_lang),
            get_text('role', self.current_lang),
            get_text('actions', self.current_lang)
        ])
        header = self.users_table.horizontalHeader()
        for i in range(3):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        self.users_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card_layout.addWidget(self.users_table, 1)

        # Add card to main layout, make it expand
        main_layout.addWidget(card, 1)

        # Fixed bottom button bar
        button_bar = QWidget()
        button_bar.setStyleSheet("background: white;")
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(0, 20, 0, 10)
        button_layout.setSpacing(20)
        button_layout.addStretch()
        self.add_user_button = self.create_rounded_button("➕ " + get_text('add_user', self.current_lang))
        self.add_user_button.setMinimumWidth(180)
        self.add_user_button.clicked.connect(self.add_user)
        self.edit_user_button = self.create_rounded_button("✏️ " + get_text('edit_user', self.current_lang))
        self.edit_user_button.setMinimumWidth(180)
        self.edit_user_button.clicked.connect(self.edit_user)
        self.delete_user_button = self.create_rounded_button("🗑️ " + get_text('delete_user', self.current_lang))
        self.delete_user_button.setMinimumWidth(180)
        self.delete_user_button.clicked.connect(self.delete_user)
        button_layout.addWidget(self.add_user_button)
        button_layout.addWidget(self.edit_user_button)
        button_layout.addWidget(self.delete_user_button)
        button_layout.addStretch()
        main_layout.addWidget(button_bar, 0, Qt.AlignBottom)

        self.load_users()
        return page

    def create_rounded_button(self, text):
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3B82F6, stop:1 #1D4ED8);
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2563EB, stop:1 #1E40AF);
            }
            QPushButton:pressed {
                background: #1E40AF;
            }
        """)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return btn

    def create_stock_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        # Main card
        card = QGroupBox()
        card.setStyleSheet("""
            QGroupBox {
                background: white;
                border: 2px solid #E2E8F0;
                border-radius: 16px;
                padding: 20px;
            }
        """)
        card_layout = QVBoxLayout(card)

        # Title (store reference for retranslate)
        self.stock_title_label = QLabel(get_text('manage_stock', self.current_lang))
        self.stock_title_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.stock_title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(self.stock_title_label)

        # Search by name (simple)
        search_layout = QHBoxLayout()
        self.search_name_input = QLineEdit()
        self.search_name_input.setPlaceholderText(get_text('product_name', self.current_lang))
        self.search_name_button = self.create_rounded_button(get_text('search', self.current_lang))
        self.search_name_button.clicked.connect(self.search_by_name)
        search_layout.addWidget(self.search_name_input)
        search_layout.addWidget(self.search_name_button)
        card_layout.addLayout(search_layout)

        # Table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.products_table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.products_table.setHorizontalHeaderLabels([
            get_text('product_name', self.current_lang),
            get_text('category', self.current_lang),
            get_text('reference', self.current_lang),
            get_text('quantity', self.current_lang),
            get_text('entry_date', self.current_lang),
            get_text('exit_date', self.current_lang),
            get_text('actions', self.current_lang)
        ])
        header = self.products_table.horizontalHeader()
        for i in range(7):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        card_layout.addWidget(self.products_table)
        # double click shows details
        self.products_table.cellDoubleClicked.connect(self.on_product_double_clicked)

        # Bottom button bar (fixed at bottom)
        button_bar = QWidget()
        button_bar.setStyleSheet("background: white;")
        button_layout = QHBoxLayout(button_bar)
        button_layout.setContentsMargins(0, 20, 0, 10)
        button_layout.setSpacing(20)
        button_layout.addStretch()
        self.add_product_button = self.create_rounded_button("➕ " + get_text('add_product', self.current_lang))
        self.add_product_button.setMinimumWidth(140)
        self.add_product_button.clicked.connect(self.add_product)
        self.edit_product_button = self.create_rounded_button("✏️ " + get_text('edit_product', self.current_lang))
        self.edit_product_button.setMinimumWidth(140)
        self.edit_product_button.clicked.connect(self.edit_product)
        self.delete_product_button = self.create_rounded_button("🗑️ " + get_text('delete_product', self.current_lang))
        self.delete_product_button.setMinimumWidth(140)
        self.delete_product_button.clicked.connect(self.delete_product)
        button_layout.addWidget(self.add_product_button)
        button_layout.addWidget(self.edit_product_button)
        button_layout.addWidget(self.delete_product_button)
        button_layout.addStretch()

        # Add other buttons (take, print, export, inventory, pagination) above the bottom bar
        top_button_layout = QHBoxLayout()
        top_button_layout.setSpacing(15)
        self.take_button = self.create_rounded_button("🛒 " + get_text('stock_exit', self.current_lang))
        self.take_button.clicked.connect(self.take_selected_products)
        if self.user_role == 'admin':
            self.take_button.setVisible(False)
        self.print_button = self.create_rounded_button("🖨️ " + get_text('print', self.current_lang))
        self.print_button.clicked.connect(self.print_products)
        self.export_button = self.create_rounded_button("📊 " + get_text('export_excel', self.current_lang))
        self.export_button.clicked.connect(self.export_products)
        # self.open_inventory_button = self.create_rounded_button(get_text('inventory', self.current_lang))
        # self.open_inventory_button.clicked.connect(lambda: self.show_page('inventory'))
        self.products_page = 0
        self.products_page_size = 100
        self.prev_page_button = QPushButton("◀")
        self.prev_page_button.clicked.connect(self.prev_products_page)
        self.next_page_button = QPushButton("▶")
        self.next_page_button.clicked.connect(self.next_products_page)
        self.page_label = QLabel()
        self.update_page_label()
        top_button_layout.addWidget(self.take_button)
        top_button_layout.addWidget(self.print_button)
        top_button_layout.addWidget(self.export_button)
        # Removed inventory button from stock page
        top_button_layout.addWidget(self.prev_page_button)
        top_button_layout.addWidget(self.page_label)
        top_button_layout.addWidget(self.next_page_button)
        top_button_layout.addStretch()
        card_layout.addLayout(top_button_layout)

        layout.addWidget(card, 1)
        layout.addWidget(button_bar, 0, Qt.AlignBottom)

        return page

    def create_search_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        search_card = QGroupBox(get_text('advanced_search', self.current_lang))
        search_layout = QVBoxLayout(search_card)
        grid = QGridLayout()
        grid.setColumnStretch(1,3)
        grid.setColumnStretch(3,3)
        grid.setColumnStretch(5,2)
        grid.setColumnStretch(7,2)
        # Simplified search: by product name only (live)
        self.search_product_input = QLineEdit()
        self.search_product_input.setPlaceholderText(get_text('product_name', self.current_lang))
        grid.addWidget(QLabel(get_text('search', self.current_lang)), 0, 0)
        grid.addWidget(self.search_product_input, 0, 1)

        search_layout.addLayout(grid)
        layout.addWidget(search_card)

        results_card = QGroupBox(get_text('inventory', self.current_lang))
        results_layout = QVBoxLayout(results_card)

        self.search_table = QTableWidget()
        self.search_table.setColumnCount(6)
        self.search_table.setHorizontalHeaderLabels([
            get_text('product_name', self.current_lang),
            get_text('category', self.current_lang),
            get_text('reference', self.current_lang),
            get_text('quantity', self.current_lang),
            get_text('entry_date', self.current_lang),
            get_text('exit_date', self.current_lang)
        ])

        self.search_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        results_layout.addWidget(self.search_table)
        layout.addWidget(results_card)

        # Connect live search
        self.search_product_input.textChanged.connect(self.search_products_tab)
        # Populate initial products
        self.load_products_for_search()
        return widget


    def create_inventory_page(self):
        widget = QWidget()
        # Make the inventory page use all available space inside the main area
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Main card (expands to fill available space)
        main_card = QGroupBox(get_text('inventory', self.current_lang))
        main_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        card_layout = QVBoxLayout(main_card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(10)

        # Inventory table
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(6)
        self.inventory_table.setHorizontalHeaderLabels([
            get_text('product_name', self.current_lang),
            get_text('category', self.current_lang),
            get_text('reference', self.current_lang),
            get_text('quantity', self.current_lang),
            get_text('entry_date', self.current_lang),
            get_text('exit_date', self.current_lang)
        ])

        # Make columns stretch to take full width and set a larger font for readability
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignCenter)
        header_font = QFont("Arial", 14, QFont.Bold)
        self.inventory_table.horizontalHeader().setFont(header_font)
        self.inventory_table.setFont(QFont("Arial", 12))

        # Allow table to expand in both directions
        self.inventory_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.inventory_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.inventory_table.setSelectionMode(QAbstractItemView.SingleSelection)

        card_layout.addWidget(self.inventory_table, 1)

        # Bottom buttons (full-width style)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)


        # Create inventory page buttons (fix missing attribute)
        self.add_inventory_button = self.create_rounded_button("➕ " + get_text('add_product', self.current_lang))
        self.edit_inventory_button = self.create_rounded_button("✏️ " + get_text('edit_product', self.current_lang))
        self.delete_inventory_button = self.create_rounded_button("🗑️ " + get_text('delete_product', self.current_lang))
        self.print_inventory_button = self.create_rounded_button("🖨️ " + get_text('print', self.current_lang))
        self.export_inventory_button = self.create_rounded_button("📊 " + get_text('export_excel', self.current_lang))
        self.refresh_inventory_button = self.create_rounded_button("🔄 " + get_text('refresh', self.current_lang) if hasattr(self, 'refresh_inventory_button') else "🔄 Refresh")

        # Make buttons expand to fill horizontal space evenly
        for btn in (self.add_inventory_button, self.edit_inventory_button, self.delete_inventory_button, self.print_inventory_button, self.export_inventory_button, self.refresh_inventory_button):
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # Connect actions (reuse existing methods where appropriate)
        self.add_inventory_button.clicked.connect(self.add_product)
        self.edit_inventory_button.clicked.connect(self.edit_product)
        if self.user_role == 'admin':
            self.delete_inventory_button.clicked.connect(self.delete_product)
        else:
            self.delete_inventory_button.setVisible(False)
        self.print_inventory_button.clicked.connect(self.print_products)
        self.export_inventory_button.clicked.connect(self.export_products)
        self.refresh_inventory_button.clicked.connect(self.load_inventory)

        # Add buttons to layout and make them sit at the bottom
        button_layout.addWidget(self.add_inventory_button)
        button_layout.addWidget(self.edit_inventory_button)
        button_layout.addWidget(self.delete_inventory_button)
        button_layout.addWidget(self.print_inventory_button)
        button_layout.addWidget(self.export_inventory_button)
        button_layout.addWidget(self.refresh_inventory_button)
        card_layout.addLayout(button_layout)

        layout.addWidget(main_card, 1)

        # Load data
        self.load_inventory()
        return widget

    def create_stats_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Header
        header = QLabel(get_text('statistics', self.current_lang))
        header.setFont(QFont("Arial", 22, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        

        
        # Placeholder for future: charts/graphs
        chart_label = QLabel(get_text('stats_charts_placeholder', self.current_lang) if 'stats_charts_placeholder' in globals() else "[Charts and graphs coming soon]")
        chart_label.setAlignment(Qt.AlignCenter)
        chart_label.setStyleSheet("font-size: 18px; color: #64748B; margin-top: 40px;")
        layout.addWidget(chart_label)

        layout.addStretch()
        return widget

    def create_logs_page(self):
        from PyQt5.QtCore import QDate
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Filters: date range and user
        filters_layout = QHBoxLayout()
        filters_layout.setSpacing(10)

        # Date pickers
        self.logs_from_date = QDateEdit()
        self.logs_from_date.setCalendarPopup(True)
        self.logs_from_date.setDisplayFormat('dd/MM/yyyy')
        self.logs_from_date.setDate(QDate(2018, 1, 1))
        self.logs_to_date = QDateEdit()
        self.logs_to_date.setCalendarPopup(True)
        self.logs_to_date.setDisplayFormat('dd/MM/yyyy')
        self.logs_to_date.setDate(QDate.currentDate())
        filters_layout.addWidget(QLabel(get_text('from_date', self.current_lang)))
        filters_layout.addWidget(self.logs_from_date)
        filters_layout.addWidget(QLabel(get_text('to_date', self.current_lang)))
        filters_layout.addWidget(self.logs_to_date)

        # User dropdown
        self.logs_user_combo = QComboBox()
        self.logs_user_combo.addItem(get_text('all_users', self.current_lang), None)
        for user_id, username, _ in self.stock_manager.get_users():
            self.logs_user_combo.addItem(username, user_id)
        filters_layout.addWidget(QLabel(get_text('user', self.current_lang)))
        filters_layout.addWidget(self.logs_user_combo)

        # Search button
        self.logs_search_button = QPushButton(get_text('search', self.current_lang))
        self.logs_search_button.clicked.connect(self.load_logs_filtered)
        filters_layout.addWidget(self.logs_search_button)

        layout.addLayout(filters_layout)

        # Logs table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(3)
        self.logs_table.setHorizontalHeaderLabels([
            get_text('date', self.current_lang),
            get_text('user', self.current_lang),
            get_text('action', self.current_lang)
        ])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.logs_table)

        self.load_logs_filtered()
        return widget

    def load_logs_filtered(self):
        from_date = self.logs_from_date.date().toString('yyyy-MM-dd')
        to_date = self.logs_to_date.date().toString('yyyy-MM-dd')
        user_id = self.logs_user_combo.currentData()
        logs = self.stock_manager.db.get_logs_filtered(start_date=from_date, end_date=to_date, user_id=user_id)
        self.logs_table.setRowCount(len(logs))
        for row, (username, action, timestamp) in enumerate(logs):
            self.logs_table.setItem(row, 0, QTableWidgetItem(timestamp))
            self.logs_table.setItem(row, 1, QTableWidgetItem(username))
            self.logs_table.setItem(row, 2, QTableWidgetItem(action))

    def create_backup_page(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.backup_button = QPushButton(get_text('backup', self.current_lang))
        self.backup_button.clicked.connect(self.backup)
        self.restore_button = QPushButton(get_text('restore', self.current_lang))
        self.restore_button.clicked.connect(self.restore)
        layout.addWidget(self.backup_button)
        layout.addWidget(self.restore_button)

        return widget

    def change_admin_page(self, index):
        self.admin_stack.setCurrentIndex(index)

    def apply_styles(self):
        def apply_styles(self):
         self.setStyleSheet("""
    QMainWindow,QDialog{
        background:# white  ;
    }

    QLabel{
        color:#99bae8;
        font-size:15px;
    }

    QGroupBox{
        background:white;
        border:1px solid #CBD5E1;
        border-radius:12px;
        margin-top:10px;
    }

    QGroupBox::title{
        background:#047857;
        color:white;
        padding:4px 12px;
        border-radius:6px;
        font-weight:bold;
    }

    QPushButton{
        background:#0F766E;
        color:white;
        border:none;
        border-radius:10px;
        padding:10px 20px;
        font-weight:bold;
    }

    QPushButton:hover{
        background:#065F46;
    }

    QPushButton:pressed{
        background:#bcd1c4;
    }

    QTableWidget{
        background:white;
        border:1px solid #CBD5E1;
        border-radius:10px;
        gridline-color:#E5E7EB;
    }

    QHeaderView::section{
        background:#047857;
        color:white;
        padding:6px;
        font-weight:bold;
        border:none;
    }

    QComboBox,QLineEdit,QDateEdit{
        background:white;
        border:1px solid #CBD5E1;
        border-radius:8px;
        padding:6px;
    }

    QListWidget::item:selected{
        background:#0F766E;
        color:white;
    }
    """)


        # Add animations
        self.add_button_animation()
        self.add_table_animation()

    def add_button_animation(self):
        # Animate buttons on hover
        for button in self.findChildren(QPushButton):
            animation = QPropertyAnimation(button, b"geometry")
            animation.setDuration(200)
            animation.setEasingCurve(QEasingCurve.OutBounce)
            # Note: This is a placeholder; actual hover animation needs event handling

    def add_table_animation(self):
        # Add fade in animation for table
        if hasattr(self, 'products_table'):
            animation = QPropertyAnimation(self.products_table, b"windowOpacity")
            animation.setDuration(500)
            animation.setStartValue(0)
            animation.setEndValue(1)
            animation.start()

    def format_date_for_display(self, date_str: str) -> str:
        """Format a DB date/time string (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS) to dd/MM/yyyy HH:MM."""
        if not date_str:
            return ''
        try:
            s = str(date_str)
            parts = s.split(' ')
            date_part = parts[0]
            time_part = parts[1] if len(parts) > 1 else ''
            dparts = date_part.split('-')
            if len(dparts) >= 3:
                date_fmt = f"{dparts[2]}/{dparts[1]}/{dparts[0]}"
                if time_part:
                    tparts = time_part.split(':')
                    if len(tparts) >= 2:
                        return f"{date_fmt} {tparts[0]}:{tparts[1]}"
                    return f"{date_fmt} {time_part}"
                return date_fmt
        except Exception:
            pass
        return str(date_str)

    def print_products(self):
        from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
        from PyQt5.QtCore import QDateTime

        printer = QPrinter(QPrinter.HighResolution)
        # Force A4 full page printing and sensible margins
        try:
            printer.setPageSize(QPrinter.A4)
        except Exception:
            try:
                from PyQt5.QtGui import QPageSize
                printer.setPageSize(QPageSize(QPageSize.A4))
            except Exception:
                pass
        printer.setOrientation(QPrinter.Portrait)
        printer.setFullPage(False)
        printer.setPageMargins(10, 10, 10, 10, QPrinter.Millimeter)

        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)

            # Header
            y = 100
            # Logo
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'logo.jpg')
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                painter.drawPixmap(100, y, pixmap.scaled(100, 100, Qt.KeepAspectRatio))
            # Title

            # Use larger font for printing
            print_font = QFont(self.arabic_font.family(), 22, QFont.Bold)
            painter.setFont(print_font)
            painter.drawText(250, y + 50, "Direction de l'emploi de la wilaya de Tiaret")
            painter.drawText(250, y + 80, get_text('inventory', 'fr'))

            y += 150
            # Table - scale to fit the printable A4 rect (width and height)
            painter.save()
            page_rect = printer.pageRect()
            widget_size = self.products_table.size()
            scale_w = page_rect.width() / widget_size.width() if widget_size.width() else 1
            scale_h = page_rect.height() / widget_size.height() if widget_size.height() else 1
            scale = min(scale_w, scale_h)
            painter.scale(scale, scale)
            # Set larger font for table headers and cells
            table_font = QFont(self.arabic_font.family(), 16)
            self.products_table.setFont(table_font)
            self.products_table.horizontalHeader().setFont(QFont(self.arabic_font.family(), 17, QFont.Bold))
            # Temporarily set headers to French for printing
            original_headers = [self.products_table.horizontalHeaderItem(i).text() for i in range(self.products_table.columnCount())]
            french_headers = [get_text('product_name', 'fr'), get_text('category', 'fr'), get_text('reference', 'fr'), get_text('quantity', 'fr'), get_text('entry_date', 'fr'), get_text('exit_date', 'fr'), get_text('actions', 'fr')]
            for i in range(min(len(french_headers), self.products_table.columnCount())):
                self.products_table.horizontalHeaderItem(i).setText(french_headers[i])
            self.products_table.render(painter)
            # Restore original headers
            for i in range(len(original_headers)):
                self.products_table.horizontalHeaderItem(i).setText(original_headers[i])
            painter.restore()

            # Footer (include time)
            footer_y = page_rect.height() - 100
            painter.drawText(50, footer_y, f"Employé: {self.user_id}")
            painter.drawText(50, footer_y + 20, f"{get_text('date','fr')}: {QDateTime.currentDateTime().toString('dd/MM/yyyy HH:mm')}")
            painter.drawText(50, footer_y + 40, f"{get_text('total_products','fr')}: {self.stock_manager.get_statistics(self.user_id, self.user_role)[0]}")

            painter.end()
            QMessageBox.information(self, get_text('success', 'fr'), get_text('print_success', 'fr'))

    # Rest of the methods remain similar, but update for new structure

    def logout(self):
        reply = QMessageBox.question(self, get_text('logout', self.current_lang), get_text('confirm_logout', self.current_lang), QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._user_logout = True
            self.close()

    def was_user_logout(self):
        return getattr(self, '_user_logout', False)

    def change_language(self, lang):
        """Switch application language at runtime and update UI texts and layout, with crash prevention."""
        import traceback
        try:
            if not lang:
                return
            lang = lang.lower()
            self.current_lang = lang
            # Set application-wide layout direction (global RTL/LTR)
            app = QApplication.instance()
            if app:
                app.setLayoutDirection(Qt.RightToLeft if lang == 'ar' else Qt.LeftToRight)
            # Update all UI texts and layouts
            self.retranslate_ui()
        except Exception as e:
            print(f"Language switch error: {e}")
            traceback.print_exc()

    def retranslate_ui(self):
        """Update texts and headers for all visible UI elements according to `self.current_lang`.

        This method centralizes translations for Labels, Buttons, Table Headers, Window Title,
        tab texts and other dynamic UI elements so language switching works without restart.
        """
        lang = self.current_lang
        direction = Qt.RightToLeft if lang == 'ar' else Qt.LeftToRight
        app = QApplication.instance()
        if app:
            app.setLayoutDirection(direction)
        self.setLayoutDirection(direction)
        if hasattr(self, 'sidebar'):
            self.sidebar.setLayoutDirection(direction)
        if hasattr(self, 'main_widget'):
            self.main_widget.setLayoutDirection(direction)

        lang = self.current_lang
        direction = Qt.RightToLeft if lang == 'ar' else Qt.LeftToRight
        app = QApplication.instance()
        if app:
            app.setLayoutDirection(direction)
        self.setLayoutDirection(direction)
        if hasattr(self, 'sidebar'):
            self.sidebar.setLayoutDirection(direction)
        if hasattr(self, 'main_widget'):
            self.main_widget.setLayoutDirection(direction)

        # Window title
        self.setWindowTitle(get_text('admin_panel' if self.user_role == 'admin' else 'user_panel', lang))

        # Sidebar title label (dashboard label)
        if hasattr(self, 'sidebar_title_label'):
            self.sidebar_title_label.setText(get_text('dashboard', lang))
            if lang == 'ar':
                self.sidebar_title_label.setAlignment(Qt.AlignRight)
            else:
                self.sidebar_title_label.setAlignment(Qt.AlignLeft)
        # Sidebar buttons & labels
        if hasattr(self, 'dashboard_btn'):
            self.dashboard_btn.setText("🏠 " + get_text('dashboard', lang))
            self.dashboard_btn.setLayoutDirection(Qt.RightToLeft if lang == 'ar' else Qt.LeftToRight)
        if hasattr(self, 'users_btn'):
            self.users_btn.setText("👥 " + get_text('users', lang))
            self.users_btn.setLayoutDirection(Qt.RightToLeft if lang == 'ar' else Qt.LeftToRight)
        if hasattr(self, 'stock_btn'):
            self.stock_btn.setText(self.get_stock_button_text())
            self.stock_btn.setLayoutDirection(Qt.RightToLeft if lang == 'ar' else Qt.LeftToRight)
        if hasattr(self, 'logs_btn'):
            self.logs_btn.setText("📝 " + get_text('logs', lang))
            self.logs_btn.setLayoutDirection(Qt.RightToLeft if lang == 'ar' else Qt.LeftToRight)
        if hasattr(self, 'backup_btn'):
            self.backup_btn.setText("💾 " + get_text('backup', lang))
            self.backup_btn.setLayoutDirection(Qt.RightToLeft if lang == 'ar' else Qt.LeftToRight)
        if hasattr(self, 'logout_button'):
            self.logout_button.setText("🚪 " + get_text('logout', lang))
            self.logout_button.setLayoutDirection(Qt.RightToLeft if lang == 'ar' else Qt.LeftToRight)

        # Language label
        if hasattr(self, 'sidebar'):
            lang_label = self.sidebar.findChild(QLabel, "language_label")
            if lang_label:
                lang_label.setText(get_text('language', lang))
        if hasattr(self, 'lang_combo'):
            self.lang_combo.blockSignals(True)
            self.lang_combo.setCurrentText(lang.upper())
            self.lang_combo.blockSignals(False)
        # Main area
        if hasattr(self, 'main_widget'):
            self.main_widget.setLayoutDirection(direction)

        # QStackedWidget pages: call their retranslate_ui if available
        for page_attr in ['dashboard_page', 'users_page', 'stock_page', 'search_page', 'inventory_page', 'logs_page', 'backup_page']:
            page = getattr(self, page_attr, None)
            if page and hasattr(page, 'retranslate_ui'):
                try:
                    page.retranslate_ui(lang)
                except Exception as e:
                    print(f"Page {page_attr} retranslate error: {e}")

        # Table headers
        if hasattr(self, 'users_table'):
            self.users_table.setHorizontalHeaderLabels([
                get_text('username', lang),
                get_text('role', lang),
                get_text('actions', lang)
            ])
        if hasattr(self, 'products_table'):
            self.products_table.setHorizontalHeaderLabels([
                get_text('product_name', lang),
                get_text('category', lang),
                get_text('reference', lang),
                get_text('quantity', lang),
                get_text('entry_date', lang),
                get_text('exit_date', lang),
                get_text('actions', lang)
            ])
        if hasattr(self, 'inventory_table'):
            self.inventory_table.setHorizontalHeaderLabels([
                get_text('product_name', lang),
                get_text('category', lang),
                get_text('reference', lang),
                get_text('quantity', lang),
                get_text('entry_date', lang),
                get_text('exit_date', lang)
            ])
        if hasattr(self, 'search_table'):
            col_count = self.search_table.columnCount()
            if col_count == 4:
                self.search_table.setHorizontalHeaderLabels([
                    get_text('product_name', lang),
                    get_text('category', lang),
                    get_text('reference', lang),
                    get_text('quantity', lang)
                ])
            elif col_count == 6:
                self.search_table.setHorizontalHeaderLabels([
                    get_text('product_name', lang),
                    get_text('category', lang),
                    get_text('reference', lang),
                    get_text('quantity', lang),
                    get_text('entry_date', lang),
                    get_text('exit_date', lang)
                ])
            elif col_count == 7:
                self.search_table.setHorizontalHeaderLabels([
                    get_text('product_name', lang),
                    get_text('exit_quantity', lang),
                    get_text('person', lang),
                    get_text('exit_reason', lang),
                    get_text('date', lang),
                    get_text('time', lang),
                    get_text('actions', lang)
                ])

        # QLineEdit placeholders (all pages)
        for widget in self.findChildren(QLineEdit):
            if hasattr(widget, 'setPlaceholderText') and hasattr(widget, 'objectName'):
                name = widget.objectName().lower()
                if 'search' in name:
                    widget.setPlaceholderText(get_text('search', lang))
                elif 'username' in name:
                    widget.setPlaceholderText(get_text('username', lang))
                elif 'password' in name:
                    widget.setPlaceholderText(get_text('password', lang))
                elif 'product' in name:
                    widget.setPlaceholderText(get_text('product_name', lang))

        # RTL alignment for layouts
        if lang == 'ar':
            for layout in self.findChildren((QHBoxLayout, QVBoxLayout)):
                try:
                    layout.setAlignment(Qt.AlignRight)
                except Exception:
                    pass

        # Update sidebar counts and stats
        self.update_sidebar_counts()
        try:
            self.update_stats()
        except Exception:
            pass
            self.delete_user_button.setText(get_text('delete_user', self.current_lang))
        if hasattr(self, 'add_product_button') and self.add_product_button is not None:
            self.add_product_button.setText(get_text('add_product', self.current_lang))
        if hasattr(self, 'edit_product_button') and self.edit_product_button is not None:
            self.edit_product_button.setText(get_text('edit_product', self.current_lang))
        if hasattr(self, 'print_button') and self.print_button is not None:
            self.print_button.setText(get_text('print', self.current_lang))
        if hasattr(self, 'export_button') and self.export_button is not None:
            self.export_button.setText(get_text('export_excel', self.current_lang))
        if hasattr(self, 'delete_product_button') and self.delete_product_button is not None:
            self.delete_product_button.setText(get_text('delete_product', self.current_lang))
        if hasattr(self, 'open_inventory_button') and self.open_inventory_button is not None:
            self.open_inventory_button.setText(get_text('inventory', self.current_lang))
        if hasattr(self, 'search_button') and self.search_button is not None:
            self.search_button.setText(get_text('search', self.current_lang))
        if hasattr(self, 'search_input') and self.search_input is not None:
            self.search_input.setPlaceholderText(get_text('search', self.current_lang))
        if hasattr(self, 'backup_button') and self.backup_button is not None:
            self.backup_button.setText(get_text('backup', self.current_lang))
        if hasattr(self, 'restore_button') and self.restore_button is not None:
            self.restore_button.setText(get_text('restore', self.current_lang))


        # Update dashboard cards and chart label if present
        if hasattr(self, 'dashboard_page'):
            for card in self.dashboard_page.findChildren(QGroupBox):
                text = card.title() if hasattr(card, 'title') else ''
                if 'منتج' in text or 'Product' in text or 'Produit' in text:
                    card.setTitle(get_text('total_products', self.current_lang))
                elif 'فئة' in text or 'Category' in text or 'Catégorie' in text:
                    card.setTitle(get_text('total_categories', self.current_lang))
                elif 'مستخدم' in text or 'User' in text or 'Utilisateur' in text:
                    card.setTitle(get_text('users', self.current_lang))
                elif 'نشاط' in text or 'Activity' in text or 'Activité' in text:
                    card.setTitle(get_text('today_activity', self.current_lang))
            for label in self.dashboard_page.findChildren(QLabel):
                if '[Charts' in label.text() or 'مخططات' in label.text() or 'graphiques' in label.text():
                    label.setText(get_text('stats_charts_placeholder', self.current_lang) if 'stats_charts_placeholder' in globals() else "[Charts and graphs coming soon]")


        # --- Update QLabel titles for users and stock pages (admin and user) ---
        # Only update user-related labels/buttons if admin or attribute exists
        for label_name, key in [
            ('users_title_label', 'manage_users'),
            ('users_tab_title_label', 'manage_users'),
            ('stock_title_label', 'manage_stock'),
            ('stock_tab_title_label', 'manage_stock')
        ]:
            label = getattr(self, label_name, None)
            if label_name.startswith('users') and self.user_role != 'admin' and label is None:
                continue
            print(f'DEBUG: {label_name}:', type(label), repr(label))
            if label is not None:
                label.setText(get_text(key, self.current_lang))
            else:
                print(f'ERROR: {label_name} is None in retranslate_ui, skipping setText')
        # Search QGroupBox (admin and user)
        if hasattr(self, 'search_page'):
            for group in self.search_page.findChildren(QGroupBox):
                if 'بحث' in group.title() or 'search' in group.title().lower() or 'advanced_search' in group.objectName().lower():
                    group.setTitle(get_text('advanced_search', self.current_lang))
        # Product name placeholder (search input)
        if hasattr(self, 'search_name_input'):
            self.search_name_input.setPlaceholderText(get_text('product_name', self.current_lang))
        # Add/Edit/Delete User buttons (admin and user)
        # Add/Edit/Delete User buttons (admin and user) with debug prints
        for btn_name in ['add_user_button', 'edit_user_button', 'delete_user_button', 'search_name_button']:
            btn = getattr(self, btn_name, None)
            print(f'DEBUG: {btn_name}:', type(btn), repr(btn))
            if btn is None:
                print(f'ERROR: {btn_name} is None in retranslate_ui, skipping setText')
        if hasattr(self, 'add_user_button') and self.add_user_button is not None:
            print('DEBUG: setting add_user_button text')
            self.add_user_button.setText("➕ " + get_text('add_user', self.current_lang))
        if hasattr(self, 'edit_user_button') and self.edit_user_button is not None:
            self.delete_user_button.setText("🗑️ " + get_text('delete_user', self.current_lang))
        elif hasattr(self, 'delete_user_button'):
            print('ERROR: delete_user_button is None in retranslate_ui, skipping setText')
            self.edit_user_button.setText("✏️ " + get_text('edit_user', self.current_lang))
        import traceback
        for btn_name, key, prefix in [
            ('add_product_button', 'add_product', ''),
            ('edit_product_button', 'edit_product', ''),
            ('print_button', 'print', ''),
            ('export_button', 'export_excel', ''),
            ('delete_product_button', 'delete_product', ''),
            ('open_inventory_button', 'inventory', ''),
            ('search_button', 'search', ''),
            ('backup_button', 'backup', ''),
            ('restore_button', 'restore', ''),
        ]:
            btn = getattr(self, btn_name, None)
            try:
                if btn is not None:
                    btn.setText(f"{prefix}{get_text(key, self.current_lang)}")
                else:
                    print(f'ERROR: {btn_name} is None in retranslate_ui, skipping setText')
            except Exception as e:
                print(f'EXCEPTION: {btn_name} setText failed: {e}')
                traceback.print_exc()
    def update_sidebar_counts(self):
        if hasattr(self, 'stock_btn'):
            self.stock_btn.setText(self.get_stock_button_text())

    def create_users_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = self.create_page_header('manage_users')
        # Store reference to the QLabel inside header for retranslate
        self.users_tab_title_label = None
        for child in header.findChildren(QLabel):
            if child.text() == get_text('manage_users', self.current_lang):
                self.users_tab_title_label = child
                break
        layout.addWidget(header)

        # Main card
        main_card = QGroupBox("")
        card_layout = QVBoxLayout(main_card)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(3)
        self.users_table.setHorizontalHeaderLabels([get_text('username', self.current_lang), get_text('role', self.current_lang), get_text('actions', self.current_lang)])
        card_layout.addWidget(self.users_table)

        layout.addWidget(main_card)

        # Buttons card
        buttons_card = QGroupBox("")
        buttons_layout = QHBoxLayout(buttons_card)
        buttons_layout.setSpacing(20)
        buttons_layout.setContentsMargins(20, 20, 20, 20)

        self.add_user_button = QPushButton("➕ " + get_text('add_user', self.current_lang))
        self.add_user_button.clicked.connect(self.add_user)
        self.edit_user_button = QPushButton("✏️ " + get_text('edit_user', self.current_lang))
        self.edit_user_button.clicked.connect(self.edit_user)
        self.delete_user_button = QPushButton("🗑️ " + get_text('delete_user', self.current_lang))
        self.delete_user_button.clicked.connect(self.delete_user)
        buttons_layout.addWidget(self.add_user_button)
        buttons_layout.addWidget(self.edit_user_button)
        buttons_layout.addWidget(self.delete_user_button)

        layout.addWidget(buttons_card)

        self.tabs.addTab(widget, get_text('manage_users', self.current_lang))
        self.load_users()

    def load_users(self):
        self.show_loading("جاري تحميل المستخدمين ...")
        self.worker = LoadWorker(self.stock_manager.get_users)
        self.worker.finished.connect(self.on_users_loaded)
        self.worker.start()

    def on_users_loaded(self, users):
        self.users_table.setRowCount(len(users))
        for row, (user_id, username, role) in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(username))
            self.users_table.setItem(row, 1, QTableWidgetItem(role))
            self.users_table.item(row, 0).setData(Qt.UserRole, user_id)
        self.hide_loading()

    def add_user(self):
        dialog = UserDialog(self.current_lang)
        if dialog.exec_() == QDialog.Accepted:
            username, password, role = dialog.get_data()
            if self.stock_manager.add_user(username, password, role, self.user_id):
                QMessageBox.information(self, get_text('success', self.current_lang), get_text('user_added', self.current_lang))
                self.load_users()
            else:
                QMessageBox.warning(self, get_text('error', self.current_lang), 'User already exists or error')

    def edit_user(self):
        current_row = self.users_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, get_text('error', self.current_lang), 'Select a user')
            return
        user_id = self.users_table.item(current_row, 0).data(Qt.UserRole)
        username = self.users_table.item(current_row, 0).text()
        role = self.users_table.item(current_row, 1).text()
        # Always use the current language for the dialog
        dialog = UserDialog(self.current_lang, username, '', role)
        if hasattr(dialog, 'set_language'):
            dialog.set_language(self.current_lang)
        if dialog.exec_() == QDialog.Accepted:
            new_username, password, new_role = dialog.get_data()
            if self.stock_manager.update_user(user_id, new_username, password, new_role, self.user_id):
                QMessageBox.information(self, get_text('success', self.current_lang), get_text('user_updated', self.current_lang))
                self.load_users()
            else:
                QMessageBox.warning(self, get_text('error', self.current_lang), 'Error updating user')

    def delete_user(self):
        current_row = self.users_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, get_text('error', self.current_lang), 'Select a user')
            return
        user_id = self.users_table.item(current_row, 0).data(Qt.UserRole)
        reply = QMessageBox.question(self, get_text('confirm_delete', self.current_lang), 'Delete user?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.stock_manager.delete_user(user_id, self.user_id):
                QMessageBox.information(self, get_text('success', self.current_lang), get_text('user_deleted', self.current_lang))
                self.load_users()
            else:
                QMessageBox.warning(self, get_text('error', self.current_lang), 'Error deleting user')

    def create_stock_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = self.create_page_header('manage_stock')
        # Store reference to the QLabel inside header for retranslate (first QLabel after logo is always the title)
        self.stock_tab_title_label = None
        labels = header.findChildren(QLabel)
        if len(labels) >= 3:
            self.stock_tab_title_label = labels[2]  # 0: logo, 1: org, 2: title
        elif len(labels) > 0:
            self.stock_tab_title_label = labels[-1]
        layout.addWidget(header)

        # Main card
        main_card = QGroupBox("")
        card_layout = QVBoxLayout(main_card)

        # Table
        # Search by name (simple)
        search_layout = QHBoxLayout()
        self.search_name_input = QLineEdit()
        self.search_name_input.setPlaceholderText(get_text('product_name', self.current_lang))
        self.search_name_button = QPushButton(get_text('search', self.current_lang))
        self.search_name_button.clicked.connect(self.search_by_name)
        search_layout.addWidget(self.search_name_input)
        search_layout.addWidget(self.search_name_button)
        card_layout.addLayout(search_layout)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(7)
        self.products_table.setHorizontalHeaderLabels([get_text('product_name', self.current_lang), get_text('category', self.current_lang), get_text('reference', self.current_lang), get_text('quantity', self.current_lang), get_text('entry_date', self.current_lang), get_text('exit_date', self.current_lang), get_text('actions', self.current_lang)])
        card_layout.addWidget(self.products_table)

        layout.addWidget(main_card)

        # Buttons card
        buttons_card = QGroupBox("")
        buttons_layout = QHBoxLayout(buttons_card)
        buttons_layout.setSpacing(20)
        buttons_layout.setContentsMargins(20, 20, 20, 20)

        self.add_product_button = QPushButton("➕ " + get_text('add_product', self.current_lang))
        self.add_product_button.clicked.connect(self.add_product)
        self.edit_product_button = QPushButton("✏️ " + get_text('edit_product', self.current_lang))
        self.edit_product_button.clicked.connect(self.edit_product)
        self.take_button = QPushButton("🛒 " + get_text('stock_exit', self.current_lang))
        self.take_button.clicked.connect(self.take_selected_products)
        if self.user_role == 'admin':
            self.take_button.setVisible(False)
        self.print_button = QPushButton("🖨️ " + get_text('print', self.current_lang))
        self.print_button.clicked.connect(self.print_products)
        self.export_button = QPushButton("📊 " + get_text('export_excel', self.current_lang))
        self.export_button.clicked.connect(self.export_products)
        if self.user_role == 'admin':
            self.delete_product_button = QPushButton("🗑️ " + get_text('delete_product', self.current_lang))
            self.delete_product_button.clicked.connect(self.delete_product)
            buttons_layout.addWidget(self.delete_product_button)
        buttons_layout.addWidget(self.add_product_button)
        buttons_layout.addWidget(self.edit_product_button)
        buttons_layout.addWidget(self.take_button)
        buttons_layout.addWidget(self.print_button)
        buttons_layout.addWidget(self.export_button)

        layout.addWidget(buttons_card)

        self.tabs.addTab(widget, get_text('manage_stock', self.current_lang))
        self.load_products()

    def load_products(self):
        self.show_loading("جاري تحميل المنتجات ...")
        # Load all products then show current page
        self.worker = LoadWorker(self.stock_manager.get_products)
        self.worker.finished.connect(self.on_products_loaded_all)
        self.worker.start()

    def on_products_loaded_all(self, products):
        # store for pagination
        self._all_products = products
        self.show_products_page()
        # refresh sidebar counts (e.g., inventory total)
        self.update_sidebar_counts()
        self.hide_loading()

    def show_products_page(self):
        products = getattr(self, '_all_products', [])
        start = self.products_page * self.products_page_size
        end = start + self.products_page_size
        page_items = products[start:end]
        self.products_table.setRowCount(len(page_items))
        for row, (prod_id, name, cat, ref, qty, created_at, last_exit) in enumerate(page_items):
            self.products_table.setItem(row, 0, QTableWidgetItem(name))
            self.products_table.setItem(row, 1, QTableWidgetItem(cat))
            self.products_table.setItem(row, 2, QTableWidgetItem(ref or ''))
            self.products_table.setItem(row, 3, QTableWidgetItem(str(qty)))
            # Format dates to dd/MM/yyyy, handle None or invalid
            try:
                created_display = self.format_date_for_display(created_at) if created_at else "-"
            except Exception:
                created_display = "-"
            try:
                exit_display = self.format_date_for_display(last_exit) if last_exit else "-"
            except Exception:
                exit_display = "-"
            self.products_table.setItem(row, 4, QTableWidgetItem(created_display))
            self.products_table.setItem(row, 5, QTableWidgetItem(exit_display))
            self.products_table.item(row, 0).setData(Qt.UserRole, prod_id)
        self.update_page_label()

    def update_page_label(self):
        total = len(getattr(self, '_all_products', []))
        pages = max(1, (total + self.products_page_size - 1) // self.products_page_size)
        self.page_label.setText(f"{self.products_page + 1}/{pages}")

    def next_products_page(self):
        total = len(getattr(self, '_all_products', []))
        pages = max(1, (total + self.products_page_size - 1) // self.products_page_size)
        if self.products_page + 1 < pages:
            self.products_page += 1
            self.show_products_page()

    def prev_products_page(self):
        if self.products_page > 0:
            self.products_page -= 1
            self.show_products_page()

    def add_product(self):
        dialog = ProductDialog(self.stock_manager, self.current_lang)
        if dialog.exec_() == QDialog.Accepted:
            name, cat_id, ref_id, quantity = dialog.get_data()
            if self.stock_manager.add_product(name, cat_id, ref_id, quantity, self.user_id):
                QMessageBox.information(self, get_text('success', self.current_lang), get_text('product_added', self.current_lang))
                self.load_products()
            else:
                QMessageBox.warning(self, get_text('error', self.current_lang), 'Error adding product')

    def search_by_name(self):
        query = self.search_name_input.text().strip()
        if not query:
            self.load_products()
            return
        products = self.stock_manager.search_products(query)
        self.on_products_loaded(products)

    def edit_product(self):
        current_row = self.products_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, get_text('error', self.current_lang), get_text('select_product', self.current_lang))
            return
        prod_id = self.products_table.item(current_row, 0).data(Qt.UserRole)
        name = self.products_table.item(current_row, 0).text()
        cat_name = self.products_table.item(current_row, 1).text()
        ref_name = self.products_table.item(current_row, 2).text()
        qty = int(self.products_table.item(current_row, 3).text())
        # Find cat_id and ref_id
        categories = self.stock_manager.get_categories()
        cat_id = next((c[0] for c in categories if c[1] == cat_name), None)
        references = self.stock_manager.get_references(cat_id) if cat_id else []
        ref_id = next((r[0] for r in references if r[1] == ref_name), None) if ref_name else None
        dialog = ProductDialog(self.stock_manager, self.current_lang, name, cat_id, ref_id, qty, prod_id)
        if dialog.exec_() == QDialog.Accepted:
            new_name, new_cat_id, new_ref_id, new_qty = dialog.get_data()
            if new_qty < qty:
                # Quantity decreased, open stock exit dialog (user is shown and can confirm amount/reason)
                person = self.stock_manager.get_username(self.user_id) or ''
                exit_dialog = StockExitDialog(self.current_lang, qty, person)
                # Pre-set the spin to the difference
                exit_dialog.quantity_spin.setValue(qty - new_qty)
                if exit_dialog.exec_() == QDialog.Accepted:
                    qty_removed, reason = exit_dialog.get_data()
                    if not self.stock_manager.add_stock_exit(prod_id, qty_removed, person, reason, self.user_id):
                        QMessageBox.warning(self, get_text('error', self.current_lang), 'Failed to record stock exit')
                        return
            if self.stock_manager.update_product(prod_id, new_name, new_cat_id, new_ref_id, new_qty, self.user_id):
                QMessageBox.information(self, get_text('success', self.current_lang), get_text('product_updated', self.current_lang))
                self.load_products()
            else:
                QMessageBox.warning(self, get_text('error', self.current_lang), 'Error updating product')

    def delete_product(self):
        current_row = self.products_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, get_text('error', self.current_lang), 'Select a product')
            return
        prod_id = self.products_table.item(current_row, 0).data(Qt.UserRole)
        reply = QMessageBox.question(self, get_text('confirm_delete', self.current_lang), 'Delete product?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.stock_manager.delete_product(prod_id, self.user_id):
                QMessageBox.information(self, get_text('success', self.current_lang), get_text('product_deleted', self.current_lang))
                self.load_products()
            else:
                QMessageBox.warning(self, get_text('error', self.current_lang), 'Error deleting product')

    def on_product_double_clicked(self, row, col):
        prod_id = self.products_table.item(row, 0).data(Qt.UserRole)
        prod = self.stock_manager.get_product(prod_id)
        if not prod:
            QMessageBox.warning(self, get_text('error', self.current_lang), 'Product not found')
            return
        dialog = ProductDetailsDialog(self.current_lang, prod)
        # Connect take button in details dialog
        def _on_take():
            person = self.stock_manager.get_username(self.user_id) or ''
            dlg = StockExitDialog(self.current_lang, prod[4], person)
            if dlg.exec_() == QDialog.Accepted:
                qty, reason = dlg.get_data()
                if self.stock_manager.add_stock_exit(prod_id, qty, person, reason, self.user_id):
                    QMessageBox.information(self, get_text('success', self.current_lang), get_text('product_updated', self.current_lang))
                    self.load_products()
                else:
                    QMessageBox.warning(self, get_text('error', self.current_lang), 'Failed to take product')

        def _on_undo():
            # Undo the last exit for this product
            if self.stock_manager.undo_last_stock_exit(prod_id, self.user_id):
                QMessageBox.information(self, get_text('success', self.current_lang), get_text('product_updated', self.current_lang))
                self.load_products()
            else:
                    QMessageBox.warning(self, get_text('error', self.current_lang), get_text('undo_failed', self.current_lang))
        dialog.take_btn.clicked.connect(_on_take)
        dialog.undo_btn.clicked.connect(_on_undo)
        dialog.exec_()

    def take_selected_products(self):
        selected = [idx.row() for idx in self.products_table.selectionModel().selectedRows()]
        if not selected:
            QMessageBox.warning(self, get_text('error', self.current_lang), 'Select one or more products')
            return
        if len(selected) == 1:
            row = selected[0]
            prod_id = self.products_table.item(row, 0).data(Qt.UserRole)
            available = int(self.products_table.item(row, 3).text())
            person = self.stock_manager.get_username(self.user_id) or ''
            dlg = StockExitDialog(self.current_lang, available, person)
            if dlg.exec_() == QDialog.Accepted:
                qty, reason = dlg.get_data()
                if self.stock_manager.add_stock_exit(prod_id, qty, person, reason, self.user_id):
                    QMessageBox.information(self, get_text('success', self.current_lang), get_text('product_updated', self.current_lang))
                    self.load_products()
                else:
                    QMessageBox.warning(self, get_text('error', self.current_lang), 'Failed to take product')
        else:
            items = []
            for row in selected:
                prod_id = self.products_table.item(row, 0).data(Qt.UserRole)
                name = self.products_table.item(row, 0).text()
                available = int(self.products_table.item(row, 3).text())
                items.append((prod_id, name, available))
            dlg = BatchTakeDialog(self.current_lang, items)
            if dlg.exec_() == QDialog.Accepted:
                results, reason = dlg.get_data()
                person = self.stock_manager.get_username(self.user_id) or ''
                # Build list of (product_id, qty) for items with qty > 0
                items_to_take = [(pid, q) for pid, q in results if q > 0]
                if not items_to_take:
                    QMessageBox.warning(self, get_text('error', self.current_lang), get_text('no_quantities', self.current_lang))
                    return
                ok = self.stock_manager.batch_stock_exit(items_to_take, person, reason, self.user_id)
                if ok:
                    QMessageBox.information(self, get_text('success', self.current_lang), get_text('products_taken', self.current_lang))
                else:
                    QMessageBox.warning(self, get_text('error', self.current_lang), get_text('batch_failed', self.current_lang))
                self.load_products()

    def print_products(self):
        # Offer Preview / Print / Save to PDF
        from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
        from PyQt5.QtWidgets import QFileDialog
        from PyQt5.QtCore import QDateTime
        from ui.printer import preview_widget, save_table_to_pdf

        choice = QMessageBox()
        choice.setWindowTitle(get_text('print', self.current_lang))
        choice.setText(get_text('print', self.current_lang))
        preview_btn = choice.addButton(get_text('preview', self.current_lang), QMessageBox.ActionRole)
        pdf_btn = choice.addButton(get_text('save_pdf', self.current_lang), QMessageBox.ActionRole)
        print_btn = choice.addButton(get_text('print', self.current_lang), QMessageBox.ActionRole)
        choice.addButton(QMessageBox.Cancel)
        choice.exec_()

        if choice.clickedButton() == preview_btn:
            preview_widget(self.products_table, parent=self)
            return
        if choice.clickedButton() == pdf_btn:
            path, _ = QFileDialog.getSaveFileName(self, 'Save as PDF', '', 'PDF Files (*.pdf)')
            if path:
                save_table_to_pdf(self.products_table, path)
                QMessageBox.information(self, get_text('success', self.current_lang), get_text('export_success', self.current_lang))
            return
        if choice.clickedButton() == print_btn:
            # Use existing multi-page print (keep current behavior)
            from PyQt5.QtPrintSupport import QPrinter
            from PyQt5.QtCore import QDateTime

            printer = QPrinter(QPrinter.HighResolution)
            # Ensure A4 and margins
            try:
                printer.setPageSize(QPrinter.A4)
            except Exception:
                try:
                    from PyQt5.QtGui import QPageSize
                    printer.setPageSize(QPageSize(QPageSize.A4))
                except Exception:
                    pass
            printer.setOrientation(QPrinter.Portrait)
            printer.setFullPage(False)
            printer.setPageMargins(10, 10, 10, 10, QPrinter.Millimeter)

            dialog = QPrintDialog(printer, self)
            if dialog.exec_() == QPrintDialog.Accepted:
                painter = QPainter(printer)

                page_rect = printer.pageRect()
                header_height = 150
                footer_height = 120
                content_top = header_height
                available_height = page_rect.height() - header_height - footer_height

                def draw_page_header():
                    y = 30
                    logo_path = os.path.join(os.path.dirname(__file__), '..', 'logo.jpg')
                    pixmap = QPixmap(logo_path)
                    if not pixmap.isNull():
                        painter.drawPixmap(50, y, pixmap.scaled(80, 80, Qt.KeepAspectRatio))
                    painter.setFont(self.arabic_font)
                    painter.drawText(160, y + 30, "مديرية التشغيل لولاية تيارت")
                    painter.drawText(160, y + 60, get_text('inventory', 'fr'))

                total_rows = self.products_table.rowCount()
                table_width = self.products_table.viewport().width()
                table_header_h = self.products_table.horizontalHeader().height()
                row_heights = [self.products_table.rowHeight(r) for r in range(total_rows)]

                scale_w = page_rect.width() / table_width if table_width else 1
                scale = min(1.0, scale_w)
                avail_table_h = available_height / scale

                start_row = 0
                while start_row < total_rows:
                    painter.save()
                    draw_page_header()
                    painter.scale(scale, scale)

                    h_acc = table_header_h
                    end_row = start_row
                    while end_row < total_rows and (h_acc + row_heights[end_row]) <= avail_table_h:
                        h_acc += row_heights[end_row]
                        end_row += 1
                    if end_row == start_row:
                        end_row = min(start_row + 1, total_rows)
                        h_acc = table_header_h + row_heights[start_row]

                    y_offset = sum(row_heights[:start_row])
                    source_rect = QRect(0, y_offset, self.products_table.viewport().width(), h_acc)

                    self.products_table.render(painter, QPoint(10, content_top / scale), source_rect)
                    painter.restore()

                    footer_y = page_rect.height() - 80
                    painter.drawText(50, footer_y, f"{get_text('person','fr')}: {self.user_id}")
                    painter.drawText(50, footer_y + 20, f"{get_text('date','fr')}: {QDateTime.currentDateTime().toString('dd/MM/yyyy HH:mm')}")
                    painter.drawText(50, footer_y + 40, f"{get_text('total_products','fr')}: {self.stock_manager.get_statistics(self.user_id, self.user_role)[0]}")

                    start_row = end_row
                    if start_row < total_rows:
                        printer.newPage()

                painter.end()
                QMessageBox.information(self, get_text('success', 'fr'), get_text('print_success', 'fr'))

    def export_products(self):
        from PyQt5.QtWidgets import QFileDialog
        import pandas as pd
        path, _ = QFileDialog.getSaveFileName(self, 'Export to Excel', '', 'Excel Files (*.xlsx)')
        if path:
            self.show_loading("جاري تصدير المنتجات ...")
            try:
                data = []
                for row in range(self.products_table.rowCount()):
                    row_data = []
                    for col in range(self.products_table.columnCount() - 1):  # Exclude actions column
                        item = self.products_table.item(row, col)
                        row_data.append(item.text() if item else '')
                    # Normalize date/time columns (entry & exit) if present
                    if len(row_data) >= 6:
                        row_data[4] = self.format_date_for_display(row_data[4])
                    if len(row_data) >= 7:
                        row_data[5] = self.format_date_for_display(row_data[5])
                    data.append(row_data)
                # If entry/exit columns are present include them
                cols = [get_text('product_name', self.current_lang), get_text('category', self.current_lang), get_text('reference', self.current_lang), get_text('quantity', self.current_lang)]
                if self.products_table.columnCount() >= 6:
                    cols.append(get_text('entry_date', self.current_lang))
                if self.products_table.columnCount() >= 7:
                    cols.append(get_text('exit_date', self.current_lang))
                df = pd.DataFrame(data, columns=cols)
                df.to_excel(path, index=False)
                QMessageBox.information(self, get_text('success', self.current_lang), get_text('export_success', self.current_lang))
            finally:
                self.hide_loading()

    def create_search_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = self.create_page_header('search')
        layout.addWidget(header)

        # Search card
        search_card = QGroupBox("")
        search_layout = QVBoxLayout(search_card)

        # Filters
        filters_layout = QHBoxLayout()

        # Only product search input (live)
        self.search_product_input = QLineEdit()
        self.search_product_input.setPlaceholderText(get_text('product_name', self.current_lang))
        filters_layout.addWidget(QLabel(get_text('search', self.current_lang)))
        filters_layout.addWidget(self.search_product_input)

        search_layout.addLayout(filters_layout)

        # Buttons
        buttons_layout = QHBoxLayout()
        self.apply_filters_button = QPushButton(get_text('apply_filters', self.current_lang))
        self.apply_filters_button.clicked.connect(self.apply_filters)
        self.clear_filters_button = QPushButton(get_text('clear_filters', self.current_lang))
        self.clear_filters_button.clicked.connect(self.clear_filters)
        buttons_layout.addWidget(self.apply_filters_button)
        buttons_layout.addWidget(self.clear_filters_button)
        search_layout.addLayout(buttons_layout)

        layout.addWidget(search_card)

        # Results card
        results_card = QGroupBox("")
        results_layout = QVBoxLayout(results_card)

        self.search_table = QTableWidget()
        self.search_table.setColumnCount(7)
        self.search_table.setHorizontalHeaderLabels([get_text('product_name', self.current_lang), get_text('exit_quantity', self.current_lang), get_text('person', self.current_lang), get_text('exit_reason', self.current_lang), get_text('date', self.current_lang), get_text('time', self.current_lang), get_text('actions', self.current_lang)])
        results_layout.addWidget(self.search_table)

        layout.addWidget(results_card)

        self.tabs.addTab(widget, get_text('search', self.current_lang))
        self.clear_filters()

    def create_inventory_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = self.create_page_header('inventory')
        layout.addWidget(header)

        # Main card
        main_card = QGroupBox("")
        card_layout = QVBoxLayout(main_card)

        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(4)
        self.inventory_table.setHorizontalHeaderLabels([get_text('product_name', self.current_lang), get_text('category', self.current_lang), get_text('reference', self.current_lang), get_text('quantity', self.current_lang)])
        card_layout.addWidget(self.inventory_table)

        layout.addWidget(main_card)

        self.tabs.addTab(widget, get_text('inventory', self.current_lang))
        self.load_inventory()

    def load_inventory(self):
        inventory = self.stock_manager.get_inventory()
        self.inventory_table.setRowCount(len(inventory))
        for row, (prod_id, name, cat, ref, qty, created_at, last_exit) in enumerate(inventory):
            self.inventory_table.setItem(row, 0, QTableWidgetItem(name))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(cat))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(ref or ''))
            self.inventory_table.setItem(row, 3, QTableWidgetItem(str(qty)))
            # If inventory table has additional columns for dates, set them (safe guard)
            if self.inventory_table.columnCount() >= 6:
                self.inventory_table.setItem(row, 4, QTableWidgetItem(self.format_date_for_display(created_at)))
            if self.inventory_table.columnCount() >= 7:
                self.inventory_table.setItem(row, 5, QTableWidgetItem(self.format_date_for_display(last_exit)))
            self.inventory_table.item(row, 0).setData(Qt.UserRole, prod_id)

    def apply_filters(self):
        # Deprecated: advanced filters removed. Use live search instead.
        self.load_products_for_search()

    def load_products_for_search(self):
        products = self.stock_manager.get_products()
        self.populate_search_table(products)

    def search_products_tab(self, query: str):
        query = query.strip()
        if not query:
            self.load_products_for_search()
            return
        products = self.stock_manager.search_products(query)
        self.populate_search_table(products)

    def populate_search_table(self, products):
        # products tuples: (id, name, category, reference, qty, created_at, last_exit)
        self.search_table.setRowCount(len(products))
        for row, (prod_id, name, cat, ref, qty, created_at, last_exit) in enumerate(products):
            self.search_table.setItem(row, 0, QTableWidgetItem(name))
            self.search_table.setItem(row, 1, QTableWidgetItem(cat))
            self.search_table.setItem(row, 2, QTableWidgetItem(ref or ''))
            self.search_table.setItem(row, 3, QTableWidgetItem(str(qty)))
            self.search_table.setItem(row, 4, QTableWidgetItem(self.format_date_for_display(created_at)))
            self.search_table.setItem(row, 5, QTableWidgetItem(self.format_date_for_display(last_exit)))
            self.search_table.item(row, 0).setData(Qt.UserRole, prod_id)

    

    def update_stats(self):
        total_products, total_categories = self.stock_manager.get_statistics(self.user_id, self.user_role)
        def set_card_label_text(card, text):
            if card is not None:
                labels = card.findChildren(QLabel)
                # Assume the second QLabel is the title (icon, title, value)
                if len(labels) >= 2:
                    labels[1].setText(text)
        set_card_label_text(self.total_products_label, f"{get_text('total_products', self.current_lang)}: {total_products}")
        set_card_label_text(self.total_categories_label, f"{get_text('total_categories', self.current_lang)}: {total_categories}")

    def create_logs_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = self.create_page_header('logs')
        layout.addWidget(header)

        # Main card
        main_card = QGroupBox("")
        card_layout = QVBoxLayout(main_card)

        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        logs = self.stock_manager.get_logs()
        for username, action, timestamp in logs:
            self.logs_text.append(f"{timestamp} - {username}: {action}")
        card_layout.addWidget(self.logs_text)

        layout.addWidget(main_card)

        self.tabs.addTab(widget, get_text('logs', self.current_lang))

    def create_backup_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Header
        header = self.create_page_header('backup')
        layout.addWidget(header)

        # Main card
        main_card = QGroupBox("")
        card_layout = QVBoxLayout(main_card)

        self.backup_button = QPushButton("💾 " + get_text('backup', self.current_lang))
        self.backup_button.clicked.connect(self.backup)
        self.restore_button = QPushButton("🔄 " + get_text('restore', self.current_lang))
        self.restore_button.clicked.connect(self.restore)
        card_layout.addWidget(self.backup_button)
        card_layout.addWidget(self.restore_button)

        layout.addWidget(main_card)

        self.tabs.addTab(widget, get_text('backup', self.current_lang))

    def backup(self):
        path, _ = QFileDialog.getSaveFileName(self, 'Backup Database', '', 'Database Files (*.db)')
        if path:
            self.stock_manager.backup_database(path)
            QMessageBox.information(self, get_text('success', self.current_lang), get_text('backup_success', self.current_lang))

    def restore(self):
        path, _ = QFileDialog.getOpenFileName(self, 'Restore Database', '', 'Database Files (*.db)')
        if path:
            self.stock_manager.restore_database(path)
            QMessageBox.information(self, get_text('success', self.current_lang), get_text('restore_success', self.current_lang))
            # Reload data
            self.load_users()
            self.load_products()

class UserDialog(QDialog):
    def __init__(self, lang, username='', password='', role='user'):
        super().__init__()
        self.setStyleSheet("""
            QDialog {
                background: white;
                border-radius: 16px;
                border: 2px solid #E2E8F0;
            }
            QWidget {
                background: white;
            }
            QLabel {
                color: #374151;
                font-size: 14px;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                background: white;
            }
            QComboBox {
                background: white;
                border: 1px solid #D1D5DB;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        self.lang = lang
        self.init_ui(username, password, role)
        # Ensure consistent dialog size
        set_dialog_half_size(self)

    def init_ui(self, username, password, role):
        self.setWindowTitle(get_text('add_user' if not username else 'edit_user', self.lang))
        layout = QFormLayout()

        self.username_input = QLineEdit(username)
        self.password_input = QLineEdit(password)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.role_combo = QComboBox()
        self.role_combo.addItems(['admin', 'user'])
        self.role_combo.setCurrentText(role)

        layout.addRow(get_text('username', self.lang), self.username_input)
        layout.addRow(get_text('password', self.lang), self.password_input)
        layout.addRow(get_text('role', self.lang), self.role_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        return self.username_input.text(), self.password_input.text(), self.role_combo.currentText()

class BatchTakeDialog(QDialog):
    def __init__(self, lang, items: list):
        # items: list of tuples (prod_id, name, available_qty)
        super().__init__()
        self.lang = lang
        self.items = items
        self.setWindowTitle(get_text('stock_exit', self.lang))
        layout = QVBoxLayout()
        self.spinboxes = []
        for prod_id, name, avail in items:
            h = QHBoxLayout()
            h.addWidget(QLabel(name))
            sb = QSpinBox()
            sb.setMinimum(0)
            sb.setMaximum(avail)
            sb.setValue(0)
            h.addWidget(sb)
            layout.addLayout(h)
            self.spinboxes.append((prod_id, sb))
        self.reason_input = QTextEdit()
        self.reason_input.setMaximumHeight(100)
        layout.addWidget(QLabel(get_text('reason', self.lang)))
        layout.addWidget(self.reason_input)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)
        set_dialog_half_size(self)

    def get_data(self):
        results = [(prod_id, sb.value()) for prod_id, sb in self.spinboxes]
        return results, self.reason_input.toPlainText()


class ProductDetailsDialog(QDialog):
    def __init__(self, lang, prod_tuple):
        # prod_tuple: (id, name, category, reference, quantity, created_at, last_exit)
        super().__init__()
        self.lang = lang
        pid, name, cat, ref, qty, created_at, last_exit = prod_tuple
        self.pid = pid
        self.setWindowTitle(get_text('product_name', self.lang) + ': ' + name)
        layout = QFormLayout()
        layout.addRow(get_text('product_name', self.lang), QLabel(name))
        layout.addRow(get_text('quantity', self.lang), QLabel(str(qty)))
        layout.addRow(get_text('category', self.lang), QLabel(cat))
        layout.addRow(get_text('reference', self.lang), QLabel(ref or ''))
        layout.addRow(get_text('entry_date', self.lang), QLabel(self.format_dt(created_at)))
        layout.addRow(get_text('exit_date', self.lang), QLabel(self.format_dt(last_exit)))
        # Buttons: Take and Undo last exit
        buttons_h = QHBoxLayout()
        self.take_btn = QPushButton(get_text('stock_exit', self.lang))
        buttons_h.addWidget(self.take_btn)
        self.undo_btn = QPushButton(get_text('undo_last_exit', self.lang))
        buttons_h.addWidget(self.undo_btn)
        layout.addRow(buttons_h)
        self.setLayout(layout)
        set_dialog_half_size(self)

    def format_dt(self, d):
        if not d:
            return ''
        s = str(d)
        parts = s.split(' ')
        date_part = parts[0]
        time_part = parts[1] if len(parts) > 1 else ''
        dparts = date_part.split('-')
        if len(dparts) >= 3:
            date_fmt = f"{dparts[2]}/{dparts[1]}/{dparts[0]}"
            if time_part:
                tparts = time_part.split(':')
                if len(tparts) >= 2:
                    return f"{date_fmt} {tparts[0]}:{tparts[1]}"
                return f"{date_fmt} {time_part}"
            return date_fmt
        return str(d)


class ProductDialog(QDialog):
    def __init__(self, stock_manager, lang, name='', cat_id=None, ref_id=None, qty=0, prod_id=None):
        super().__init__()
        # Force a white background for dialog and inner cards to avoid dark/black appearance
        self.setStyleSheet("""
QDialog, QGroupBox, QWidget, QFrame {
    background: #FFFFFF;
}

QLineEdit, QSpinBox, QComboBox {
    background: white;
    color: #1F2937;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 6px;
}

QLabel {
    color: #1F2937;
}

QDialogButtonBox QPushButton {
    background: white;
    color: black; 
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 6px 12px;
}

QDialogButtonBox QPushButton:hover {
    background: #F3F4F6;
    border-color: #9CA3AF;
    color: #1F2937;
    
}
""")

        self.stock_manager = stock_manager
        self.lang = lang
        self.prod_id = prod_id
        self.init_ui(name, cat_id, ref_id, qty)

    def init_ui(self, name, cat_id, ref_id, qty):
        self.setWindowTitle(get_text('add_product' if not name else 'edit_product', self.lang))
        layout = QFormLayout()

        self.name_input = QLineEdit(name)
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(0)
        self.quantity_input.setValue(qty)

        self.category_combo = QComboBox()
        categories = self.stock_manager.get_categories()
        for cat_id_, cat_name in categories:
            self.category_combo.addItem(cat_name, cat_id_)
        if cat_id:
            index = self.category_combo.findData(cat_id)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
        self.category_combo.currentIndexChanged.connect(self.load_references)

        self.reference_combo = QComboBox()
        self.reference_combo.addItem('', None)  # No reference
        self.load_references()
        if ref_id:
            index = self.reference_combo.findData(ref_id)
            if index >= 0:
                self.reference_combo.setCurrentIndex(index)

        # Add new category/reference buttons
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(self.category_combo)
        add_cat_button = QPushButton('+')
        add_cat_button.clicked.connect(self.add_category)
        cat_layout.addWidget(add_cat_button)

        ref_layout = QHBoxLayout()
        ref_layout.addWidget(self.reference_combo)
        add_ref_button = QPushButton('+')
        add_ref_button.clicked.connect(self.add_reference)
        ref_layout.addWidget(add_ref_button)

        layout.addRow(get_text('product_name', self.lang), self.name_input)
        layout.addRow(get_text('quantity', self.lang), self.quantity_input)
        layout.addRow(get_text('category', self.lang), cat_layout)
        layout.addRow(get_text('reference', self.lang), ref_layout)

        # If editing existing product, show entry and last exit dates
        if self.prod_id is not None:
            prod = self.stock_manager.get_product(self.prod_id)
            if prod:
                created_at = prod[5]
                last_exit = prod[6]
                # Format dates to dd/MM/yyyy HH:MM for display
                def _fmt(d):
                    if not d:
                        return ''
                    s = str(d)
                    parts = s.split(' ')
                    date_part = parts[0]
                    time_part = parts[1] if len(parts) > 1 else ''
                    dparts = date_part.split('-')
                    if len(dparts) >= 3:
                        date_fmt = f"{dparts[2]}/{dparts[1]}/{dparts[0]}"
                        if time_part:
                            tparts = time_part.split(':')
                            if len(tparts) >= 2:
                                return f"{date_fmt} {tparts[0]}:{tparts[1]}"
                            return f"{date_fmt} {time_part}"
                        return date_fmt
                    return str(d)
                layout.addRow(get_text('entry_date', self.lang), QLabel(_fmt(created_at)))
                layout.addRow(get_text('exit_date', self.lang), QLabel(_fmt(last_exit)))

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)
        set_dialog_half_size(self)

    def load_references(self):
        self.reference_combo.clear()
        self.reference_combo.addItem('', None)
        cat_id = self.category_combo.currentData()
        if cat_id:
            references = self.stock_manager.get_references(cat_id)
            for ref_id, ref_name in references:
                self.reference_combo.addItem(ref_name, ref_id)

    def add_category(self):
        text, ok = QInputDialog.getText(self, get_text('category', self.lang), 'New category:')
        if ok and text:
            cat_id = self.stock_manager.add_category(text, 1)  # Assume user_id 1 for simplicity
            if cat_id:
                self.category_combo.addItem(text, cat_id)
                self.category_combo.setCurrentIndex(self.category_combo.count() - 1)
                QMessageBox.information(self, get_text('success', self.lang), get_text('category_added', self.lang))
            else:
                QMessageBox.warning(self, get_text('error', self.lang), 'Error adding category')

    def add_reference(self):
        cat_id = self.category_combo.currentData()
        if not cat_id:
            QMessageBox.warning(self, get_text('error', self.lang), 'Select category first')
            return
        text, ok = QInputDialog.getText(self, get_text('reference', self.lang), 'New reference:')
        if ok and text:
            ref_id = self.stock_manager.add_reference(text, cat_id, 1)  # Assume user_id 1
            if ref_id:
                self.reference_combo.addItem(text, ref_id)
                self.reference_combo.setCurrentIndex(self.reference_combo.count() - 1)
                QMessageBox.information(self, get_text('success', self.lang), get_text('reference_added', self.lang))
            else:
                QMessageBox.warning(self, get_text('error', self.lang), 'Error adding reference')

    def get_data(self):
        return self.name_input.text(), self.category_combo.currentData(), self.reference_combo.currentData(), self.quantity_input.value()

class StockExitDialog(QDialog):
    def __init__(self, lang, max_quantity, person: str = None):
        super().__init__()
        # Force a white background for the dialog to avoid dark/black fullscreen look
        self.setStyleSheet("""
QDialog, QGroupBox, QWidget, QFrame {
    background: #FFFFFF;
}

QSpinBox, QTextEdit, QLineEdit, QLabel {
    color: #7ba0d4;
    background: white;
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    padding: 6px;
}

QDialogButtonBox QPushButton {
    background: #3B82F6;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 6px 12px;
}
        """)
        self.lang = lang
        self.max_quantity = max_quantity
        self.person = person
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(get_text('stock_exit', self.lang))
        layout = QFormLayout()

        # Show the person (taken from session) if provided
        if self.person:
            layout.addRow(get_text('person', self.lang), QLabel(self.person))

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(self.max_quantity)
        self.quantity_spin.setValue(1)

        self.reason_input = QTextEdit()
        self.reason_input.setMaximumHeight(100)

        layout.addRow(get_text('quantity', self.lang), self.quantity_spin)
        layout.addRow(get_text('reason', self.lang), self.reason_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_data(self):
        # returns (quantity, reason)
        return self.quantity_spin.value(), self.reason_input.toPlainText()