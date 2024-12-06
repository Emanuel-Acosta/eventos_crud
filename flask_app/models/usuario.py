from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
NOMBRE_REGEX = re.compile(r'^[a-zA-Z\s]+$')
PASSWORD_REGEX = re.compile(r'^(?=.{8,})(?=.*[a-z])(?=.*[0-9])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$')

DATABASE = 'esquema_eventos'


class Usuario:
    def __init__(self, data):
        self.id = data['id_usuario']
        self.nombre = data['nombre']
        self.apellido = data['apellido']
        self.email = data['email']
        self.password = data['password']

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM usuarios;"
        resultados = connectToMySQL(DATABASE).query_db(query)
        usuarios = []
        for usuario in resultados:
            usuarios.append(cls(usuario))
        return usuarios

    @classmethod
    def save(cls, data):
        query = """
        INSERT INTO usuarios (nombre, apellido, email, password, fecha_creacion , fecha_actualizacion) 
        VALUES (%(nombre)s, %(apellido)s, %(email)s, %(password)s, NOW(), NOW());
        """
        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def get_by_email(cls, email):
        query = "SELECT * FROM usuarios WHERE email = %(email)s;"
        resultado = connectToMySQL(DATABASE).query_db(query, {'email': email})
        if len(resultado) < 1:
            return False
        return cls(resultado[0])

    @classmethod
    def get_by_id(cls, id):
        query = "SELECT * FROM usuarios WHERE id_usuario = %(id)s;"
        resultado = connectToMySQL(DATABASE).query_db(query, {'id': id})
        if not resultado:
            return False
        return cls(resultado[0])

    @staticmethod
    def validar_usuario(usuario):
        is_valid = True
    
        # VALIDACION NOMBRE
        if len(usuario['nombre']) <= 0:
            flash("El nombre no puede estar vacío.", "danger")
            is_valid = False
        elif len(usuario['nombre']) < 2:
            flash("El nombre debe tener al menos 2 caracteres.", "danger")
            is_valid = False
        else:
            if not NOMBRE_REGEX.match(usuario['nombre']):
                flash("El nombre solo puede contener letras.", "danger")
                is_valid = False
        
        # VALIDACION APELLIDO
        if is_valid:  # Solo se valida el apellido si el nombre es válido
            if len(usuario['apellido']) < 2:
                flash("El apellido debe tener al menos 2 caracteres.", "danger")
                is_valid = False
            elif not NOMBRE_REGEX.match(usuario['apellido']):  
                flash("El apellido solo puede contener letras.", "danger")
                is_valid = False
    
        # VALIDACION EMAIL
        if is_valid:  # Solo validamos el email si el nombre y apellido son válidos
            if not EMAIL_REGEX.match(usuario['email']):
                flash("Email inválido.", "danger")
                is_valid = False
            
            # Verificamos si el email ya está registrado en la base de datos
            if is_valid:
                query = "SELECT * FROM usuarios WHERE email = %(email)s;"
                data = {'email': usuario['email']}
                resultado = connectToMySQL(DATABASE).query_db(query, data)
                if len(resultado) > 0:
                    flash("El email ya está registrado.", "danger")
                    is_valid = False
    
        # VALIDACION PASSWORD
        if is_valid:  # Solo si todas las validaciones anteriores son correctas
            if len(usuario['password']) < 8:
                flash("La contraseña debe tener al menos 8 caracteres.", "danger")
                is_valid = False
            elif not PASSWORD_REGEX.match(usuario['password']):
                flash("La contraseña debe contener al menos una letra mayúscula, una letra minúscula, un número y un caracter especial.", "danger")
                is_valid = False
            elif len(usuario['password']) <= 0:
                flash("La contraseña no puede estar vacía.", "danger")
                is_valid = False
    
        # VALIDACION CONFIRMACION PASSWORD
        if is_valid:  # Solo si la contraseña es válida
            if len(usuario['confirmPassword']) <= 0:
                flash("La confirmación de la contraseña no puede estar vacía.", "danger")
                is_valid = False
            elif usuario['password'] != usuario['confirmPassword']:
                flash("Las contraseñas no coinciden.", "danger")
                is_valid = False
    
        # Mensaje de éxito si todas las validaciones fueron correctas
        if is_valid:
            flash("Registro exitoso.", "success")
        
        return is_valid
