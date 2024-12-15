from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

# Configuración de la base de datos
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Dtrr'
app.config['MYSQL_PASSWORD'] = 'MCPE1234'
app.config['MYSQL_DB'] = 'tienda'

# Configuración de carga de imágenes
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Crear carpeta de carga si no existe
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Verificar extensiones permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Conexión a la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host=app.config['MYSQL_HOST'],
        user=app.config['MYSQL_USER'],
        password=app.config['MYSQL_PASSWORD'],
        database=app.config['MYSQL_DB']
    )

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', productos=productos)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar_producto():
    if request.method == 'POST':
        # Validar datos
        nombre = request.form['nombre']
        try:
            precio = float(request.form['precio'])
        except ValueError:
            return "El precio debe ser un número válido.", 400

        imagen = request.files['imagen']
        if not (imagen and allowed_file(imagen.filename)):
            return "Archivo no válido. Solo se permiten imágenes.", 400

        # Guardar imagen
        filename = secure_filename(imagen.filename)
        ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        imagen.save(ruta_imagen)

        # Insertar en base de datos
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO productos (nombre, precio, ruta_imagen) VALUES (%s, %s, %s)',
                           (nombre, precio, ruta_imagen))
            conn.commit()
        except mysql.connector.Error as e:
            return f"Error al guardar en la base de datos: {e}", 500
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('index'))

    return render_template('agregar.html')

if __name__ == '__main__':
    app.run(debug=True)
