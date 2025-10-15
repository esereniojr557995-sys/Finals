from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGridLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QDialog, QDoubleSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from ui_helpers import BaseDashboard, RegistrationDialog


class AdminDashboard(BaseDashboard):
    def __init__(self, data_manager, parent_app=None):
        super().__init__("Admin Dashboard", parent_app)
        self.dm = data_manager
        self.user_table = None
        self.order_table = None
        self.init_sidebar()
        self.dm.user_data_changed.connect(lambda: self.refresh_active_view(['manage_users']))
        self.dm.order_updated.connect(lambda: self.refresh_active_view(['view_orders', 'system_reports']))
        self.show_screen('manage_users', self.create_manage_users_screen)

    def init_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #fafafa; border-right: 1px solid #ddd;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_layout.setSpacing(8)

        logo_label = QLabel("🧺 WashDesk\nSystem Administration")
        logo_label.setFont(QFont('Arial', 10, QFont.Bold))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("color: #880e4f; padding: 10px;")
        sidebar_layout.addWidget(logo_label, alignment=Qt.AlignTop)
        sidebar_layout.addSpacing(15)

        self.buttons['manage_users'] = self.create_nav_button("Manage Users", 'manage_users',
                                                              lambda: self.show_screen('manage_users',
                                                                                       self.create_manage_users_screen), icon="👥")
        self.buttons['view_orders'] = self.create_nav_button("View Orders", 'view_orders',
                                                             lambda: self.show_screen('view_orders',
                                                                                      self.create_view_orders_screen), icon="📦")
        self.buttons['manage_pickup'] = self.create_nav_button("Pickup/Delivery", 'manage_pickup',
                                                               lambda: self.show_screen('manage_pickup',
                                                                                        self.create_manage_pickup_screen), icon="🚚")
        self.buttons['system_reports'] = self.create_nav_button("System Reports", 'system_reports',
                                                                lambda: self.show_screen('system_reports',
                                                                                         self.create_system_reports_screen), icon="📈")

        for btn in self.buttons.values():
            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        logout_btn = QPushButton("Logout")
        logout_btn.setFixedSize(120, 30)
        logout_btn.setStyleSheet(
            "background-color: #f0f0f0; border: 1px solid #ccc; border-radius: 4px; color: #333333;")
        logout_btn.clicked.connect(self.close)
        sidebar_layout.addWidget(logout_btn)

        self.main_h_layout.addWidget(sidebar)

    def refresh_active_view(self, keys):
        try:
            current_key = next((k for k, btn in self.buttons.items() if 'ffcdd2' in btn.styleSheet()), None)
            if current_key in keys:
                if current_key == 'manage_users':
                    self.populate_user_table()
                elif current_key == 'view_orders':
                    self.show_screen('view_orders', self.create_view_orders_screen)
                elif current_key == 'manage_pickup':
                    self.show_screen('manage_pickup', self.create_manage_pickup_screen)
                elif current_key == 'system_reports':
                    self.show_screen('system_reports', self.create_system_reports_screen)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh view: {str(e)}")

    def create_manage_users_screen(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(self.create_title_bar("Manage Users", "#ffcdd2", "#880e4f"))
        layout.addSpacing(15)

        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        search_label.setFont(QFont('Arial', 10))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name or email")
        self.search_input.setFixedHeight(30)
        self.search_input.setStyleSheet("border: 1px solid #ccc; border-radius: 4px; padding: 5px;")
        self.search_input.textChanged.connect(self.filter_user_table)
        add_btn = QPushButton("Add User")
        add_btn.setFixedSize(120, 30)
        add_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; border-radius: 4px; border: none;")
        add_btn.clicked.connect(self.add_user)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(add_btn)
        layout.addLayout(search_layout)

        self.user_table = QTableWidget()
        headers = ["Name", "Contact", "Role", "Email", "Address", "Actions"]
        self.user_table.setColumnCount(len(headers))
        self.user_table.setHorizontalHeaderLabels(headers)
        self.user_table.setFont(QFont('Arial', 9))
        header = self.user_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.populate_user_table()
        layout.addWidget(self.user_table)
        layout.addStretch()
        return container

    def populate_user_table(self):
        try:
            self.user_table.setRowCount(0)
            users = self.dm.get_all_users_flat()
            self.user_table.setRowCount(len(users))
            for row, user in enumerate(users):
                name_item = QTableWidgetItem(user['name'])
                name_item.setData(Qt.UserRole, user['id'])
                name_item.setFont(QFont('Arial', 9))
                name_item.setFlags(Qt.NoItemFlags)
                self.user_table.setItem(row, 0, name_item)
                item = QTableWidgetItem(user['contact'])
                item.setFont(QFont('Arial', 9))
                item.setFlags(Qt.NoItemFlags)
                self.user_table.setItem(row, 1, item)
                item = QTableWidgetItem(user['role'])
                item.setFont(QFont('Arial', 9))
                item.setFlags(Qt.NoItemFlags)
                self.user_table.setItem(row, 2, item)
                item = QTableWidgetItem(user['email'])
                item.setFont(QFont('Arial', 9))
                item.setFlags(Qt.NoItemFlags)
                self.user_table.setItem(row, 3, item)
                item = QTableWidgetItem(user['address'])
                item.setFont(QFont('Arial', 9))
                item.setFlags(Qt.NoItemFlags)
                self.user_table.setItem(row, 4, item)
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                delete_btn = QPushButton("Delete")
                delete_btn.setFont(QFont('Arial', 8))
                delete_btn.setFixedSize(100, 25)
                delete_btn.setStyleSheet(
                    "background-color: #ef5350; color: white; border-radius: 4px; border: none;")
                delete_btn.clicked.connect(lambda checked, r=row: self.delete_user_account(r))
                action_layout.addWidget(delete_btn)
                self.user_table.setCellWidget(row, 5, action_widget)

            self.filter_user_table(self.search_input.text())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to populate user table: {str(e)}")

    def filter_user_table(self, text):
        try:
            text = text.lower()
            for row in range(self.user_table.rowCount()):
                name = self.user_table.item(row, 0).text().lower()
                email = self.user_table.item(row, 3).text().lower()
                self.user_table.setRowHidden(row, text not in name and text not in email)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to filter users: {str(e)}")

    def add_user(self):
        try:
            reg_dialog = RegistrationDialog(self.dm, self)
            reg_dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open add user dialog: {str(e)}")

    def delete_user_account(self, row):
        try:
            user_id = self.user_table.item(row, 0).data(Qt.UserRole)
            if user_id == 301:
                QMessageBox.critical(self, "Error", "Cannot delete the primary Admin account.")
                return

            reply = QMessageBox.question(self, 'Confirm Deletion',
                                         "Are you sure you want to delete this user?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                if self.dm.delete_user(user_id):
                    QMessageBox.information(self, "Success", "User successfully deleted.")
                    self.populate_user_table()
                else:
                    QMessageBox.critical(self, "Error", "User not found.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")

    def create_system_reports_screen(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(self.create_title_bar("System Reports", "#ffcdd2", "#880e4f"))
        layout.addSpacing(15)

        try:
            num_customers = len(self.dm.user_data['Customer'])
            num_staffs = len(self.dm.user_data['Staff'])
            num_admins = len(self.dm.user_data['Admin'])
            total_orders = len(self.dm.orders)
            total_revenue = sum(o['Total'] for o in self.dm.orders if o['Total'] is not None)
            open_schedules = len(
                [s for s in self.dm.schedules if s['Status'] != 'Completed' and s['Status'] != 'Cancelled'])

            report_data = {
                "No. of Customers:": num_customers,
                "No. of Staff:": num_staffs,
                "No. of Admins:": num_admins,
                "Total Orders:": total_orders,
                "Total Revenue:": f"₱{total_revenue:.2f}",
                "Open Schedules:": open_schedules
            }

            form_layout = QGridLayout()
            form_layout.setVerticalSpacing(15)

            for row, (label_text, value) in enumerate(report_data.items()):
                label = QLabel(label_text)
                label.setFont(QFont('Arial', 12))
                label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

                value_display = QLineEdit(str(value))
                value_display.setFont(QFont('Arial', 12))
                value_display.setFixedHeight(30)
                value_display.setReadOnly(True)
                value_display.setStyleSheet("background-color: #e0e0e0; border: 1px solid #ccc; border-radius: 4px;")

                form_layout.addWidget(label, row, 0)
                form_layout.addWidget(value_display, row, 1)

            layout.addLayout(form_layout)
            layout.addStretch()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load reports: {str(e)}")

        return container

    def create_view_orders_screen(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(self.create_title_bar("All Laundry Orders", "#ffcdd2", "#880e4f"))
        layout.addSpacing(15)

        self.order_table = QTableWidget()
        headers = ["Order ID", "User Email", "Items", "Total", "Status", "Actions"]
        self.order_table.setColumnCount(len(headers))
        self.order_table.setHorizontalHeaderLabels(headers)
        self.order_table.setFont(QFont('Arial', 9))
        header = self.order_table.horizontalHeader()
        for i in range(len(headers) - 1):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        header.setSectionResizeMode(len(headers) - 1, QHeaderView.ResizeToContents)
        self.populate_order_table(self.order_table)
        layout.addWidget(self.order_table)
        layout.addStretch()
        return container

    def populate_order_table(self, order_table):
        try:
            order_table.setRowCount(0)
            if not self.dm.orders:
                return
            order_table.setRowCount(len(self.dm.orders))
            for row, order in enumerate(self.dm.orders):
                item = QTableWidgetItem(order['Order ID'])
                item.setFont(QFont('Arial', 9))
                item.setFlags(Qt.NoItemFlags)
                order_table.setItem(row, 0, item)
                item = QTableWidgetItem(order['User Email'])
                item.setFont(QFont('Arial', 9))
                item.setFlags(Qt.NoItemFlags)
                order_table.setItem(row, 1, item)
                items_str = ", ".join([i['item'] for i in order['items']])
                item = QTableWidgetItem(items_str)
                item.setFont(QFont('Arial', 9))
                item.setFlags(Qt.NoItemFlags)
                order_table.setItem(row, 2, item)
                item = QTableWidgetItem(f"₱{order['Total']:.2f}" if order['Total'] is not None else '-')
                item.setFont(QFont('Arial', 9))
                item.setFlags(Qt.NoItemFlags)
                order_table.setItem(row, 3, item)
                status_combo = QComboBox()
                status_combo.setFont(QFont('Arial', 9))
                status_combo.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
                status_combo.addItems([
                    "Pending Pick-up", "Washing", "Drying", "Completed",
                    "Ready for Pickup", "Ready for Delivery", "Cancelled"
                ])
                current_status = order['Status']
                index = status_combo.findText(current_status)
                if index >= 0:
                    status_combo.setCurrentIndex(index)
                status_combo.currentTextChanged.connect(lambda text, r=row: self.on_status_changed(r, text))
                order_table.setCellWidget(row, 4, status_combo)
                action_widget = QWidget()
                action_layout = QHBoxLayout(action_widget)
                action_layout.setContentsMargins(2, 2, 2, 2)
                action_layout.setSpacing(5)
                edit_btn = QPushButton("Edit Billing")
                edit_btn.setFont(QFont('Arial', 8))
                edit_btn.setFixedSize(100, 25)
                edit_btn.setStyleSheet(
                    "background-color: #81d4fa; color: #01579b; border-radius: 4px; border: none;")
                edit_btn.clicked.connect(lambda checked=False, r=row: self.open_billing_dialog(r))
                action_layout.addWidget(edit_btn)
                order_table.setCellWidget(row, 5, action_widget)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to populate orders: {str(e)}")

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

    def on_status_changed(self, row, new_status):
        try:
            order = self.dm.orders[row]
            order_id = order['Order ID']
            if self.dm.update_order(order_id, {'Status': new_status}):
                self.update_order_row(row)
            else:
                QMessageBox.critical(self, "Error", "Failed to update status")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Status update failed: {str(e)}")

    def update_order_row(self, row):
        try:
            if not self.order_table or row >= len(self.dm.orders):
                return
            order = self.dm.orders[row]
            total_item = QTableWidgetItem(f"₱{order['Total']:.2f}" if order['Total'] is not None else '-')
            total_item.setFont(QFont('Arial', 9))
            total_item.setFlags(Qt.NoItemFlags)
            self.order_table.setItem(row, 3, total_item)
            status_combo = self.order_table.cellWidget(row, 4)
            status_combo.blockSignals(True)
            index = status_combo.findText(order['Status'])
            if index >= 0:
                status_combo.setCurrentIndex(index)
            status_combo.blockSignals(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update order row: {str(e)}")

    def open_billing_dialog(self, row):
        try:
            order = self.dm.orders[row]
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Edit Billing for Order {order['Order ID']}")
            dialog.setModal(True)
            layout = QVBoxLayout(dialog)

            item_table = QTableWidget()
            headers = ["Item", "Price/kg", "Actual Kg", "Subtotal"]
            item_table.setColumnCount(len(headers))
            item_table.setHorizontalHeaderLabels(headers)
            item_table.setFont(QFont('Arial', 9))
            header = item_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)
            item_table.setRowCount(len(order['items']))
            for i, item in enumerate(order['items']):
                item_table.setItem(i, 0, QTableWidgetItem(item['item']))
                item_table.setItem(i, 1, QTableWidgetItem(f"₱{item['price_per_kg']:.2f}"))
                actual_kg_spin = QDoubleSpinBox()
                actual_kg_spin.setDecimals(2)
                actual_kg_spin.setMinimum(0.0)
                actual_kg_spin.setValue(item['actual_kg'] or 0.0)
                actual_kg_spin.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
                actual_kg_spin.valueChanged.connect(lambda val, idx=i: self.calculate_subtotal(idx, val, item_table, order['items'][idx]))
                item_table.setCellWidget(i, 2, actual_kg_spin)
                subtotal_item = QTableWidgetItem(f"₱{item['subtotal']:.2f}" if item['subtotal'] else '-')
                item_table.setItem(i, 3, subtotal_item)

            layout.addWidget(item_table)

            save_btn = QPushButton("Save")
            save_btn.setFixedSize(120, 30)
            save_btn.setStyleSheet(
                "background-color: #4CAF50; color: white; border-radius: 4px; border: none;")
            save_btn.clicked.connect(lambda: self.save_billing_dialog(row, item_table, dialog))
            layout.addWidget(save_btn)

            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open billing dialog: {str(e)}")

    def calculate_subtotal(self, idx, val, table, item):
        try:
            subtotal = val * item['price_per_kg']
            subtotal_item = QTableWidgetItem(f"₱{subtotal:.2f}")
            table.setItem(idx, 3, subtotal_item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to calculate subtotal: {str(e)}")

    def save_billing_dialog(self, row, table, dialog):
        try:
            order = self.dm.orders[row]
            total = 0.0
            for i in range(table.rowCount()):
                item = order['items'][i]
                actual_kg_widget = table.cellWidget(i, 2)
                actual_kg = actual_kg_widget.value()
                subtotal = actual_kg * item['price_per_kg']
                self.dm.update_order_item(item['id'], actual_kg, subtotal)
                item['actual_kg'] = actual_kg
                item['subtotal'] = subtotal
                total += subtotal
            self.dm.update_order(order['Order ID'], {'Total': total})
            order['Total'] = total
            self.update_order_row(row)
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save billing: {str(e)}")

    def create_manage_pickup_screen(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(self.create_title_bar("Scheduled Pickup/Delivery", "#ffcdd2", "#880e4f"))
        layout.addSpacing(15)

        welcome = QLabel("Scheduled Pickup/Delivery")
        welcome.setFont(QFont('Arial', 16, QFont.Bold))
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("color: #880e4f;")
        layout.addWidget(welcome)
        layout.addSpacing(15)

        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by Status:")
        filter_label.setFont(QFont('Arial', 10))
        pickup_filter_combo = QComboBox()
        pickup_filter_combo.setFixedHeight(30)
        pickup_filter_combo.setStyleSheet("border: 1px solid #ccc; border-radius: 4px;")
        pickup_filter_combo.addItems(["All", "Scheduled", "In Progress", "Completed", "Cancelled"])
        pickup_filter_combo.currentIndexChanged.connect(
            lambda: self.populate_pickup_table(pickup_table, pickup_filter_combo))

        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(pickup_filter_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        pickup_table = QTableWidget()
        headers = ["ID", "User Email", "Type", "Date", "Time", "Address", "Email", "Status"]
        pickup_table.setColumnCount(len(headers))
        pickup_table.setHorizontalHeaderLabels(headers)
        pickup_table.setFont(QFont('Arial', 9))
        header = pickup_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        self.populate_pickup_table(pickup_table, pickup_filter_combo)
        layout.addWidget(pickup_table)
        layout.addStretch()

        return container

    def populate_pickup_table(self, pickup_table, pickup_filter_combo):
        try:
            selected_filter = pickup_filter_combo.currentText()
            filtered_schedules = [
                s for s in self.dm.schedules
                if selected_filter == "All" or s['Status'] == selected_filter
            ]
            pickup_table.setRowCount(len(filtered_schedules))
            for row, schedule in enumerate(filtered_schedules):
                items = [
                    str(schedule['ID']),
                    schedule['User Email'],
                    schedule['Type'],
                    schedule['Date'],
                    schedule['Time'],
                    schedule['Address'],
                    schedule['Email'],
                    schedule['Status']
                ]
                for col, item_text in enumerate(items):
                    item = QTableWidgetItem(item_text)
                    item.setFont(QFont('Arial', 9))
                    item.setFlags(Qt.NoItemFlags)
                    pickup_table.setItem(row, col, item)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to populate pickup table: {str(e)}")