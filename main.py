import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import all modules
from database import DATA_MANAGER
from ui_helpers import RegistrationDialog
from customer_dashboard import CustomerDashboard
from staff_dashboard import StaffDashboard
from admin_dashboard import AdminDashboard


class LoginScreen(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(100, 100, 100, 100)

        # Title
        title = QLabel("🧺 WashDesk")
        title.setFont(QFont('Arial', 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #01579b;")
        main_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Laundry Services and Monitoring System")
        subtitle.setFont(QFont('Arial', 14))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #555555;")
        main_layout.addWidget(subtitle)

        main_layout.addSpacing(30)

        # Inputs
        input_container = QWidget()
        input_container.setStyleSheet(
            "border: 1px solid #ddd; padding: 20px; background-color: white; border-radius: 8px;")
        input_layout = QVBoxLayout(input_container)
        input_layout.setSpacing(15)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setFixedHeight(30)
        self.email_input.setFont(QFont('Arial', 10))
        self.email_input.setStyleSheet(
            "border: 1px solid #ccc; border-radius: 4px; padding: 5px; color: #01579b;")
        input_layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setFixedHeight(30)
        self.password_input.setFont(QFont('Arial', 10))
        self.password_input.setStyleSheet(
            "border: 1px solid #ccc; border-radius: 4px; padding: 5px; color: #01579b;")
        input_layout.addWidget(self.password_input)

        main_layout.addWidget(input_container)
        main_layout.addSpacing(20)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        login_btn = QPushButton("Login")
        login_btn.setFixedSize(120, 30)
        login_btn.setFont(QFont('Arial', 10))
        login_btn.setStyleSheet(
            "background-color: #0288d1; color: white; border-radius: 4px; border: none;")
        login_btn.clicked.connect(self.attempt_login)
        button_layout.addWidget(login_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        main_layout.addSpacing(10)

        # Register link
        register_label = QLabel("Don't have an account?")
        register_label.setFont(QFont('Arial', 10))
        register_label.setAlignment(Qt.AlignCenter)
        register_label.setStyleSheet("color: #555555;")
        main_layout.addWidget(register_label)

        register_btn = QPushButton("Register")
        register_btn.setFixedSize(120, 30)
        register_btn.setFont(QFont('Arial', 10))
        register_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; border-radius: 4px; border: none;")
        register_btn.clicked.connect(self.open_registration)
        register_h_layout = QHBoxLayout()
        register_h_layout.addStretch()
        register_h_layout.addWidget(register_btn)
        register_h_layout.addStretch()
        main_layout.addLayout(register_h_layout)

        main_layout.addStretch()
        self.setStyleSheet("background-color: #f5f5f5;")

    def open_registration(self):
        try:
            reg_dialog = RegistrationDialog(DATA_MANAGER, self)
            reg_dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open registration: {str(e)}")

    def attempt_login(self):
        try:
            email = self.email_input.text().strip()
            password = self.password_input.text().strip()

            if not email or not password:
                QMessageBox.warning(self, "Error", "Please enter both email and password.")
                return

            role, user_data = DATA_MANAGER.get_user(email)

            if user_data and DATA_MANAGER.verify_password(password, user_data['password']):
                if 'email' not in user_data:
                    user_data = dict(user_data)
                    user_data['email'] = email
                self.parent_window.switch_to_dashboard(role, user_data)
            else:
                QMessageBox.critical(self, "Login Failed", "Invalid email or password.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {str(e)}")


class WashDeskManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WashDesk Application")
        self.showMaximized()

        self.dashboards = {}
        self.current_dashboard = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.stack_layout = QVBoxLayout(self.central_widget)
        self.stack_layout.setContentsMargins(0, 0, 0, 0)

        self.switch_to_login()

    def clear_screen(self):
        while self.stack_layout.count():
            item = self.stack_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def switch_to_login(self):
        try:
            self.clear_screen()
            if self.current_dashboard:
                self.current_dashboard.close()
                self.current_dashboard = None

            self.login_screen = LoginScreen(self)
            self.stack_layout.addWidget(self.login_screen)
            self.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to switch to login: {str(e)}")

    def switch_to_dashboard(self, role, user_data):
        try:
            self.hide()
            if role == 'Customer':
                dashboard = CustomerDashboard(user_data, DATA_MANAGER)
            elif role == 'Staff':
                dashboard = StaffDashboard(DATA_MANAGER)
            elif role == 'Admin':
                dashboard = AdminDashboard(DATA_MANAGER)

            dashboard.closeEvent = lambda event: self.switch_to_login()
            self.current_dashboard = dashboard
            dashboard.show()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to switch to dashboard: {str(e)}")


if __name__ == '__main__':
    try:
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()

        app.setFont(QFont('Arial', 10))
        manager = WashDeskManager()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Application failed to start: {str(e)}")