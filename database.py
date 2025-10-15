from PyQt5.QtCore import QObject, pyqtSignal, QDate
import hashlib
import warnings
import pymysql

warnings.filterwarnings("ignore", category=DeprecationWarning)


class DataManager(QObject):
    order_updated = pyqtSignal()
    user_data_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.last_user_id = 301
        self.db = None
        self.cursor = None
        self.user_data = {'Admin': {}, 'Staff': {}, 'Customer': {}}
        self.orders = []
        self.schedules = []

        try:
            self.connect_to_database()
            print("✓ Database connection established")
        except Exception as e:
            print(f"✗ Database connection failed: {str(e)}. Running in offline mode.")
            self.load_mock_data()

    def connect_to_database(self):
        try:
            self.db = pymysql.connect(
                host="localhost",
                user="root",
                password="",
                database="washdesk_db",
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.db.cursor()
            self.create_tables()
            self.load_data_from_db()
        except pymysql.Error as err:
            print(f"✗ Database connection error: {err}")
            raise
        except Exception as e:
            print(f"✗ Unexpected connection error: {e}")
            raise

    def load_mock_data(self):
        self.user_data['Admin']['admina@mail.com'] = {
            'id': 301,
            'fullname': 'Admin A',
            'password': self.hash_password('123'),
            'contact_info': '0900-000',
            'email_address': 'admina@mail.com',
            'home_address': 'HQ'
        }
        self.user_data['Staff']['staff@mail.com'] = {
            'id': 201,
            'fullname': 'Staff 1',
            'password': self.hash_password('123'),
            'contact_info': '0911-111',
            'email_address': 'staff@mail.com',
            'home_address': 'Warehouse'
        }
        self.user_data['Customer']['john.doe@example.com'] = {
            'id': 101,
            'fullname': 'John Doe',
            'password': self.hash_password('123'),
            'contact_info': '0912-222',
            'email_address': 'john.doe@example.com',
            'home_address': '123 Main St, Anytown'
        }
        print("✓ Mock data loaded (offline mode)")

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_tables(self):
        if not self.cursor:
            print("✗ No database cursor available")
            return

        try:
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT PRIMARY KEY,
                    fullname VARCHAR(255),
                    password VARCHAR(255),
                    contact_info VARCHAR(255),
                    email_address VARCHAR(255) UNIQUE,
                    home_address TEXT,
                    role ENUM('Admin', 'Staff', 'Customer')
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    order_id VARCHAR(50) PRIMARY KEY,
                    user_email VARCHAR(255),
                    total DECIMAL(10, 2),
                    status VARCHAR(50),
                    order_date DATE
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS order_items (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    order_id VARCHAR(50),
                    item VARCHAR(255),
                    price_per_kg DECIMAL(10, 2),
                    actual_kg DECIMAL(10, 2),
                    subtotal DECIMAL(10, 2)
                )
            """)
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS schedules (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    user_email VARCHAR(255),
                    type VARCHAR(50),
                    date VARCHAR(50),
                    time VARCHAR(50),
                    address TEXT,
                    email VARCHAR(255),
                    status VARCHAR(50)
                )
            """)
            self.db.commit()

            self.cursor.execute("SELECT * FROM users WHERE email_address = 'admina@mail.com'")
            if not self.cursor.fetchone():
                self.cursor.execute("""
                    INSERT INTO users (id, fullname, password, contact_info, email_address, home_address, role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (301, 'Admin A', self.hash_password('123'), '0900-000', 'admina@mail.com', 'HQ', 'Admin'))
                self.db.commit()
                print("✓ Default admin account created")
        except pymysql.Error as err:
            print(f"✗ Error creating tables: {err}")
            self.db.rollback()

    def load_data_from_db(self):
        if not self.cursor:
            print("✗ No database cursor available")
            return

        try:
            self.cursor.execute("SELECT * FROM users")
            users = self.cursor.fetchall()
            for user in users:
                role = user['role']
                email = user['email_address']
                self.user_data[role][email] = {
                    'id': user['id'],
                    'fullname': user['fullname'],
                    'password': user['password'],
                    'contact_info': user['contact_info'],
                    'email_address': email,
                    'home_address': user['home_address']
                }
                if user['id'] > self.last_user_id:
                    self.last_user_id = user['id']

            self.cursor.execute("SELECT * FROM orders")
            orders = self.cursor.fetchall()
            for order in orders:
                order_dict = {
                    'Order ID': order['order_id'],
                    'User Email': order['user_email'],
                    'Total': float(order['total']) if order['total'] else None,
                    'Status': order['status'],
                    'Order Date': str(order['order_date'])
                }
                self.cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order['order_id'],))
                items = self.cursor.fetchall()
                order_dict['items'] = [
                    {
                        'id': item['id'],
                        'item': item['item'],
                        'price_per_kg': float(item['price_per_kg']),
                        'actual_kg': float(item['actual_kg']) if item['actual_kg'] else None,
                        'subtotal': float(item['subtotal']) if item['subtotal'] else None
                    } for item in items
                ]
                self.orders.append(order_dict)

            self.cursor.execute("SELECT * FROM schedules")
            schedules = self.cursor.fetchall()
            for schedule in schedules:
                self.schedules.append({
                    'ID': schedule['id'],
                    'User Email': schedule['user_email'],
                    'Type': schedule['type'],
                    'Date': schedule['date'],
                    'Time': schedule['time'],
                    'Address': schedule['address'],
                    'Email': schedule['email'],
                    'Status': schedule['status']
                })

            print(f"✓ Loaded {len(users)} users, {len(orders)} orders, {len(schedules)} schedules")
        except pymysql.Error as err:
            print(f"✗ Error loading data: {err}")
            self.db.rollback()

    def get_next_user_id(self):
        self.last_user_id += 1
        return self.last_user_id

    def register_user(self, role, data):
        try:
            email = data['email']
            for r in self.user_data:
                if email in self.user_data[r]:
                    print(f"✗ Registration failed: Email '{email}' already exists")
                    return False

            user_id = self.get_next_user_id()
            hashed_password = self.hash_password(data['password'])
            home_address = data.get('home_address', '')

            if self.cursor:
                self.cursor.execute("""
                    INSERT INTO users (id, fullname, password, contact_info, email_address, home_address, role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (user_id, data['fullname'], hashed_password,
                      data['contact_info'], email, home_address, role))
                self.db.commit()
                print(f"✓ User registered: {email}, ID: {user_id}")

            data['id'] = user_id
            data['password'] = hashed_password
            data['email_address'] = email
            self.user_data[role][email] = data
            self.user_data_changed.emit()
            return True
        except pymysql.Error as err:
            print(f"✗ Database error during registration: {err}")
            if self.db:
                self.db.rollback()
            return False
        except Exception as e:
            print(f"✗ Unexpected error during registration: {e}")
            return False

    def get_user(self, email):
        try:
            for role in ['Admin', 'Staff', 'Customer']:
                if email in self.user_data[role]:
                    return role, self.user_data[role][email]
            return None, None
        except Exception as e:
            print(f"✗ Error retrieving user: {e}")
            return None, None

    def verify_password(self, plain_password, hashed_password):
        try:
            return self.hash_password(plain_password) == hashed_password
        except Exception as e:
            print(f"✗ Error verifying password: {e}")
            return False

    def get_all_users_flat(self):
        try:
            users = []
            for role, user_map in self.user_data.items():
                for email, data in user_map.items():
                    users.append({
                        'id': data['id'],
                        'name': data['fullname'],
                        'contact': data['contact_info'],
                        'role': role,
                        'email': data.get('email_address', 'N/A'),
                        'address': data.get('home_address', 'N/A')
                    })
            return users
        except Exception as e:
            print(f"✗ Error retrieving users: {e}")
            return []

    def delete_user(self, user_id):
        try:
            user_id = int(user_id)
            for role, user_map in self.user_data.items():
                for email, data in list(user_map.items()):
                    if data['id'] == user_id:
                        if self.cursor:
                            self.cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                            self.db.commit()
                        del user_map[email]
                        self.user_data_changed.emit()
                        print(f"✓ User deleted: ID {user_id}")
                        return True
            print(f"✗ User not found: ID {user_id}")
            return False
        except pymysql.Error as err:
            print(f"✗ Error deleting user: {err}")
            if self.db:
                self.db.rollback()
            return False
        except Exception as e:
            print(f"✗ Unexpected error deleting user: {e}")
            return False

    def add_order(self, order_data):
        try:
            order_id = order_data['Order ID']
            if self.cursor:
                self.cursor.execute("""
                    INSERT INTO orders (order_id, user_email, total, status, order_date)
                    VALUES (%s, %s, %s, %s, %s)
                """, (order_id, order_data['User Email'], None, order_data['Status'], order_data['Order Date']))
                for item in order_data['items']:
                    self.cursor.execute("""
                        INSERT INTO order_items (order_id, item, price_per_kg, actual_kg, subtotal)
                        VALUES (%s, %s, %s, NULL, NULL)
                    """, (order_id, item['item'], item['price_per_kg']))
                self.db.commit()
            self.orders.append(order_data)
            self.order_updated.emit()
            print(f"✓ Order added: {order_id}")
            return True
        except pymysql.Error as err:
            print(f"✗ Error adding order: {err}")
            if self.db:
                self.db.rollback()
            return False
        except Exception as e:
            print(f"✗ Unexpected error adding order: {e}")
            return False

    def update_order(self, order_id, updates):
        try:
            order = next((o for o in self.orders if o['Order ID'] == order_id), None)
            if not order:
                print(f"✗ Order not found: {order_id}")
                return False

            if self.cursor:
                set_parts = []
                values = []
                if 'Status' in updates:
                    set_parts.append("status = %s")
                    values.append(updates['Status'])
                if 'Total' in updates:
                    set_parts.append("total = %s")
                    values.append(updates['Total'])
                if set_parts:
                    values.append(order_id)
                    set_clause = ", ".join(set_parts)
                    self.cursor.execute(f"UPDATE orders SET {set_clause} WHERE order_id = %s", values)
                    self.db.commit()

            order.update(updates)
            self.order_updated.emit()
            print(f"✓ Order updated: {order_id}")
            return True
        except pymysql.Error as err:
            print(f"✗ Error updating order: {err}")
            if self.db:
                self.db.rollback()
            return False
        except Exception as e:
            print(f"✗ Unexpected error updating order: {e}")
            return False

    def update_order_item(self, item_id, actual_kg, subtotal):
        try:
            if self.cursor:
                self.cursor.execute("""
                    UPDATE order_items SET actual_kg = %s, subtotal = %s WHERE id = %s
                """, (actual_kg, subtotal, item_id))
                self.db.commit()
                print(f"✓ Order item updated: ID {item_id}")
        except pymysql.Error as err:
            print(f"✗ Error updating order item: {err}")
            if self.db:
                self.db.rollback()
        except Exception as e:
            print(f"✗ Unexpected error updating order item: {e}")

    def add_schedule(self, schedule_data):
        try:
            if self.cursor:
                self.cursor.execute("""
                    INSERT INTO schedules (user_email, type, date, time, address, email, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (schedule_data['User Email'], schedule_data['Type'], schedule_data['Date'],
                      schedule_data['Time'], schedule_data['Address'], schedule_data['Email'],
                      schedule_data['Status']))
                self.db.commit()
                schedule_data['ID'] = self.cursor.lastrowid
                print(f"✓ Schedule added: ID {schedule_data['ID']}")
            else:
                schedule_data['ID'] = len(self.schedules) + 1
            self.schedules.append(schedule_data)
            return True
        except pymysql.Error as err:
            print(f"✗ Error adding schedule: {err}")
            if self.db:
                self.db.rollback()
            return False
        except Exception as e:
            print(f"✗ Unexpected error adding schedule: {e}")
            return False


DATA_MANAGER = DataManager()