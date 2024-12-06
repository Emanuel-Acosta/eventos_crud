from flask import render_template, redirect, request, flash, session, url_for
from flask_app.models.evento import Evento
from flask_app.models.usuario import Usuario
from datetime import datetime
from flask_app import app


@app.route('/nuevo_evento', methods=['GET', 'POST']) # Ruta para crear un nuevo evento
def nuevo_evento():
    if request.method == 'GET':
        return render_template('nuevo.html')
    
    if request.method == 'POST':
        # Crear diccionario con los datos del formulario
        data = {
            'nombre': request.form['nombre'],
            'ubicacion': request.form['ubicacion'],
            'fecha_inicio': request.form['fechaInicio'],
            'detalles': request.form['detalles'],
            'id_organizador': session['usuario_id']  # Desde la sesión
        }

        # Validar los datos
        errores = Evento.validar_evento(data)
        if errores:
            for error in errores:
                flash(error, 'error')
            return render_template('nuevo.html', data=data)

        # Crear el evento
        evento_id = Evento.crear(data)
        if evento_id:
            flash('evento creado exitosamente', 'success')
            return redirect(url_for('dashboard'))
        
        flash('Error al crear el evento', 'error')
        return render_template('nuevo.html', data=data)

@app.route('/ver_evento/<int:id>')# Ruta para ver un evento en detalle
def ver_evento(id):
    evento = Evento.obtener_por_id(id)
    if not evento:
        flash('evento no encontrado', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('ver_evento.html', evento=evento)

@app.route('/eliminar_evento/<int:id>')# Ruta para eliminar un evento
def eliminar_evento(id):
    if Evento.eliminar(id):
        flash('evento eliminado exitosamente', 'success')
    else:
        flash('Error al eliminar el evento', 'error')
    return redirect(url_for('dashboard'))


@app.route("/editar_evento/<int:id>")# Ruta para editar un evento
def editar_evento(id):
    if 'usuario_id' not in session:
        return redirect('/login')
    
    evento = Evento.obtener_por_id(id)
    if evento.id_organizador != session['usuario_id']:
        flash("No tienes permiso para editar este evento", "error") 
        return redirect(url_for('dashboard'))
    else:
        return render_template("editar_evento.html", data=evento)
    
@app.route("/actualizar_evento", methods=['GET', 'POST'])# Ruta para actualizar un evento
def actualizar_evento():
    if 'usuario_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        # Recoger los datos del formulario
        datos = {
            "id_evento": request.form['id'],
            'nombre': request.form['nombre'],
            "ubicacion": request.form['ubicacion'],
            "fecha_inicio": request.form['fechaInicio'],
            "detalles": request.form['detalles'],
        }

        # Validar los datos
        errores = Evento.validar_evento(datos)
        if errores:
            # Si hay errores, mostrar los mensajes y renderizar el formulario con los datos actuales
            for error in errores:
                flash(error, 'error')
            return render_template('editar_evento.html', data=datos)

        # Si no hay errores, proceder con la actualización
        Evento.actualizar(datos)

        flash("Evento actualizado exitosamente", "success")
        return redirect(url_for('dashboard'))

