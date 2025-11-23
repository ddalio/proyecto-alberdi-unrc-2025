from app import mail
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
from flask import jsonify, flash, redirect, url_for
from flask import current_app

def responder_error(mensaje, es_ajax, url_redireccion):
    if es_ajax:
        return jsonify({'success': False, 'error': mensaje})
    else:
        flash(mensaje, "error")
        return redirect(url_redireccion)

def formatear_fecha(fecha):
    if fecha:
        return fecha.strftime("%d/%m/%Y %H:%M")
    return "No disponible"

def generar_token_verificacion(nombre_usuario):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(nombre_usuario, salt='email-verification')

def enviar_email_verificacion(email, token, nombre):
    subject = "Verifica tu cuenta"
    verification_url = url_for('cuentas.verificar_email', token=token, _external=True)
    
    html_body = f"""
    <h2>Verifica tu cuenta</h2>
    <p>Hola {nombre},</p>
    <p>Por favor haz clic en el siguiente enlace para verificar tu cuenta:</p>
    <a href="{verification_url}">Verificar mi cuenta</a>
    <p>Este enlace expirará en 24 horas.</p>
    """
    
    send_email(subject, email, html_body)

def validar_email(email):
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, email) is not None

import re

def validar_contraseña(password):
    if len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres."

    if not re.search(r"[A-Z]", password):
        return "La contraseña debe contener al menos una letra mayúscula."

    if not re.search(r"[a-z]", password):
        return "La contraseña debe contener al menos una letra minúscula."

    if not re.search(r"[0-9]", password):
        return "La contraseña debe contener al menos un número."

    if not re.search(r"[@$!%*?&#]", password):
        return "La contraseña debe contener al menos un símbolo (@$!%*?&#)."

    return None  # Si no hay errores

def send_email(subject, recipient, html_body):
    msg = Message(
        subject=subject,
        recipients=[recipient],
        sender="no-reply.alberdi@gmail.com"
    )
    msg.html = html_body
    mail.send(msg)
