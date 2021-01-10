from flask import make_response, jsonify
from app import app

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': '404: Not Found (Не найдено)'}), 404)

@app.errorhandler(401)
def unauthorized(error):
    return make_response(jsonify({'error': '401: Unauthorized (Неавторизован)'}), 401)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': '400: Bad Request (Плохой запрос)'}), 400)
