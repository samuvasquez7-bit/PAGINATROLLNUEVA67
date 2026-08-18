from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error

# Inicializamos Flask apuntando a tus carpetas exactas
app = Flask(__name__, template_folder='Templates', static_folder='Static')

# Configuración de tu conexión a phpMyAdmin (XAMPP/WAMP por defecto)
db_config = {
    'host': 'localhost',
    'user': 'Crack123',      # Usuario por defecto de phpMyAdmin
    'password': '12345678',      # Normalmente en blanco en local
    'database': 'memepedia_db'
}

def crear_conexion():
    """Crea y retorna la conexión a la base de datos."""
    try:
        conexion = mysql.connector.connect(**db_config)
        return conexion
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
        # Capturamos los datos del formulario (los atributos 'name' del HTML)
        nombre = request.form.get('nombre')
        correo = request.form.get('correo')
        telefono = request.form.get('telefono')
        fecha_nac = request.form.get('fecha_nac')

        conexion = crear_conexion()
        if conexion:
            try:
                cursor = conexion.cursor()
                # Usamos %s para parametrizar y evitar Inyección SQL (¡Buenas prácticas!)
                sql = """INSERT INTO usuarios (nombre, correo, telefono, fecha_nac) 
                         VALUES (%s, %s, %s, %s)"""
                valores = (nombre, correo, telefono, fecha_nac)
                
                cursor.execute(sql, valores)
                conexion.commit() # Guardamos los cambios
                
                print("¡Usuario registrado con éxito!")
                # Redirigimos al index tras un registro exitoso
                return redirect(url_for('index'))
                
            except Error as e:
                print(f"Error al insertar datos: {e}")
            finally:
                # Siempre cerramos la conexión para no saturar el servidor
                if conexion.is_connected():
                    cursor.close()
                    conexion.close()
                    
    # Si el método es GET, simplemente mostramos el formulario
    return render_template('registro.html')

if __name__ == '__main__':
    app.run(debug=True)