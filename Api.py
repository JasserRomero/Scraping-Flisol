from flask import Flask, jsonify, request
import re
from ScrapingTransito import Prueba

app = Flask(__name__)
@app.route('/', methods=['GET'])
def inicio():
    return jsonify({'mensaje': 'Bienvenido a la API de comparendos de la ciudad de Barranquilla'}), 200

# Ruta para obtener un vehículo por su placa
@app.route('/api/vehiculos/<placa>', methods=['GET'])
def obtener_vehiculo(placa):
    ExpresionRegular = r'((^[a-zA-Z]{3}\d{3}|[SRsr]{1}\d{5}|[a-zA-Z]{3}\d{2}[a-zA-Z]{1})$)'
    if not re.match(ExpresionRegular, placa):
        return jsonify({'mensaje': 'Placa no valida'}), 400
    else:
        prueba = Prueba(placa=placa)
        Soup = prueba.Peticion()
        ComparendosFisicos, ComparendosElectronicos = prueba.obtener_informacion(Soup)
        return jsonify( ComparendosFisicos,  ComparendosElectronicos), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)

