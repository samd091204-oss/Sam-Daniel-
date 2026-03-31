from db import get_db, init_db

init_db()  # Ensure database is initialized

def send_review_links():
    db = get_db()
    cursor = db.cursor()

    # get delivered orders
    cursor.execute("SELECT order_id FROM orders WHERE status='Delivered'")
    orders = cursor.fetchall()

    for order in orders:
        order_id = order[0]
        print(f"Send email with review link:")
        print(f"http://127.0.0.1:5000/review?order_id={order_id}")

    cursor.close()
    db.close()

if __name__ == "__main__":
    send_review_links()