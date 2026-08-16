

from flask_mail import Message

from mail_config import mail


def send_order_confirmation(user_email, order_id, total_price):
    message = Message(
        subject="Order Confirmation",
        recipients=[user_email]
    )

    message.body = f"""
Hello,

Thank you for your order!

Order ID: {order_id}
Total: ₦{total_price}

Your order has been received and is being processed.

Thank you for shopping with us!
"""

    mail.send(message)