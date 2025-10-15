from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QGridLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QDialog, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QColor
from ui_helpers import BaseDashboard


class StaffDashboard(BaseDashboard):
    def __init__(self, data_manager, parent_app=None):
        super().__init__("Staff Dashboard", parent_app)
        self.dm = data_manager
        self.order_table = None
        self.init_sidebar()
        self.dm.order_updated.connect(lambda: self.refresh_active_view(['view_orders', 'manage_pickup', 'report']))
        self.show_screen('view_orders', self.create_view_orders_screen)

    def init_sidebar(self):
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: #fafafa; border-right: 1px solid #ddd;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(10, 15, 10, 15)
        sidebar_layout.setSpacing(8)

        logo_label = QLabel("🧺 WashDesk\nOrder & Logistics Management")
        logo_label.setFont(QFont('Arial', 10, QFont.Bold))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("color: #33691e; padding: 10px;")
        sidebar_layout.addWidget(logo_label, alignment=Qt.AlignTop)
        sidebar_layout.addSpacing(15)

        self.buttons['view_orders'] = self.create_nav_button("View Orders", 'view_orders',
                                                             lambda: self.show_screen('view_orders',
                                                                                      self.create_view_orders_screen), icon="📦")
        self.buttons['manage_pickup'] = self.create_nav_button("Pickup/Delivery", 'manage_pickup',
                                                               lambda: self.show_screen('manage_pickup',
                                                                                        self.create_manage_pickup_screen), icon="🚚")
        self.buttons['report'] = self.create_nav_button("Daily Report", 'report',
                                                        lambda: self.show_screen('report',
                                                                                 self.create_daily_report_screen), icon="📊")

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
                if current_key == 'view_orders':
                    self.show_screen('view_orders', self.create_view_orders_screen)
                elif current_key == 'manage_pickup':
                    self.show_screen('manage_pickup', self.create_manage_pickup_screen)
                elif current_key == 'report':
                    self.show_screen('report', self.create_daily_report_screen)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh view: {str(e)}")

    def create_view_orders_screen(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(self.create_title_bar("All Laundry Orders", "#b2ff59", "#33691e"))
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

    def create_daily_report_screen(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(self.create_title_bar("Today's Summary", "#b2ff59", "#33691e"))
        layout.addSpacing(30)

        try:
            today = QDate.currentDate().toString("yyyy-MM-dd")
            orders_today = [o for o in self.dm.orders if o['Order Date'] == today]
            revenue_today = sum(o['Total'] for o in orders_today if o['Total'] is not None)
            schedules_today = [s for s in self.dm.schedules if s['Date'] == QDate.currentDate().toString("MM/dd/yyyy")]

            report_data = {
                "Orders Today:": len(orders_today),
                "Revenue Today:": f"₱{revenue_today:.2f}",
                "Schedules Today:": len(schedules_today)
            }

            form_layout = QGridLayout()
            form_layout.setVerticalSpacing(20)

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
            QMessageBox.critical(self, "Error", f"Failed to load report: {str(e)}")

        return container

    def create_manage_pickup_screen(self):
        container = QWidget()
        layout = QVBoxLayout(container)

        layout.addWidget(self.create_title_bar("Scheduled Pickup/Delivery", "#b2ff59", "#33691e"))
        layout.addSpacing(15)

        welcome = QLabel("Scheduled Pickup/Delivery")
        welcome.setFont(QFont('Arial', 16, QFont.Bold))
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("color: #33691e;")
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