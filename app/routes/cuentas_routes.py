import re
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import Cuenta, Administrador
from app.utils.def_cuentas import *
from werkzeug.security import generate_password_hash
from app import db
from app.decorators import admin_required, login_required
from datetime import datetime
from app import db 
import re

cuentas_bp = Blueprint('cuentas', __name__, url_prefix='/cuentas')

# Configuración de seguridad para el hash
HASH_METHOD = 'pbkdf2:sha256'
SALT_LENGTH = 16
MIN_PASSWORD_LENGTH = 8

@cuentas_bp.route("/")
@login_required
@admin_required 
def cuentas():
    cuentas = Cuenta.query.all()

    # Traemos todos los administradores
    admins = {admin.nombre_usuario for admin in Administrador.query.all()}

    # Agregamos el rol a cada cuenta
    cuentas_con_rol = []
    for cuenta in cuentas:
        rol = "Administrador" if cuenta.nombre_usuario in admins else "Usuario"
        cuentas_con_rol.append({
            "nombre_usuario": cuenta.nombre_usuario,
            "nombre": cuenta.nombre,
            "apellido": cuenta.apellido,
            "email": cuenta.email,
            "rol": rol
        })
    return render_template('cuentas.html', list_cuentas=cuentas_con_rol)

@cuentas_bp.route("/crear", methods=['POST'])
@admin_required 
def crear_cuenta():
    
    es_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    URL_CUENTAS = url_for('cuentas.cuentas') 
    
    nombre_usuario = request.form.get('usuario', '').strip()
    contraseña = request.form.get('password', '').strip()
    repetir_contraseña = request.form.get('password2', '').strip()
    nombre = request.form.get('nombre', '').strip()
    apellido = request.form.get('apellido', '').strip()
    email = request.form.get('email', '').strip().lower()
    rol = request.form.get('rol', '').strip()

    campos_obligatorios = [nombre_usuario, contraseña, repetir_contraseña, nombre, apellido, email, rol]
    
    if not all(campos_obligatorios):
        mensaje = 'Todos los campos son obligatorios'
        return responder_error(mensaje, es_ajax, URL_CUENTAS)

    if not validar_email(email):
        mensaje = 'El formato del email no es válido'
        return responder_error(mensaje, es_ajax, URL_CUENTAS)

    if contraseña != repetir_contraseña:
        mensaje = 'Las contraseñas no coinciden'
        return responder_error(mensaje, es_ajax, URL_CUENTAS)

    error_contraseña = validar_contraseña(contraseña)
    if error_contraseña:
        return responder_error(error_contraseña, es_ajax, URL_CUENTAS)

    cuenta = Cuenta.query.filter_by(nombre_usuario=nombre_usuario).first()
    if cuenta:
        mensaje = 'El nombre de usuario ya existe'
        return responder_error(mensaje, es_ajax, URL_CUENTAS)

    cuenta_con_email = Cuenta.query.filter_by(email=email).first(); 
    if cuenta_con_email:
        mensaje = 'El email ya está registrado'
        return responder_error(mensaje, es_ajax, URL_CUENTAS)

    roles_validos = ['administrador', 'usuario']
    if rol.lower() not in roles_validos:
        mensaje = 'Rol no válido'
        return responder_error(mensaje, es_ajax, URL_CUENTAS)

    try:
        nueva_cuenta = Cuenta(
            nombre_usuario=nombre_usuario,
            email=email,
            nombre=nombre,
            apellido=apellido
        )
        nueva_cuenta.password_hash = generate_password_hash(contraseña)

        db.session.add(nueva_cuenta)
        db.session.flush()

        # Generar token y enviar email de verificación
        token = generar_token_verificacion(nueva_cuenta.nombre_usuario)
        enviar_email_verificacion(nueva_cuenta.email, token, nueva_cuenta.nombre)

        if rol.lower() == "administrador":
            nuevo_admin = Administrador(nombre_usuario=nombre_usuario)
            db.session.add(nuevo_admin)

        db.session.commit()

        if es_ajax:
            return jsonify({
                'success': True, 
                'usuario_id': nueva_cuenta.nombre_usuario,
                'message': 'Usuario creado exitosamente y email de verificación enviado'
            })
        else:
            flash("Cuenta creada exitosamente y email de verificación enviado", "cuentas_success")
            return redirect(URL_CUENTAS)

    except Exception as e:
        db.session.rollback()
        error_msg = f"Error al crear la cuenta: {str(e)}"
        return responder_error(error_msg, es_ajax, URL_CUENTAS)


@cuentas_bp.route("/editar/<nombre_usuario>", methods=['POST'])
@admin_required 
def editar_cuenta(nombre_usuario):
    # Buscar la cuenta a editar
    cuenta = Cuenta.query.filter_by(nombre_usuario=nombre_usuario).first()
    if not cuenta:
        flash("La cuenta no existe", "cuentas_error")
        return redirect(url_for('cuentas.cuentas'))
    
    # Procesar formulario POST (actualizar)
    nuevo_nombre = request.form.get('nombre', '').strip()
    nuevo_apellido = request.form.get('apellido', '').strip()
    nuevo_email = request.form.get('email', '').strip().lower()
    nuevo_rol = request.form.get('rol', '').strip()
    nueva_contraseña = request.form.get('password', '').strip()
    repetir_contraseña = request.form.get('password2', '').strip()

    try:
        # Validaciones básicas
        if not all([nuevo_nombre, nuevo_apellido, nuevo_email, nuevo_rol]):
            flash("Todos los campos excepto contraseña son obligatorios", "cuentas_error")
            return redirect(url_for('cuentas.cuentas'))
        
        # Validar email
        if not validar_email(nuevo_email):
            flash("El formato del email no es válido", "cuentas_error")
            return redirect(url_for('cuentas.cuentas'))
        
        # Validar que el email no esté en uso por otra cuenta
        cuenta_existente = Cuenta.query.filter_by(email=nuevo_email).first()
        if cuenta_existente and cuenta_existente.nombre_usuario != nombre_usuario:
            flash("El email ya está en uso por otra cuenta", "cuentas_error")
            return redirect(url_for('cuentas.cuentas'))
        
        # Validar rol
        roles_validos = ['administrador', 'usuario', 'empleado']
        if nuevo_rol.lower() not in roles_validos:
            flash("Rol no válido", "cuentas_error")
            return redirect(url_for('cuentas.cuentas'))
        
        # Actualizar datos básicos
        cuenta.nombre = nuevo_nombre
        cuenta.apellido = nuevo_apellido
        cuenta.email = nuevo_email
        
        # Manejar cambio de contraseña (si se proporcionó)
        if nueva_contraseña:
            if nueva_contraseña != repetir_contraseña:
                flash("Las contraseñas no coinciden", "cuentas_error")
                return redirect(url_for('cuentas.cuentas'))
            
            error_contraseña = validar_contraseña(nueva_contraseña)
            if error_contraseña:
                flash(error_contraseña, "error")
                return redirect(url_for('cuentas.cuentas'))
            
            # Encriptar nueva contraseña
            cuenta.password_hash = generate_password_hash(
                nueva_contraseña, 
                method=HASH_METHOD, 
                salt_length=SALT_LENGTH
            )
        
        admin_actual = Administrador.query.filter_by(nombre_usuario=nombre_usuario).first()
        
        if nuevo_rol.lower() == "administrador" and not admin_actual:
            nuevo_admin = Administrador(nombre_usuario=nombre_usuario)
            db.session.add(nuevo_admin)
        elif nuevo_rol.lower() != "administrador" and admin_actual:
            db.session.delete(admin_actual)
        
        db.session.commit()
        flash(f"Cuenta de {nombre_usuario} actualizada exitosamente ", "cuentas_success")
        return redirect(url_for("cuentas.cuentas"))
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar la cuenta: {str(e)}", "cuentas_error")
        return redirect(url_for('cuentas.cuentas'))


@cuentas_bp.route("/eliminar/<nombre_usuario>", methods=['POST'])
@admin_required 
def eliminar_cuenta(nombre_usuario):
    cuenta = Cuenta.query.filter_by(nombre_usuario=nombre_usuario).first()
    if not cuenta:
            flash("La cuenta no existe", "error")
            return redirect(url_for('cuentas.cuentas'))

    admin = Administrador.query.filter_by(nombre_usuario=nombre_usuario).first()
    if admin:
        db.session.delete(admin)

    db.session.delete(cuenta)
    db.session.commit()
    flash(f"La cuenta '{nombre_usuario}' fue eliminada correctamente.", "cuentas_success")
    return redirect(url_for('cuentas.cuentas'))

@cuentas_bp.route("/detalles/<nombre_usuario>")
def detalles_cuenta(nombre_usuario):
    try:
        cuenta = Cuenta.query.filter_by(nombre_usuario=nombre_usuario).first()
        
        if not cuenta:
            return jsonify({
                "success": False,
                "error": "La cuenta no existe"
            }), 404
        
        # Verificar si es administrador
        es_admin = Administrador.query.filter_by(nombre_usuario=nombre_usuario).first() is not None
    
        
        datos_cuenta = {
            "nombre_usuario": cuenta.nombre_usuario,
            "nombre": cuenta.nombre,
            "apellido": cuenta.apellido,
            "email": cuenta.email,
            "rol": "Administrador" if es_admin else "Usuario",
            "fecha_creacion": formatear_fecha(cuenta.fecha_creacion),
            "ultimo_acceso": formatear_fecha(cuenta.ultimo_acceso)
        }
        
        return jsonify({
            "success": True,
            "cuenta": datos_cuenta
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@cuentas_bp.route('/verificar-password', methods=['POST'])
def verificar_password():
    try:
        data = request.get_json()
        nombre_usuario = data.get('usuario')
        nueva_password = data.get('nueva_password')
        
        # Buscar el usuario en la base de datos
        usuario = Cuenta.query.filter_by(nombre_usuario=nombre_usuario).first()
        
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'})
        
        if check_password_hash(usuario.password_hash, nueva_password):
            return jsonify({'success': True, 'es_igual': True})
        else:
            return jsonify({'success': True, 'es_igual': False})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@cuentas_bp.route("/buscar", methods=['POST'])
@admin_required 
def buscar_cuenta():
    try:
        data = request.get_json()
        termino_busqueda = data.get('busqueda', '').strip()
        
        if not termino_busqueda:
            cuentas = Cuenta.query.all()
        else:
            # Buscar en múltiples campos
            cuentas = Cuenta.query.filter(
                db.or_(
                    Cuenta.nombre_usuario.ilike(f'%{termino_busqueda}%'),
                    Cuenta.nombre.ilike(f'%{termino_busqueda}%'),
                    Cuenta.apellido.ilike(f'%{termino_busqueda}%'),
                    Cuenta.email.ilike(f'%{termino_busqueda}%')
                )
            ).all()
        
        # Traemos todos los administradores
        admins = {admin.nombre_usuario for admin in Administrador.query.all()}
        
        resultados = []
        for cuenta in cuentas:
            rol = "Administrador" if cuenta.nombre_usuario in admins else "Usuario"
            resultados.append({
                "nombre_usuario": cuenta.nombre_usuario,
                "nombre": cuenta.nombre,
                "apellido": cuenta.apellido,
                "email": cuenta.email,
                "rol": rol
            })
        
        return jsonify({
            "success": True,
            "resultados": resultados,
            "total": len(resultados)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@cuentas_bp.route('/verificar-email', methods=['POST'])
def enviar_verificacion():
    try:
        data = request.get_json()
        nombre_usuario = data.get('usuario')

        # Buscar usuario
        usuario = Cuenta.query.filter_by(nombre_usuario=nombre_usuario).first()
        if not usuario:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'})

        # Revisar si ya está verificado
        if usuario.email_verificado:
            return jsonify({'success': False, 'error': 'El email ya está verificado'})

        # Generar token y enviar email
        token = generar_token_verificacion(usuario.nombre_usuario)
        enviar_email_verificacion(usuario.email, token, usuario.nombre)

        return jsonify({'success': True, 'message': 'Email de verificación enviado'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@cuentas_bp.route('/verificar-email/<token>')
def verificar_email(token):
    try:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        nombre_usuario = s.loads(token, salt='email-verification', max_age=86400)

        cuenta = Cuenta.query.filter_by(nombre_usuario=nombre_usuario).first()
        if not cuenta:
            return "Usuario no encontrado", 404

        if cuenta.email_verificado:
            return "El email ya fue verificado previamente."

        cuenta.email_verificado = True
        cuenta.fecha_verificacion = datetime.utcnow()
        db.session.commit()

        return """
            <h2>Email verificado correctamente</h2>
            <p>Tu cuenta ya está activa. Ya podés iniciar sesión.</p>
            <a href="/login">Ir al login</a>
        """
    except SignatureExpired:
        return "<h3>El enlace expiró. Pedí uno nuevo.</h3>"
    except Exception as e:
        return f"Error verificando token: {e}", 400

