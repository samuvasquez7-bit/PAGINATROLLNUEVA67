import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'clave_secreta_memepedia_retro'

# Configuración dinámica para producción (Render/CleverCloud) y local
db_config = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'Crack123'),
    'password': os.environ.get('DB_PASSWORD', '12345678'),
    'database': os.environ.get('DB_NAME', 'memepedia_db')
}

def crear_conexion():
    try:
        return mysql.connector.connect(**db_config)
    except Error as e:
        print(f"Error conectando a MySQL: {e}")
        return None

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/registro.html', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        telefono = request.form.get('telefono')
        fecha_nac = request.form.get('fecha_nac')

        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "INSERT INTO usuarios (nombre, correo, telefono, fecha_nac) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (nombre, correo, telefono, fecha_nac))
                conexion.commit()
                return redirect(url_for('login'))
            except Error as e:
                print(f"Error al registrar usuario: {e}")
            finally:
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
    return render_template('registro.html')

# --- AUTENTICACIÓN Y SESIONES ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
                user = cursor.fetchone()
                if user:
                    session['user_id'] = user['id']
                    session['nombre'] = user['nombre']
                    session['rol'] = user['rol']
                    if user['rol'] == 'admin':
                        return redirect(url_for('admin_panel'))
                    return redirect(url_for('index'))
                else:
                    flash("Correo no encontrado. Por favor regístrate primero.")
            finally:
                cursor.close()
                conexion.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# --- PANEL ADMINISTRADOR Y CRUD ---
@app.route('/admin')
@app.route('/admin.html')
def admin_panel():
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))
    
    conexion = crear_conexion()
    usuarios = []
    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios")
            usuarios = cursor.fetchall()
        finally:
            cursor.close()
            conexion.close()
    return render_template('admin.html', usuarios=usuarios)

@app.route('/admin/eliminar/<int:id>')
def eliminar_usuario(id):
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))
    
    conexion = crear_conexion()
    if conexion:
        try:
            cursor = conexion.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
            conexion.commit()
        finally:
            cursor.close()
            conexion.close()
    return redirect(url_for('admin_panel'))

@app.route('/admin/editar/<int:id>', methods=['GET', 'POST'])
@app.route('/editar_usuario.html/<int:id>', methods=['GET', 'POST'])
def editar_usuario(id):
    if session.get('rol') != 'admin':
        return redirect(url_for('login'))
    
    conexion = crear_conexion()
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        telefono = request.form.get('telefono')
        rol = request.form.get('rol')
        
        if conexion:
            try:
                cursor = conexion.cursor()
                sql = "UPDATE usuarios SET nombre=%s, correo=%s, telefono=%s, rol=%s WHERE id=%s"
                cursor.execute(sql, (nombre, correo, telefono, rol, id))
                conexion.commit()
                return redirect(url_for('admin_panel'))
            finally:
                cursor.close()
                conexion.close()

    if conexion:
        try:
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
            usuario = cursor.fetchone()
            return render_template('editar_usuario.html', usuario=usuario)
        finally:
            cursor.close()
            conexion.close()
            
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True)
