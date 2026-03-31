import sqlite3

def get_db():
    return sqlite3.connect('ecommerce.db')

def init_db():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            category TEXT,
            price REAL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            delivery_date TEXT,
            status TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            review_text TEXT,
            rating INTEGER,
            sentiment REAL,
            ml_prediction TEXT,
            trust_score REAL,
            status TEXT
        )
    ''')
    # Insert sample user
    cursor.execute("INSERT OR IGNORE INTO users (user_id, name, email) VALUES (1, 'John Doe', 'john@example.com')")
    # Insert sample products
    cursor.execute("INSERT OR IGNORE INTO products (product_id, product_name, category, price) VALUES (1, 'Laptop', 'Electronics', 50000)")
    cursor.execute("INSERT OR IGNORE INTO products (product_id, product_name, category, price) VALUES (2, 'Book', 'Education', 500)")
    db.commit()
    cursor.close()
    db.close()