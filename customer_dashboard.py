from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QCalendarWidget, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QSpinBox
)
from PyQt5.QtCore import Qt, QDate, QEvent
from PyQt5.QtGui import QFont, QColor
from ui_helpers import BaseDashboard
import re
import uuid
import datetime


class CustomerDashboard(BaseDashboard):
    def __init__(self, user_data, data_manager, parent_app=None):
        super().__init__("Customer Dashboard", parent_app)
        self.user_data = user_data
        self.dm = data_manager
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setMinimumDate(QDate.currentDate())
        self.calendar_widget.setGridVisible(True)
        self.calendar_widget.setFixedSize(250, 200)
        self.calendar_widget.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
        self.calendar_widget.selectionChanged.connect(self.update_date_dropdown)
        self.calendar_dialog = None
        self.cart_items = []
        self.init_sidebar()
        self.dm.order_updated.connect(lambda: self.refresh_active_view(['status']))
        self.show_screen('order', self.create_order_laundry_screen)

    def init_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #fafafa; border-right: 1px solid #ddd;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_layout.setSpacing(8)

        logo_label = QLabel("🧺 WashDesk\nYour Laundry Services")
        logo_label.setFont(QFont('Arial', 10, QFont.Bold))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("color: #01579b; padding: 10px;")
        sidebar_layout.addWidget(logo_label, alignment=Qt.AlignTop)
        sidebar_layout.addSpacing(15)

        self.buttons['order'] = self.create_nav_button("Order Laundry", 'order',
                                                       lambda: self.show_screen('order',
                                                                                self.create_order_laundry_screen), icon="🛒")
        self.buttons['schedule'] = self.create_nav_button("Schedule Service", 'schedule',
                                                          lambda: self.show_screen('schedule',
                                                                                   self.create_schedule_screen), icon="📅")
        self.buttons['status'] = self.create_nav_button("Order Status", 'status',
                                                        lambda: self.show_screen('status',
                                                                                 self.create_order_view_screen), icon="📋")
        self.buttons['profile'] = self.create_nav_button("Profile", 'profile',
                                                         lambda: self.show_screen('profile',
                                                                                  self.create_profile_screen), icon="👤")

        for btn in self.buttons.values():
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        logout_btn = QPushButton("Logout")
        logout_btn.setFixedSize(120, 30)
        logout_btn.setFont(QFont('Arial', 10))
        logout_btn.setStyleSheet(
            "background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 4px; color: #333333;")
        logout_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(logout_btn)

        self.main_h_layout.addWidget(sidebar, 0, Qt.AlignLeft)

    def refresh_active_view(self, keys):
        try:
            current_key = next((k for k, btn in self.buttons.items() if 'ffcdd2' in btn.styleSheet()), None)
            if current_key in keys:
                if current_key == 'status':
                    self.show_screen('status', self.create_order_view_screen)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh view: {str(e)}")

    def create_order_laundry_screen(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)

        layout.addWidget(self.create_title_bar("Order Laundry", "#81d4fa", "#01579b"))
        layout.addSpacing(15)

        welcome = QLabel(f"Welcome, {self.user_data['fullname']}!")
        welcome.setFont(QFont('Arial', 16, QFont.Bold))
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("color: #01579b;")
        layout.addWidget(welcome)

        form_container = QWidget()
        form_container.setStyleSheet("background-color: #ffffff; border: 1px solid #ccc; border-radius: 8px; padding: 20px;")
        form_layout = QGridLayout(form_container)
        form_layout.setSpacing(10)

        items_label = QLabel("Select Item:")
        items_label.setFont(QFont('Arial', 10))
        items_label.setFixedWidth(120)
        self.item_combo = QComboBox()
        self.item_combo.setFixedHeight(30)
        self.item_combo.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px; min-width: 200px;")
        self.item_combo.addItems(["Clothes (₱50/kg)", "Beddings (₱60/kg)", "Curtains (₱70/kg)", "Others (₱80/kg)"])
        form_layout.addWidget(items_label, 0, 0, Qt.AlignRight)
        form_layout.addWidget(self.item_combo, 0, 1)

        qty_label = QLabel("Quantity (kg):")
        qty_label.setFont(QFont('Arial', 10))
        qty_label.setFixedWidth(120)
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setFixedHeight(30)
        self.qty_spin.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px; min-width: 100px;")
        form_layout.addWidget(qty_label, 1, 0, Qt.AlignRight)
        form_layout.addWidget(self.qty_spin, 1, 1)

        add_btn = QPushButton("Add to Cart")
        add_btn.setFixedSize(120, 30)
        add_btn.setFont(QFont('Arial', 10))
        add_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; border-radius: 4px; border: none;")
        add_btn.clicked.connect(self.add_to_cart)
        form_layout.addWidget(add_btn, 2, 1, Qt.AlignRight)

        layout.addWidget(form_container)

        self.cart_table = QTableWidget()
        headers = ["Item", "Quantity (kg)", "Price/kg", "Remove"]
        self.cart_table.setColumnCount(len(headers))
        self.cart_table.setHorizontalHeaderLabels(headers)
        self.cart_table.setFont(QFont('Arial', 9))
        header = self.cart_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.cart_table)

        confirm_order_btn = QPushButton("Confirm Order")
        confirm_order_btn.setFixedSize(150, 35)
        confirm_order_btn.setFont(QFont('Arial', 12, QFont.Bold))
        confirm_order_btn.setStyleSheet(
            "background-color: #0288d1; color: white; border-radius: 4px; border: none;")
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(confirm_order_btn)
        btn_layout.addStretch()
        confirm_order_btn.clicked.connect(self.place_order)
        layout.addLayout(btn_layout)

        layout.addStretch()
        return container

    def add_to_cart(self):
        try:
            item_text = self.item_combo.currentText()
            item = item_text.split(' (')[0]
            price_per_kg = float(item_text.split('₱')[1].split('/')[0])
            qty = self.qty_spin.value()

            self.cart_items.append({
                'item': item,
                'quantity': qty,
                'price_per_kg': price_per_kg
            })

            self.cart_table.setRowCount(len(self.cart_items))
            row = len(self.cart_items) - 1
            self.cart_table.setItem(row, 0, QTableWidgetItem(item))
            self.cart_table.setItem(row, 1, QTableWidgetItem(str(qty)))
            self.cart_table.setItem(row, 2, QTableWidgetItem(f"₱{price_per_kg:.2f}"))
            remove_btn = QPushButton("Remove")
            remove_btn.setFixedSize(100, 25)
            remove_btn.setFont(QFont('Arial', 8))
            remove_btn.setStyleSheet(
                "background-color: #ef5350; color: white; border-radius: 4px; border: none;")
            remove_btn.clicked.connect(lambda: self.remove_from_cart(row))
            self.cart_table.setCellWidget(row, 3, remove_btn)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add to cart: {str(e)}")

    def remove_from_cart(self, row):
        try:
            self.cart_items.pop(row)
            self.cart_table.removeRow(row)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove item: {str(e)}")

    def place_order(self):
        try:
            if not self.cart_items:
                QMessageBox.warning(self, "Error", "Cart is empty. Add items to place an order.")
                return

            order_id = str(uuid.uuid4())[:8]
            order_data = {
                'Order ID': order_id,
                'User Email': self.user_data['email_address'],
                'Total': None,
                'Status': 'Pending Pick-up',
                'Order Date': datetime.datetime.now().strftime("%Y-%m-%d"),
                'items': [
                    {
                        'id': None,
                        'item': item['item'],
                        'price_per_kg': item['price_per_kg'],
                        'actual_kg': None,
                        'subtotal': None
                    } for item in self.cart_items
                ]
            }

            if self.dm.add_order(order_data):
                QMessageBox.information(self, "Success", "Order placed successfully.")
                self.cart_items = []
                self.cart_table.setRowCount(0)
            else:
                QMessageBox.critical(self, "Error", "Failed to place order.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Order placement failed: {str(e)}")

    def create_schedule_screen(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)

        layout.addWidget(self.create_title_bar("Schedule Service", "#81d4fa", "#01579b"))
        layout.addSpacing(15)

        form_container = QWidget()
        form_container.setStyleSheet("background-color: #ffffff; border: 1px solid #ccc; border-radius: 8px; padding: 20px;")
        form_layout = QGridLayout(form_container)
        form_layout.setSpacing(10)

        type_label = QLabel("Service Type:")
        type_label.setFont(QFont('Arial', 10))
        type_label.setFixedWidth(120)
        self.service_type_combo = QComboBox()
        self.service_type_combo.setFixedHeight(30)
        self.service_type_combo.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px; min-width: 200px;")
        self.service_type_combo.addItems(["Pickup", "Delivery"])
        self.service_type_combo.currentTextChanged.connect(self.toggle_address_fields)
        form_layout.addWidget(type_label, 0, 0, Qt.AlignRight)
        form_layout.addWidget(self.service_type_combo, 0, 1)

        date_label = QLabel("Date:")
        date_label.setFont(QFont('Arial', 10))
        date_label.setFixedWidth(120)
        self.date_input = QLineEdit()
        self.date_input.setFixedHeight(30)
        self.date_input.setReadOnly(True)
        self.date_input.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px; min-width: 200px;")
        self.date_input.setText(QDate.currentDate().toString("MM/dd/yyyy"))
        self.date_input.mousePressEvent = lambda event: self.show_calendar()
        form_layout.addWidget(date_label, 1, 0, Qt.AlignRight)
        form_layout.addWidget(self.date_input, 1, 1)

        time_label = QLabel("Time:")
        time_label.setFont(QFont('Arial', 10))
        time_label.setFixedWidth(120)
        self.hour_spin = QSpinBox()
        self.hour_spin.setRange(8, 17)  # 8 AM to 5 PM
        self.hour_spin.setFixedHeight(30)
        self.hour_spin.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px; min-width: 90px;")
        self.minute_spin = QSpinBox()
        self.minute_spin.setRange(0, 59)
        self.minute_spin.setFixedHeight(30)
        self.minute_spin.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px; min-width: 90px;")
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.hour_spin)
        time_layout.addWidget(self.minute_spin)
        form_layout.addWidget(time_label, 2, 0, Qt.AlignRight)
        form_layout.addLayout(time_layout, 2, 1)

        self.address_label = QLabel("Address:")
        self.address_label.setFont(QFont('Arial', 10))
        self.address_label.setFixedWidth(120)
        self.address_input = QLineEdit(self.user_data.get('home_address', ''))
        self.address_input.setFixedHeight(30)
        self.address_input.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px; min-width: 200px;")
        form_layout.addWidget(self.address_label, 3, 0, Qt.AlignRight)
        form_layout.addWidget(self.address_input, 3, 1)

        self.email_label = QLabel("Email:")
        self.email_label.setFont(QFont('Arial', 10))
        self.email_label.setFixedWidth(120)
        self.email_input = QLineEdit(self.user_data['email_address'])
        self.email_input.setFixedHeight(30)
        self.email_input.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px; min-width: 200px;")
        form_layout.addWidget(self.email_label, 4, 0, Qt.AlignRight)
        form_layout.addWidget(self.email_input, 4, 1)

        layout.addWidget(form_container)

        schedule_btn = QPushButton("Schedule")
        schedule_btn.setFixedSize(150, 35)
        schedule_btn.setFont(QFont('Arial', 12, QFont.Bold))
        schedule_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; border-radius: 4px; border: none;")
        schedule_btn.clicked.connect(self.schedule_service)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(schedule_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        self.toggle_address_fields(self.service_type_combo.currentText())
        layout.addStretch()
        return container

    def show_calendar(self):
        try:
            if not self.calendar_dialog:
                self.calendar_dialog = QDialog(self)
                self.calendar_dialog.setWindowTitle("Select Date")
                self.calendar_dialog.setModal(True)
                dialog_layout = QVBoxLayout(self.calendar_dialog)
                dialog_layout.addWidget(self.calendar_widget)
                select_btn = QPushButton("Select")
                select_btn.setFixedSize(120, 30)
                select_btn.setFont(QFont('Arial', 10))
                select_btn.setStyleSheet(
                    "background-color: #0288d1; color: white; border-radius: 4px; border: none;")
                select_btn.clicked.connect(self.calendar_dialog.accept)
                dialog_layout.addWidget(select_btn)
            self.calendar_dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show calendar: {str(e)}")

    def update_date_dropdown(self):
        try:
            selected_date = self.calendar_widget.selectedDate()
            self.date_input.setText(selected_date.toString("MM/dd/yyyy"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update date: {str(e)}")

    def toggle_address_fields(self, service_type):
        try:
            is_delivery = service_type == "Delivery"
            self.address_label.setVisible(is_delivery)
            self.address_input.setVisible(is_delivery)
            self.email_label.setVisible(is_delivery)
            self.email_input.setVisible(is_delivery)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to toggle fields: {str(e)}")

    def schedule_service(self):
        try:
            service_type = self.service_type_combo.currentText()
            date = self.date_input.text()
            time = f"{self.hour_spin.value():02d}:{self.minute_spin.value():02d}"
            address = self.address_input.text().strip() if self.address_input.isVisible() else ''
            email = self.email_input.text().strip() if self.email_input.isVisible() else ''

            if not all([service_type, date, time]) or (service_type == "Delivery" and not all([address, email])):
                QMessageBox.warning(self, "Error", "All fields are required.")
                return

            if service_type == "Delivery" and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                QMessageBox.warning(self, "Error", "Invalid email format.")
                return

            schedule_data = {
                'ID': None,
                'User Email': self.user_data['email_address'],
                'Type': service_type,
                'Date': date,
                'Time': time,
                'Address': address,
                'Email': email,
                'Status': 'Scheduled'
            }

            if self.dm.add_schedule(schedule_data):
                QMessageBox.information(self, "Success", "Schedule created successfully.")
                self.address_input.setText(self.user_data.get('home_address', '')) if self.address_input.isVisible() else None
                self.email_input.setText(self.user_data['email_address']) if self.email_input.isVisible() else None
            else:
                QMessageBox.critical(self, "Error", "Failed to create schedule.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Schedule creation failed: {str(e)}")

    def create_order_view_screen(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)

        layout.addWidget(self.create_title_bar("Order Status", "#81d4fa", "#01579b"))
        layout.addSpacing(15)

        order_table = QTableWidget()
        headers = ["Order ID", "Items", "Total", "Status", "Order Date"]
        order_table.setColumnCount(len(headers))
        order_table.setHorizontalHeaderLabels(headers)
        order_table.setFont(QFont('Arial', 9))
        header = order_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        try:
            user_orders = [o for o in self.dm.orders if o['User Email'] == self.user_data['email_address']]
            order_table.setRowCount(len(user_orders))
            for row, order in enumerate(user_orders):
                item = QTableWidgetItem(order['Order ID'])
                item.setFont(QFont('Arial', 9))
                item.setFlags(Qt.ItemIsEnabled)  # View-only
                order_table.setItem(row, 0, item)
                items_str = ", ".join([i['item'] for i in order['items']])
                item = QTableWidgetItem(items_str)
                item.setFont(QFont('Arial', 9))
                item.setFlags(Qt.ItemIsEnabled)  # View-only
                order_table.setItem(row, 1, item)
                item = QTableWidgetItem(f"₱{order['Total']:.2f}" if order['Total'] is not None else '-')
                item.setFont(QFont('Arial', 9))
                item.setFlags(Qt.ItemIsEnabled)  # View-only
                order_table.setItem(row, 2, item)
                item = QTableWidgetItem(order['Status'])
                item.setFont(QFont('Arial', 9))
                item.setFlags(Qt.ItemIsEnabled)  # View-only
                self.set_status_color(item, order['Status'])
                order_table.setItem(row, 3, item)
                item = QTableWidgetItem(order['Order Date'])
                item.setFont(QFont('Arial', 9))
                item.setFlags(Qt.ItemIsEnabled)  # View-only
                order_table.setItem(row, 4, item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to populate orders: {str(e)}")

        layout.addWidget(order_table)
        layout.addStretch()
        return container

    def set_status_color(self, item, status):
        colors = {
            "Pending Pick-up": QColor(255, 255, 0),
            "Washing": QColor(0, 0, 255),
            "Drying": QColor(255, 165, 0),
            "Completed": QColor(0, 128, 0),
            "Ready for Pickup": QColor(0, 255, 0),
            "Ready for Delivery": QColor(0, 255, 255),
            "Cancelled": QColor(255, 0, 0)
        }
        item.setBackground(colors.get(status, QColor(255, 255, 255)))

    def create_profile_screen(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(15)

        layout.addWidget(self.create_title_bar("Your Profile", "#81d4fa", "#01579b"))
        layout.addSpacing(15)

        form_container = QWidget()
        form_container.setStyleSheet("background-color: #ffffff; border: 1px solid #ccc; border-radius: 8px; padding: 20px;")
        form_layout = QGridLayout(form_container)
        form_layout.setSpacing(10)

        fields = [
            ('Fullname', self.user_data.get('fullname', '')),
            ('Email', self.user_data.get('email_address', '')),
            ('Contact Info', self.user_data.get('contact_info', '')),
            ('Home Address', self.user_data.get('home_address', ''))
        ]

        self.profile_fields = {}
        for row, (label_text, value) in enumerate(fields):
            label = QLabel(label_text + ":")
            label.setFont(QFont('Arial', 10))
            label.setFixedWidth(120)
            input_widget = QLineEdit(value)
            input_widget.setFixedHeight(30)
            input_widget.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px; min-width: 250px;")
            input_widget.setReadOnly(True)
            form_layout.addWidget(label, row, 0, Qt.AlignRight)
            form_layout.addWidget(input_widget, row, 1)
            self.profile_fields[label_text] = input_widget

        layout.addWidget(form_container)
        layout.addStretch()
        return container