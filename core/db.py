# IMPORT LIBRARIES
import mysql.connector
import os


# MySQL DB INIT
db = mysql.connector.connect(
    host=str(os.environ.get("DB_HOST", "127.0.0.1")),
    user=str(os.environ.get("DB_USER", "root")),
    password=str(os.environ.get("DB_PASSWORD", "")),
    database="buffetdb"
)

cursor = db.cursor()


# Check if db initiated
def check_db():
    cursor.execute("SHOW TABLES")
    
    check = ()

    for x in cursor:
        check += x

    if 'config' in check:
        return True

    else:
        return False


# Setups database - Creates tables etc.
def initialize_db():
    # CONFIG TABLE
    cursor.execute("CREATE TABLE IF NOT EXISTS config (name TINYTEXT, description TINYTEXT, akey TINYTEXT)")

    # PRODUCTS TABLES
    cursor.execute("CREATE TABLE IF NOT EXISTS products (id INT AUTO_INCREMENT PRIMARY KEY, name TINYTEXT, price FLOAT, category TINYTEXT)")

    cursor.execute("CREATE TABLE IF NOT EXISTS products_images (id INT AUTO_INCREMENT PRIMARY KEY, image LONGTEXT)")

    cursor.execute("CREATE TABLE IF NOT EXISTS products_stock (id INT AUTO_INCREMENT PRIMARY KEY, stock INT, sold INT DEFAULT 0)")

    cursor.execute("CREATE TABLE IF NOT EXISTS products_visibility (id INT AUTO_INCREMENT PRIMARY KEY, visible BOOL DEFAULT True)")

    # ACCOUNT TABLES
    cursor.execute("CREATE TABLE IF NOT EXISTS accounts (pin INT PRIMARY KEY, name TINYTEXT)")
    
    cursor.execute("CREATE TABLE IF NOT EXISTS accounts_opened (account_pin INT, product_id INT)")

    # TRANSACTIONS TABLE
    cursor.execute("CREATE TABLE IF NOT EXISTS transactions (id INT AUTO_INCREMENT PRIMARY KEY, account INT, products TEXT, date TINYTEXT, time TINYTEXT, price FLOAT)")

def clear_db():
    cursor.execute("DROP TABLE IF EXISTS config, products, products_images, products_stock, products_visibility, accounts, accounts_opened, transactions") 
