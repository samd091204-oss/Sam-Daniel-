from flask import Flask, request, render_template
from db import get_db, init_db
import datetime

app = Flask(__name__)

init_db()  # Initialize database on startup

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/products")
def products():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT product_id, product_name, category, price FROM products")
    products_list = cursor.fetchall()
    cursor.close()
    db.close()
    products_data = [{'product_id': p[0], 'product_name': p[1], 'category': p[2], 'price': p[3]} for p in products_list]
    return render_template('products.html', products=products_data)

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT product_id, product_name, category, price FROM products WHERE product_id = ?", (product_id,))
    product = cursor.fetchone()
    cursor.execute("SELECT review_text, rating, trust_score FROM reviews WHERE order_id IN (SELECT order_id FROM orders WHERE product_id = ?)", (product_id,))
    reviews = cursor.fetchall()
    cursor.close()
    db.close()
    if product:
        product_data = {'product_id': product[0], 'product_name': product[1], 'category': product[2], 'price': product[3]}
        reviews_data = [{'review_text': r[0], 'rating': r[1], 'trust_score': r[2]} for r in reviews]
        return render_template('product_detail.html', product=product_data, reviews=reviews_data)
    return "Product not found"

@app.route("/buy/<int:product_id>", methods=["GET", "POST"])
def buy(product_id):
    db = get_db()
    cursor = db.cursor()

    # insert order
    cursor.execute(
        "INSERT INTO orders (user_id, product_id, delivery_date, status) VALUES (?, ?, ?, ?)",
        (1, product_id, datetime.date.today().isoformat(), "Delivered")
    )

    db.commit()
    cursor.close()
    db.close()

    return render_template('order_success.html')

@app.route("/review")
def review():
    order_id = request.args.get('order_id')
    if not order_id:
        return "Order ID required", 400
    return render_template('review.html', order_id=order_id)

@app.route("/submit_review", methods=["POST"])
def submit_review():
    order_id = request.form.get("order_id")
    review_text = request.form.get("review")
    rating = int(request.form.get("rating"))

    # Calculate trust_score
    from ml_model import predict_review
    from utils import check_sentiment, calculate_trust

    sentiment = check_sentiment(review_text)
    ml_result = predict_review(review_text)
    trust_score = calculate_trust(sentiment, rating, 1 if ml_result == "Genuine" else 0)

    # Insert into db
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO reviews (order_id, review_text, rating, sentiment, ml_prediction, trust_score, status) VALUES (?, ?, ?, ?, ?, ?, ?)", (order_id, review_text, rating, sentiment, ml_result, trust_score, 'approved'))
    db.commit()
    cursor.close()
    db.close()

    return "Review submitted successfully!"

if __name__ == "__main__":
    app.run(debug=True)