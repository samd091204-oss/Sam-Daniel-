import sqlite3


def get_db():
    return sqlite3.connect('ecommerce.db')


def ensure_column(cursor, table_name, column_name, column_type):
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    if column_name not in columns:
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT
        )
    ''')
    ensure_column(cursor, 'users', 'password', 'TEXT')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT,
            category TEXT,
            price REAL,
            image_url TEXT,
            description TEXT,
            rating REAL,
            review_count INTEGER
        )
    ''')
    ensure_column(cursor, 'products', 'image_url', 'TEXT')
    ensure_column(cursor, 'products', 'description', 'TEXT')
    ensure_column(cursor, 'products', 'rating', 'REAL')
    ensure_column(cursor, 'products', 'review_count', 'INTEGER')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            delivery_date TEXT,
            status TEXT,
            review_email_sent INTEGER DEFAULT 0
        )
    ''')
    ensure_column(cursor, 'orders', 'review_email_sent', 'INTEGER')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            review_text TEXT,
            rating INTEGER,
            sentiment TEXT,
            authenticity TEXT,
            image_consistency TEXT,
            status TEXT,
            image_url TEXT
        )
    ''')
    ensure_column(cursor, 'reviews', 'sentiment', 'TEXT')
    ensure_column(cursor, 'reviews', 'authenticity', 'TEXT')
    ensure_column(cursor, 'reviews', 'image_consistency', 'TEXT')
    ensure_column(cursor, 'reviews', 'image_url', 'TEXT')

    # Insert sample user
    cursor.execute("INSERT OR IGNORE INTO users (user_id, name, email, password) VALUES (1, 'John Doe', 'john@example.com', 'password1')")

    # Insert sample products (50)
    sample_products = [
        (1, '4K Smart TV', 'Electronics', 64999, 'https://via.placeholder.com/300x200?text=4K+Smart+TV', '65-inch Ultra HD Smart TV with HDR and voice remote', 4.7, 120),
        (2, 'Wireless Noise Cancelling Headphones', 'Electronics', 11999, 'https://via.placeholder.com/300x200?text=Headphones', 'Bluetooth over-ear headphones with ANC', 4.5, 345),
        (3, 'Gaming Laptop', 'Electronics', 79999, 'https://via.placeholder.com/300x200?text=Gaming+Laptop', 'High-performance laptop with RTX graphics', 4.6, 88),
        (4, 'Smart Home Speaker', 'Electronics', 4999, 'https://via.placeholder.com/300x200?text=Smart+Speaker', 'Voice assistant speaker with rich sound', 4.3, 222),
        (5, 'Fitness Tracker', 'Electronics', 2499, 'https://via.placeholder.com/300x200?text=Fitness+Tracker', 'Waterproof fitness tracker for daily health', 4.1, 401),
        (6, 'Men’s Golf Polo Shirt', 'Fashion', 1999, 'https://via.placeholder.com/300x200?text=Golf+Polo', 'Breathable performance polo shirt', 4.2, 115),
        (7, 'Women’s Denim Jacket', 'Fashion', 3499, 'https://via.placeholder.com/300x200?text=Denim+Jacket', 'Classic cotton jacket with modern fit', 4.4, 89),
        (8, 'Running Sneakers', 'Fashion', 5999, 'https://via.placeholder.com/300x200?text=Running+Sneakers', 'Lightweight and comfortable running shoes', 4.6, 173),
        (9, 'Fashion Leather Wallet', 'Fashion', 1299, 'https://via.placeholder.com/300x200?text=Leather+Wallet', 'RFID-blocking premium leather wallet', 4.3, 67),
        (10, 'Sunglasses Set', 'Fashion', 999, 'https://via.placeholder.com/300x200?text=Sunglasses', 'UV400 polarized sunglasses with case', 4.5, 210),
        (11, 'Nonstick Cookware Set', 'Home & Kitchen', 7999, 'https://via.placeholder.com/300x200?text=Cookware+Set', '10-piece premium nonstick cookware set', 4.6, 140),
        (12, 'Air Fryer 6L', 'Home & Kitchen', 6999, 'https://via.placeholder.com/300x200?text=Air+Fryer', 'Digital air fryer for healthy cooking', 4.5, 186),
        (13, 'Espresso Coffee Machine', 'Home & Kitchen', 9999, 'https://via.placeholder.com/300x200?text=Coffee+Machine', 'Professional espresso machine with steam wand', 4.7, 104),
        (14, 'Memory Foam Pillow', 'Home & Kitchen', 2499, 'https://via.placeholder.com/300x200?text=Pillow', 'Ergonomic pillow for better sleep', 4.4, 78),
        (15, 'Robot Vacuum Cleaner', 'Home & Kitchen', 14999, 'https://via.placeholder.com/300x200?text=Robot+Vacuum', 'Smart mapping robot vacuum with app control', 4.2, 63),
        (16, 'Best-selling Novel', 'Books', 499, 'https://via.placeholder.com/300x200?text=Novel', 'Suspense thriller bestseller hardcover', 4.8, 240),
        (17, 'Self-help Guide', 'Books', 399, 'https://via.placeholder.com/300x200?text=Self+Help', 'Personal growth and productivity book', 4.6, 156),
        (18, 'Children’s Storybook', 'Books', 299, 'https://via.placeholder.com/300x200?text=Storybook', 'Illustrated bedtime story for kids', 4.7, 178),
        (19, 'Cookbook', 'Books', 599, 'https://via.placeholder.com/300x200?text=Cookbook', 'Global cuisine recipes for home chefs', 4.5, 132),
        (20, 'Business Strategy Book', 'Books', 699, 'https://via.placeholder.com/300x200?text=Business+Book', 'Startup and leadership playbook', 4.3, 97),
        (21, 'Skin Care Kit', 'Beauty & Personal Care', 2599, 'https://via.placeholder.com/300x200?text=Skin+Care', '5-step daily skin care bundle', 4.5, 186),
        (22, 'Electric Toothbrush', 'Beauty & Personal Care', 1999, 'https://via.placeholder.com/300x200?text=Toothbrush', 'Rechargeable sonic toothbrush with timer', 4.4, 125),
        (23, 'Hair Dryer', 'Beauty & Personal Care', 2899, 'https://via.placeholder.com/300x200?text=Hair+Dryer', 'Ceramic fast-dry hair dryer', 4.6, 88),
        (24, 'Perfume Gift Set', 'Beauty & Personal Care', 3499, 'https://via.placeholder.com/300x200?text=Perfume', 'Luxury fragrance set for men', 4.5, 101),
        (25, 'Body Lotion', 'Beauty & Personal Care', 799, 'https://via.placeholder.com/300x200?text=Lotion', 'Hydrating body lotion with vitamins', 4.2, 74),
        (26, 'Yoga Mat', 'Sports & Fitness', 1499, 'https://via.placeholder.com/300x200?text=Yoga+Mat', 'Non-slip exercise yoga mat', 4.7, 220),
        (27, 'Adjustable Dumbbells', 'Sports & Fitness', 4999, 'https://via.placeholder.com/300x200?text=Dumbbells', '17.5 kg adjustable dumbbell set', 4.5, 132),
        (28, 'Running Shoes', 'Sports & Fitness', 5999, 'https://via.placeholder.com/300x200?text=Running+Shoes', 'Breathable running shoes for men', 4.4, 191),
        (29, 'Resistance Bands', 'Sports & Fitness', 899, 'https://via.placeholder.com/300x200?text=Resistance+Bands', 'Set of 5 resistance bands for home workouts', 4.3, 211),
        (30, 'Fitness Watch', 'Sports & Fitness', 6999, 'https://via.placeholder.com/300x200?text=Fitness+Watch', 'Multi-sport fitness smartwatch', 4.2, 143),
        (31, 'Building Blocks Set', 'Toys & Games', 1299, 'https://via.placeholder.com/300x200?text=Blocks+Set', 'Creative building blocks for kids', 4.6, 98),
        (32, 'Board Game', 'Toys & Games', 1699, 'https://via.placeholder.com/300x200?text=Board+Game', 'Strategy board game for family fun', 4.7, 113),
        (33, 'RC Car', 'Toys & Games', 2199, 'https://via.placeholder.com/300x200?text=RC+Car', 'Remote controlled racing car', 4.4, 64),
        (34, 'Puzzle Pack', 'Toys & Games', 899, 'https://via.placeholder.com/300x200?text=Puzzle', '500-piece jigsaw puzzle set', 4.5, 80),
        (35, 'Dollhouse', 'Toys & Games', 2999, 'https://via.placeholder.com/300x200?text=Dollhouse', 'Mini dollhouse with furniture', 4.3, 55),
        (36, 'Organic Groceries Set', 'Groceries', 1599, 'https://via.placeholder.com/300x200?text=Groceries', 'Organic breakfast essentials pack', 4.4, 123),
        (37, 'Olive Oil', 'Groceries', 799, 'https://via.placeholder.com/300x200?text=Olive+Oil', 'Extra virgin olive oil 1L', 4.6, 121),
        (38, 'Protein Powder', 'Groceries', 2399, 'https://via.placeholder.com/300x200?text=Protein', 'Whey protein for post-workout', 4.5, 87),
        (39, 'Coffee Beans', 'Groceries', 1099, 'https://via.placeholder.com/300x200?text=Coffee', 'Premium roasted coffee beans', 4.7, 173),
        (40, 'Herbal Tea Collection', 'Groceries', 599, 'https://via.placeholder.com/300x200?text=Herbal+Tea', 'Assorted herbal tea 20 bags', 4.4, 145),
        (41, 'Leather Camera Strap', 'Accessories', 999, 'https://via.placeholder.com/300x200?text=Camera+Strap', 'Vintage leather camera strap', 4.3, 68),
        (42, 'Bluetooth Speaker', 'Accessories', 2599, 'https://via.placeholder.com/300x200?text=Speaker', 'Portable Bluetooth speaker', 4.5, 132),
        (43, 'Phone Case', 'Accessories', 499, 'https://via.placeholder.com/300x200?text=Phone+Case', 'Shockproof phone case', 4.4, 201),
        (44, 'Travel Backpack', 'Accessories', 3999, 'https://via.placeholder.com/300x200?text=Backpack', 'Water-resistant travel backpack', 4.6, 158),
        (45, 'Sunglasses', 'Accessories', 1299, 'https://via.placeholder.com/300x200?text=Sunglasses', 'UV protection polarized sunglasses', 4.2, 99),
        (46, 'Office Chair', 'Office Supplies', 6999, 'https://via.placeholder.com/300x200?text=Office+Chair', 'Ergonomic mesh office chair', 4.3, 116),
        (47, 'Standing Desk', 'Office Supplies', 12999, 'https://via.placeholder.com/300x200?text=Standing+Desk', 'Height-adjustable desk', 4.5, 78),
        (48, 'Stationery Kit', 'Office Supplies', 899, 'https://via.placeholder.com/300x200?text=Stationery', 'Complete desk stationery kit', 4.4, 89),
        (49, 'Notebook Bundle', 'Office Supplies', 499, 'https://via.placeholder.com/300x200?text=Notebook', 'Set of 5 ruled notebooks', 4.6, 103),
        (50, 'Desk Lamp', 'Office Supplies', 1599, 'https://via.placeholder.com/300x200?text=Desk+Lamp', 'LED desk lamp with brightness levels', 4.5, 72)
    ]

    for p in sample_products:
        cursor.execute('INSERT OR IGNORE INTO products (product_id, product_name, category, price, image_url, description, rating, review_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', p)

    db.commit()
    cursor.close()
    db.close()