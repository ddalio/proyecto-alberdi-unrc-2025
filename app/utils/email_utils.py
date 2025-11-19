from app import mail
from flask_mail import Message

def send_email(subject, recipient, html_body):
    msg = Message(
        subject=subject,
        recipients=[recipient],
        sender="no-reply.alberdi@gmail.com"
    )
    msg.html = html_body
    mail.send(msg)
