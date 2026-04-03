import smtplib
from email.message import EmailMessage
from db import get_db, init_db

init_db()  # Ensure database is initialized


# -------- EMAIL CONFIGURATION --------
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

SMTP_USER = "samd091204@gmail.com"       # your Gmail
SMTP_PASSWORD = "opfn qbts dfja igdl"      # Gmail App Password
FROM_EMAIL = SMTP_USER
# -------------------------------------


def send_email(to_email, subject, body):

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        print(f"Email successfully sent to {to_email}")

    except Exception as ex:
        print(f"Failed to send email to {to_email}: {ex}")


def send_review_links():

    db = get_db()
    cursor = db.cursor()

    query = """
        SELECT o.order_id, u.name, u.email, p.product_name, p.category, p.price
        FROM orders o
        JOIN users u ON o.user_id = u.user_id
        JOIN products p ON o.product_id = p.product_id
        WHERE o.status = 'Delivered' AND IFNULL(o.review_email_sent, 0) = 0
    """

    cursor.execute(query)
    orders = cursor.fetchall()

    print("Orders found:", len(orders))   # Debug line

    for order in orders:

        order_id, customer_name, customer_email, product_name, product_category, product_price = order

        review_link = f"http://127.0.0.1:5000/review?order_id={order_id}"

        subject = f"Please review your purchase: {product_name}"

        body = f"""
Hello {customer_name},

Thank you for shopping with us!

Product Details:
Product: {product_name}
Category: {product_category}
Price: ₹{product_price}
Order ID: {order_id}

We would love to hear your feedback.

Please click the link below to submit your review:

{review_link}

Thank you for helping us improve!

Regards,
E-Commerce Team
"""

        send_email(customer_email, subject, body)

        cursor.execute(
            "UPDATE orders SET review_email_sent = 1 WHERE order_id = ?",
            (order_id,)
        )

    db.commit()

    cursor.close()
    db.close()


if __name__ == "__main__":
    send_review_links()