from PyQt5.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QDialog, QFrame, QGridLayout, QMessageBox,
    QHeaderView, QTableWidget, QTableWidgetItem, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import re


class BaseDashboard(QMainWindow):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.showMaximized()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_h_layout = QHBoxLayout(self.central_widget)
        self.main_h_layout.setContentsMargins(0, 0, 0, 0)
        self.main_h_layout.setSpacing(0)
        self.current_content = QWidget()
        self.buttons = {}
        self.init_content_area()

    def create_title_bar(self, title_text, bg_color, text_color):
        title_bar = QLabel(title_text)
        title_bar.setFont(QFont('Arial', 18, QFont.Bold))
        title_bar.setAlignment(Qt.AlignCenter)
        title_bar.setFixedHeight(50)
        title_bar.setStyleSheet(f"background-color: {bg_color}; color: {text_color}; border-radius: 4px; padding: 10px;")
        return title_bar

    def create_nav_button(self, text, screen_key, action=None, icon=""):
        btn_text = f"{icon} {text}" if icon else text
        btn = QPushButton(btn_text)
        btn.setFixedHeight(40)
        btn.setFont(QFont('Arial', 10))
        btn.setStyleSheet(
            "background-color: #e0e0e0; text-align: left; padding-left: 15px; border: none; border-radius: 4px;"
            "color: #333333;")
        if action:
            btn.clicked.connect(action)
        return btn

    def init_content_area(self):
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: #ffffff; border-radius: 8px;")
        self.content_stack = QVBoxLayout(self.content_widget)
        self.content_stack.setContentsMargins(40, 20, 40, 20)
        self.content_stack.setSpacing(15)
        self.content_stack.addWidget(self.current_content)
        self.main_h_layout.addWidget(self.content_widget)

    def show_screen(self, screen_key, content_creator):
        for key, btn in self.buttons.items():
            btn.setStyleSheet(
                "background-color: #ffcdd2; text-align: left; padding-left: 15px; border: none; border-radius: 4px;"
                "color: #333333; font-weight: bold;" if key == screen_key else
                "background-color: #e0e0e0; text-align: left; padding-left: 15px; border: none; border-radius: 4px;"
                "color: #333333;"
            )
        if self.current_content:
            self.current_content.deleteLater()
        try:
            new_content = content_creator()
            self.current_content = new_content
            self.content_stack.addWidget(self.current_content)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load screen: {str(e)}")


class RegistrationDialog(QDialog):
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.dm = data_manager
        self.setWindowTitle("Register")
        self.setGeometry(400, 50, 400, 500)
        self.setModal(True)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(15)
        self.layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Create New Account")
        title.setFont(QFont('Arial', 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #01579b;")
        self.layout.addWidget(title)
        self.layout.addSpacing(20)

        self.fields = {}
        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        role_label = QLabel("Role:")
        role_label.setFont(QFont('Arial', 10))
        role_label.setFixedWidth(100)
        self.role_combo = QComboBox()
        self.role_combo.setFixedHeight(30)
        self.role_combo.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px;")
        self.role_combo.addItems(["Customer", "Staff", "Admin"])
        self.role_combo.currentIndexChanged.connect(self.toggle_fields)
        form_layout.addWidget(role_label, 0, 0, Qt.AlignRight)
        form_layout.addWidget(self.role_combo, 0, 1)

        fields_config = [
            ('Fullname', False), ('Email', False), ('Password', True),
            ('Contact Info', False)
        ]

        for i, (label_text, is_password) in enumerate(fields_config, start=1):
            label = QLabel(label_text + ":")
            label.setFont(QFont('Arial', 10))
            label.setFixedWidth(100)
            input_widget = QLineEdit()
            input_widget.setFixedHeight(30)
            input_widget.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px;")
            if is_password:
                input_widget.setEchoMode(QLineEdit.Password)
            form_layout.addWidget(label, i, 0, Qt.AlignRight)
            form_layout.addWidget(input_widget, i, 1)
            self.fields[label_text] = input_widget

        self.address_container = QWidget()
        address_layout = QVBoxLayout(self.address_container)
        address_label = QLabel("Home Address:")
        address_label.setFont(QFont('Arial', 10))
        self.fields['Home Address'] = QLineEdit()
        self.fields['Home Address'].setFixedHeight(30)
        self.fields['Home Address'].setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px;")
        address_layout.addWidget(address_label)
        address_layout.addWidget(self.fields['Home Address'])
        form_layout.addWidget(self.address_container, len(fields_config) + 1, 0, 1, 2)

        self.layout.addLayout(form_layout)
        self.layout.addSpacing(20)

        self.register_btn = QPushButton("Register")
        self.register_btn.setFixedSize(150, 35)
        self.register_btn.setFont(QFont('Arial', 12, QFont.Bold))
        self.register_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; border-radius: 4px; border: none;")
        self.register_btn.clicked.connect(self.attempt_registration)

        btn_h_layout = QHBoxLayout()
        btn_h_layout.addStretch()
        btn_h_layout.addWidget(self.register_btn)
        btn_h_layout.addStretch()
        self.layout.addLayout(btn_h_layout)

        self.layout.addStretch()
        self.toggle_fields(0)

    def toggle_fields(self, index):
        role = self.role_combo.currentText()
        is_customer = role == 'Customer'
        self.address_container.setVisible(is_customer)

    def attempt_registration(self):
        try:
            role = self.role_combo.currentText()
            data = {k.replace(' ', '_').lower(): v.text().strip() for k, v in self.fields.items()}

            # Validate required fields
            required_fields = ['fullname', 'email', 'password', 'contact_info']
            if role == 'Customer':
                required_fields.append('home_address')
            if any(not data.get(field) for field in required_fields):
                QMessageBox.warning(self, "Error", "All required fields must be filled.")
                return

            # Validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
                QMessageBox.warning(self, "Error", "Invalid email format.")
                return

            # Check for duplicate email
            for r in self.dm.user_data:
                if data['email'] in self.dm.user_data[r]:
                    QMessageBox.critical(self, "Error", f"Email '{data['email']}' already exists.")
                    return

            # Attempt registration
            if self.dm.register_user(role, data):
                QMessageBox.information(self, "Success", f"{role} account registered successfully.")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Registration failed due to an internal error.")
        except pymysql.Error as e:
            QMessageBox.critical(self, "Database Error", f"Database error during registration: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Registration failed: {str(e)}")
            print(f"Registration error details: {str(e)}")  # Debug output