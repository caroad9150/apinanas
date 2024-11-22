import random
from flask import Flask, jsonify, request, send_from_directory
import pyodbc 
import requests 
# from pymongo import MongoClient # type: ignore
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)  # Esto permitirá solicitudes desde cualquier origen
# Configuración de la conexión a la base de datos
# server = 'DESKTOP-MTPAL4V'
# database = 'progra5'
# connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'
# Nuevos datos de conexión
server = 'tiusr3pl.cuc-carrera-ti.ac.cr.\MSSQLSERVER2019'  
database = 'tiusr3pl_'
username = 'nanas'
password = 'Nanasp24.'  
# Actualizando la cadena de conexión
connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password};'


# actualizar precio
@app.route('/actualizar_precio', methods=['POST'])
def actualizar_precio():
    data = request.json
    nombre = data.get('nombre')
    precio = data.get('precio')

    if not nombre or not precio:
        return jsonify({"mensaje": "Nombre y precio son requeridos"}), 400

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        query = "EXEC mantenproductos @op='cambiar', @nombre=?, @precio=?"
        cursor.execute(query, (nombre, precio))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()

        if rows_affected > 0:
            return jsonify({"mensaje": "Se han modificado el precio correctamente"})
        else:
            return jsonify({"mensaje": "Hubo un error, vuelve a intentar más tarde"}), 500
    except Exception as ex:
        print(str(ex))
        return jsonify({"mensaje": "Hubo un error, vuelve a intentar más tarde"}), 500
#api tse y registro 
@app.route('/verificar_registro', methods= ['POST']) 
def verificar_registro():
    data = request.json
    id = data.get('id')
    nombre = data.get('nombre')
    cel = data.get('cel')
    correo = data.get('correo')
    direccion = data.get('direccion')
    clave = data.get('clave')
    pregunta = data.get('pregunta')
    respuesta = data.get('respuesta')

    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # # Verificar si la cédula existe en la tabla tse
        # cursor.execute("SELECT idcliente FROM tse WHERE idcliente = ?", id)
        # tse_result = cursor.fetchone()

        # if not tse_result:
        #     return jsonify({"mensaje": "Cédula no existente."}), 400

        # Proceder con el registro si la cédula existe
        token = random.randint(100000, 999999)

        query = """
        EXEC mantenclientes
            @op='registro',
            @id=?,
            @nombre=?,
            @cel=?,
            @correo=?,
            @direccion=?,
            @clave=?,
            @token=?,
            @tipo='cliente',
            @estado='a',
            @pregunta=?,
            @respuesta=?,
            @ip=?,
            @buscador=?
        """
        cursor.execute(query, (id, nombre, cel, correo, direccion, clave, token, pregunta, respuesta, request.remote_addr, request.user_agent.browser))
        conn.commit()
        rows_affected = cursor.rowcount
        conn.close()

        if rows_affected > 0:
            return jsonify({"mensaje": "Se ha ingresado correctamente", "token": token})
        else:
            return jsonify({"mensaje": "Hubo un error, vuelve a intentar más tarde"}), 500

    except Exception as ex:
        print(str(ex))
        return jsonify({"mensaje": "Hubo un error, vuelve a intentar más tarde"}), 500
#api agregar al carrito 
@app.route('/add-carritorepos', methods=['POST'])
def add_carritorepos():
    try:
        data = request.json
        idcliente = data['idcliente']
        productos = data['productos']
        cantidad = data['cantidad']
        ip = request.remote_addr
        buscador = request.user_agent.browser

        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()

            query = """
            EXEC mantenrepos @op = 'nuevo', @idpedido = '', @idcliente = ?, @productos = ?, @cantidad = ?, @precio = '', @estado = 'pendiente', @ip = ?, @buscador = ?
            """
            cursor.execute(query, (idcliente, productos, cantidad, ip, buscador))
            conn.commit()

            select_query = """
            SELECT TOP 1 idpedido, idcliente, productos, cantidad, precio, total, estado 
            FROM reposteria 
            WHERE idcliente = ? 
            ORDER BY idpedido DESC
            """
            cursor.execute(select_query, (idcliente,))
            row = cursor.fetchone()

            if row:
                response = {
                    "idpedido": row.idpedido,
                    "idcliente": row.idcliente,
                    "productos": row.productos,
                    "cantidad": row.cantidad,
                    "precio": row.precio,
                    "total": row.total,
                    "estado": row.estado
                }
                return jsonify(response), 200
            else:
                return jsonify({"mensaje": "Hubo un error, vuelve a intentar más tarde"}), 500

    except Exception as e:
        print(e)
        return jsonify({"mensaje": "Hubo un error, vuelve a intentar más tarde"}), 500   
    
#api agregar al carrito caterin
@app.route('/add-carritocate', methods=['POST'])
def add_carritocate():
    try:
        data = request.json
        idcliente = data.get('idcliente')
        degustacion = data.get('degustacion')
        fech_hora_degus = data.get('fech_hora_degus')
        direc = data.get('direc')
        fechaevento = data.get('fechaevento')
        hora = data.get('hora')
        paquete = data.get('paquete')
        precio = data.get('precio')
        ip = request.remote_addr
        buscador = request.user_agent.browser

        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()

            query = """
            EXEC mantencaterin @op = 'nuevo', @idcate = '', @idcliente = ?, @degustacion = ?, @fech_hora_degus = ?, @direc= ?, @fechaevento= ?, @hora= ?, @paquete= ?, @precio= ?, @ip=?, @buscador=?
            """
            cursor.execute(query, (idcliente, degustacion, fech_hora_degus, direc, fechaevento, hora, paquete, precio, ip, buscador))
            conn.commit()

            response = {
                'message': 'Agregado al carrito con éxito'
            }
            return jsonify(response), 200
    except Exception as e:
        print(e)
        response = {
            'message': 'Hubo un error, vuelve a intentar más tarde'
        }
        return jsonify(response), 500



 #api encargo personalizado
@app.route('/confir-encargo', methods=['POST'])
def confir_encargo():
    data = request.json

    idcliente = data['idcliente']
    sabor = data['sabor']
    porciones = data['porciones']
    cobertura = data['cobertura']
    colorcobertura = data['colorcobertura']
    fecha = data['fecha']
    hora = data['hora']
    domicilio = data['domicilio']
    direccion = data['direccion']
    ip = data['ip']
    buscador = data['buscador']
   
    try:
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()
                query = """
                 mantenperosnalizado @op = 'nuevo', @idperso = '', @idcliente = ?, @sabor = ?, @porciones = ?, @cobertura = ?, @colorcobertura = ?, @fecha = ?, @hora = ?, @domicilio = ?, @direccion = ?, @total = '', @ip = ?, @buscador = ?
                """
                cursor.execute(query, idcliente, sabor, porciones, cobertura, colorcobertura, fecha, hora, domicilio, direccion, ip, buscador)
                conn.commit()
            
            response = {
                'message': 'Agregado al carrito con éxito'
            }
    except Exception as e:
        print(e)
        response = {
            'message': 'Hubo un error, vuelve a intentar más tarde'
        }

    return jsonify(response)
#api personal del token
@app.route('/generate-token', methods=['GET'])
def generate_token():
    token = random.randint(100000, 999999)
    return jsonify({"token": token})

api_key = "1AA2AAAI3A"
@app.route('/tipo-cambio', methods=['GET'])
def obtener_tipo_cambio():
    url = "https://gee.bccr.fi.cr/Indicadores/Suscripciones/WS/wsindicadoreseconomicos.asmx/ObtenerIndicadoresEconomicos"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": f"HTTP error occurred: {http_err}"}), 500
    except requests.exceptions.RequestException as req_err:
        return jsonify({"error": f"Error occurred: {req_err}"}), 500

    try:
        data = response.json()
        tipo_cambio = data.get("venta")
        if tipo_cambio is not None:
            return jsonify({"tipo_cambio": tipo_cambio})
        else:
            return jsonify({"error": "El campo 'venta' no está en la respuesta"}), 500
    except ValueError as json_err:
        return jsonify({"error": f"Error al parsear JSON: {json_err}"}), 500
# api banco 
@app.route('/pagar', methods=['POST'])
def pagar():
    data = request.get_json()
    numero_tarjeta = data.get('numero_tarjeta')
    monto = data.get('monto')
    idcliente = data.get('idcliente')  # Añadido para el uso en el procedimiento almacenado

    if not numero_tarjeta or monto is None or not idcliente:
        return jsonify({"error": "Número de tarjeta, monto e idcliente son requeridos"}), 400

    try:
        # Conectar a la base de datos de SQL Server
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "EXEC mantenrepos @op = 'pagar', @idpedido = '', @idcliente = ?, @productos = '', @cantidad = '', @precio='', @estado='';",
                (idcliente,)
            )
            conn.commit()

            # Ejecutar el procedimiento almacenado
            cursor.execute(
                "EXEC realizarPago @numerotarjeta = ?, @monto = ?, @idcliente = ?",
                numero_tarjeta, monto, idcliente
            )
            conn.commit()

        return jsonify({"message": "Pago realizado con éxito"}), 200

    except pyodbc.Error as e:
        # Capturar errores específicos de SQL Server
        sqlstate = e.args[1]
        if 'Número de tarjeta o cliente no encontrado' in sqlstate:
            return jsonify({"error": "Número de tarjeta o cliente no encontrado"}), 404
        elif 'No se puede realizar el pago por falta de fondos' in sqlstate:
            return jsonify({"error": "Monto excede los fondos disponibles"}), 400
        else:
            return jsonify({"error": f"Error al procesar el pago: {str(e)}"}), 500

    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"message": "Server is running!"})

if __name__ == '__main__':
    app.run(port=5000)