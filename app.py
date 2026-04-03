from flask import Flask, request, render_template, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db, init_db
import datetime
import os
import uuid

app = Flask(__name__)
app.secret_key = 'change-this-secret-in-prod'

init_db()  # Initialize database on startup

def get_logged_in_user():
    if 'user_id' not in session:
        return None
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT user_id, name, email FROM users WHERE user_id = ?', (session['user_id'],))
    row = cursor.fetchone()
    cursor.close()
    db.close()
    if row:
        return {'user_id': row[0], 'name': row[1], 'email': row[2]}
    return None

@app.route('/')
def home():
    user = get_logged_in_user()
    return render_template('index.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required.', 'danger')
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, password_hash))
            db.commit()
            user_id = cursor.lastrowid
            session['user_id'] = user_id
            flash('Registration successful. You are now logged in.', 'success')
            return redirect(url_for('products'))
        except Exception:
            flash('Email already exists or invalid data. Please try again.', 'danger')
            return redirect(url_for('register'))
        finally:
            cursor.close()
            db.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT user_id, password FROM users WHERE email = ?', (email,))
        row = cursor.fetchone()
        cursor.close()
        db.close()

        if row and check_password_hash(row[1], password):
            session['user_id'] = row[0]
            flash('Logged in successfully.', 'success')
            return redirect(url_for('products'))

        flash('Invalid email or password.', 'danger')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('home'))

@app.route('/products')
def products():
    user = get_logged_in_user()
    selected_category = request.args.get('category', '')
    search_query = request.args.get('q', '').strip()

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT DISTINCT category FROM products')
    categories = [c[0] for c in cursor.fetchall()]

    if search_query:
        like_term = f'%{search_query}%'
        cursor.execute('SELECT product_id, product_name, category, price, image_url, description, rating, review_count FROM products WHERE product_name LIKE ? OR description LIKE ? OR category LIKE ? ORDER BY category, product_id', (like_term, like_term, like_term))
    elif selected_category and selected_category in categories:
        cursor.execute('SELECT product_id, product_name, category, price, image_url, description, rating, review_count FROM products WHERE category = ? ORDER BY product_id', (selected_category,))
    else:
        cursor.execute('SELECT product_id, product_name, category, price, image_url, description, rating, review_count FROM products ORDER BY category, product_id')

    products_list = cursor.fetchall()
    cursor.close()
    db.close()

    products_data = [
        {
            'product_id': p[0],
            'product_name': p[1],
            'category': p[2],
            'price': p[3],
            'image_url': p[4] or 'https://via.placeholder.com/300x200?text=Product',
            'description': p[5] or 'No description available.',
            'rating': p[6] or 0,
            'review_count': p[7] or 0
        }
        for p in products_list
    ]

    grouped = {}
    for item in products_data:
        grouped.setdefault(item['category'], []).append(item)

    return render_template('products.html', categories=categories, selected_category=selected_category, grouped_products=grouped, user=user)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    user = get_logged_in_user()
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT product_id, product_name, category, price, image_url, description, rating, review_count FROM products WHERE product_id = ?', (product_id,))
    product = cursor.fetchone()
    cursor.execute('SELECT review_text, rating, authenticity, image_consistency, image_url FROM reviews WHERE order_id IN (SELECT order_id FROM orders WHERE product_id = ?)', (product_id,))
    reviews = cursor.fetchall()
    cursor.close()
    db.close()

    if product:
        product_data = {
            'product_id': product[0],
            'product_name': product[1],
            'category': product[2],
            'price': product[3],
            'image_url': product[4] or 'https://via.placeholder.com/300x200?text=Product',
            'description': product[5] or 'No description available.',
            'rating': product[6] or 0,
            'review_count': product[7] or 0
        }
        reviews_data = []
        for r in reviews:
            review_text, rating, authenticity, image_consistency, image_url = r
            reviews_data.append({
                'review_text': review_text,
                'rating': rating,
                'authenticity': authenticity,
                'image_consistency': image_consistency,
                'image_url': image_url
            })
        return render_template('product_detail.html', product=product_data, reviews=reviews_data, user=user)
    return 'Product not found'

@app.route('/buy/<int:product_id>', methods=['POST'])
def buy(product_id):
    user = get_logged_in_user()
    if not user:
        flash('Please log in to place an order.', 'warning')
        return redirect(url_for('login'))

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        'INSERT INTO orders (user_id, product_id, delivery_date, status) VALUES (?, ?, ?, ?)',
        (user['user_id'], product_id, datetime.date.today().isoformat(), 'Delivered')
    )

    db.commit()
    cursor.close()
    db.close()

    flash('Order placed successfully! You will receive a review link soon.', 'success')
    return render_template('order_success.html', user=user)

@app.route('/review')
def review():
    order_id = request.args.get('order_id')
    if not order_id:
        return 'Order ID required', 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT product_id FROM orders WHERE order_id = ?', (order_id,))
    order_row = cursor.fetchone()
    if not order_row:
        cursor.close()
        db.close()
        return 'Order not found', 404

    product_id = order_row[0]
    cursor.execute('SELECT product_name, image_url, category FROM products WHERE product_id = ?', (product_id,))
    prod = cursor.fetchone()
    cursor.close()
    db.close()

    if not prod:
        return 'Product not found for this order', 404

    product_data = {
        'product_name': prod[0],
        'image_url': prod[1] or 'https://via.placeholder.com/300x200?text=Product',
        'category': prod[2]
    }

    user = get_logged_in_user()
    return render_template('review.html', order_id=order_id, product=product_data, user=user)

@app.route('/submit_review', methods=['POST'])
def submit_review():
    order_id = request.form.get('order_id')
    review_text = request.form.get('review')
    rating = int(request.form.get('rating'))

    from ml_model import predict_review, analyze_sentiment, check_review_genuinity, check_image_text_consistency

    sentiment = analyze_sentiment(review_text)
    authenticity = predict_review(review_text)
    image_url = None
    image_file = request.files.get('image')

    if image_file and image_file.filename:
        uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
        os.makedirs(uploads_dir, exist_ok=True)
        filename = f"{uuid.uuid4().hex}_{os.path.basename(image_file.filename)}"
        save_path = os.path.join(uploads_dir, filename)
        image_file.save(save_path)
        image_url = f"/static/uploads/{filename}"

    image_consistency = check_image_text_consistency(review_text, image_url)

    db = get_db()
    cursor = db.cursor()
    cursor.execute('INSERT INTO reviews (order_id, review_text, rating, sentiment, authenticity, image_consistency, status, image_url) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                   (order_id, review_text, rating, sentiment, authenticity, image_consistency, 'approved', image_url))
    db.commit()
    cursor.close()
    db.close()

    flash('Review submitted successfully!', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)