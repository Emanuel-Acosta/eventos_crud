# modelos/evento.py
from flask_app.config.mysqlconnection import connectToMySQL
from datetime import datetime
from flask import flash

DATABASE = 'esquema_eventos'

class Evento:
    def __init__(self, data):
        self.id_evento = data['id_evento']
        self.nombre = data['nombre']
        self.ubicacion = data['ubicacion']
        self.fecha_inicio = data['fecha_inicio']
        self.detalles = data['detalles']
        self.id_organizador = data['id_organizador']
        self.fecha_creacion = data['fecha_creacion']
        self.fecha_actualizacion = data['fecha_actualizacion']
        self.organizador = data.get('organizador', None)  # Para joins con la tabla usuarios

    @classmethod
    def get_all(cls): # Método para obtener todos los eventos
        query = """
            SELECT v.*, u.nombre as organizador 
            FROM eventos v
            JOIN usuarios u ON v.id_organizador = u.id_usuario
            ORDER BY v.fecha_inicio;
        """
        results = connectToMySQL(DATABASE).query_db(query)
        eventos = []
        if results:
            for row in results:
                eventos.append(cls(row))
        return eventos
    
    
    @classmethod
    def crear(cls, data): # Método para crear un evento
        query = """
            INSERT INTO eventos (nombre, ubicacion, fecha_inicio, detalles, id_organizador)
            VALUES (%(nombre)s, %(ubicacion)s, %(fecha_inicio)s, %(detalles)s, %(id_organizador)s);
        """
        return connectToMySQL(DATABASE).query_db(query, data)

    @classmethod
    def actualizar(cls, data): # Método para actualizar un evento
        query = """
            UPDATE eventos 
            SET nombre = %(nombre)s,
                ubicacion = %(ubicacion)s,
                fecha_inicio = %(fecha_inicio)s,
                detalles = %(detalles)s
            WHERE id_evento = %(id_evento)s;
        """
        
        return connectToMySQL(DATABASE).query_db(query, data)


    @classmethod
    def obtener_por_id(cls, id_evento): # Método para obtener un evento por su id
        query = """
            SELECT v.*, u.nombre as organizador 
            FROM eventos v
            JOIN usuarios u ON v.id_organizador = u.id_usuario
            WHERE v.id_evento = %(id_evento)s;
        """
        data = {'id_evento': id_evento}
        results = connectToMySQL(DATABASE).query_db(query, data)
        return cls(results[0]) if results else None

    @classmethod
    def eliminar(cls, id_evento): # Método para eliminar un evento
        query1 = "DELETE FROM participantes_evento WHERE id_evento = %(id_evento)s;"
        query2 = "DELETE FROM eventos WHERE id_evento = %(id_evento)s;"
        data = {'id_evento': id_evento}
        connectToMySQL(DATABASE).query_db(query1, data)
        connectToMySQL(DATABASE).query_db(query2, data)
        return True

    @classmethod
    def obtener_por_organizador(cls, id_organizador): # Método para obtener los eventos de un organizador
        query = """
            SELECT v.*, u.nombre as organizador 
            FROM eventos v
            JOIN usuarios u ON v.id_organizador = u.id_usuario
            WHERE v.id_organizador = %(id_organizador)s
            ORDER BY v.fecha_inicio;
        """
        data = {'id_organizador': id_organizador}
        results = connectToMySQL(DATABASE).query_db(query, data)
        eventos = []
        if results:
            for row in results:
                eventos.append(cls(row))
        return eventos

    # Método para validar los datos del evento
    @staticmethod
    def validar_evento(data): 
        errores = []
        
        # Validar que los campos no estén vacíos
        if not data['ubicacion']:
            errores.append("La ubicacion es obligatoria")
        
        if not data['fecha_inicio']:
            errores.append("La fecha de inicio es obligatoria")
            
        if not data['detalles']:
            errores.append("Detalles es obligatorio")

        # Validar fechas
        fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%dT%H:%M')
        if fecha_inicio <= datetime.now():
            errores.append("La fecha de inicio debe ser una fecha futura")
        return errores
    
    @classmethod 
    def last_insert_id(cls): # Método para obtener el último id insertado
        return connectToMySQL(DATABASE).query_db("SELECT LAST_INSERT_ID() as id;")[0]['id']