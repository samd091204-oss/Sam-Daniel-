import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from db import get_db, init_db

init_db()


def send_review_links():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT o.order_id, u.name, u.email, p.product_name, p.category, p.price
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        JOIN products p ON o.product_id = p.product_id
        WHERE o.status = 'Delivered' AND o.review_email_sent = 0
    ''')

    orders = cursor.fetchall()

    smtp_host = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'sam091204@gmail.com'
    smtp_pass = 'opfn qbts dfja igdl'
    from_email = 'sam091204@gmail.com'

    for order_id, name, email, product_name, category, price in orders:
        review_link = f'http://127.0.0.1:5000/review?order_id={order_id}'
        subject = f'Review request for your recent purchase: {product_name}'
        body = f"""
Hello {name},

Thank you for purchasing {product_name} ({category}) from our store.
We would love your honest review. Please click the link below to share your feedback:

{review_link}

Your insights help us ensure product quality and improve service for all customers.

Product: {product_name}
Category: {category}
Price: ₹{price}
Order ID: {order_id}

Thank you,
The Ecommerce Team
"""

        try:
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(from_email, email, msg.as_string())

            print(f'Sent review email to {email}')

            cursor.execute('UPDATE orders SET review_email_sent = 1 WHERE order_id = ?', (order_id,))
            db.commit()
        except Exception as e:
            print('Failed to send email to', email, 'error:', e)

    cursor.close()
    db.close()


if __name__ == '__main__':
    send_review_links()