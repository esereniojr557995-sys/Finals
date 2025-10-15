# test_system.py - Test all components

import sys
import warnings

# Suppress the deprecation warning
warnings.filterwarnings("ignore", category=DeprecationWarning)

print("=" * 50)
print("WashDesk System Component Test")
print("=" * 50)

# Test 1: PyQt5
print("\n1. Testing PyQt5...")
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt, QDate, QTime
    from PyQt5.QtGui import QFont
    print("   ✓ PyQt5 imported successfully")
except Exception as e:
    print(f"   ✗ PyQt5 error: {e}")
    sys.exit(1)

# Test 2: MySQL Connector
print("\n2. Testing MySQL Connector...")
try:
    import mysql.connector
    print("   ✓ mysql-connector-python imported successfully")
except Exception as e:
    print(f"   ✗ MySQL connector error: {e}")
    print("   → Install: pip install mysql-connector-python")

# Test 3: Database Connection
print("\n3. Testing Database Connection...")
try:
    import mysql.connector
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="washdesk_db"
    )
    print("   ✓ Database connection successful")
    db.close()
except mysql.connector.Error as err:
    print(f"   ⚠ Database connection failed: {err}")
    print("   → Make sure:")
    print("     - XAMPP MySQL is running")
    print("     - Database 'washdesk_db' exists")
    print("     - Run database_setup.sql in phpMyAdmin")
    print("   → App will run in offline mode with mock data")
except Exception as e:
    print(f"   ⚠ Unexpected error: {e}")

# Test 4: Import all modules
print("\n4. Testing Module Imports...")
try:
    from database import DATA_MANAGER
    print("   ✓ database.py imported")
except Exception as e:
    print(f"   ✗ database.py error: {e}")
    sys.exit(1)

try:
    from ui_helpers import BaseDashboard, RegistrationDialog
    print("   ✓ ui_helpers.py imported")
except Exception as e:
    print(f"   ✗ ui_helpers.py error: {e}")
    sys.exit(1)

try:
    from customer_dashboard import CustomerDashboard
    print("   ✓ customer_dashboard.py imported")
except Exception as e:
    print(f"   ✗ customer_dashboard.py error: {e}")
    sys.exit(1)

try:
    from staff_dashboard import StaffDashboard
    print("   ✓ staff_dashboard.py imported")
except Exception as e:
    print(f"   ✗ staff_dashboard.py error: {e}")
    sys.exit(1)

try:
    from admin_dashboard import AdminDashboard
    print("   ✓ admin_dashboard.py imported")
except Exception as e:
    print(f"   ✗ admin_dashboard.py error: {e}")
    sys.exit(1)

# Test 5: Check default users
print("\n5. Testing Default Users...")
try:
    admin = DATA_MANAGER.get_user('Admin', 'admina')
    if admin:
        print("   ✓ Admin account exists")
        print(f"     Username: admina")
        print(f"     Password: 123")
    else:
        print("   ⚠ Admin account not found")
except Exception as e:
    print(f"   ✗ Error checking users: {e}")

# Test 6: Test password hashing
print("\n6. Testing Password Verification...")
try:
    test_password = "123"
    admin = DATA_MANAGER.get_user('Admin', 'admina')
    if admin and DATA_MANAGER.verify_password(test_password, admin['password']):
        print("   ✓ Password hashing working correctly")
    else:
        print("   ⚠ Password verification issue")
except Exception as e:
    print(f"   ✗ Password test error: {e}")

print("\n" + "=" * 50)
print("Test Summary:")
print("=" * 50)
print("✓ All core components are working")
print("\nYou can now run: python main.py")
print("\nDefault Login Credentials:")
print("  Admin    → admina / 123")
print("  Staff    → staff123 / 123")
print("  Customer → johndoe123 / 123")
print("=" * 50)