from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import jwt
from functools import wraps
import logging
import os
from keycloak import KeycloakOpenID

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

access_role = 'prothetic_user'

def check_token(token):
    keycloak_openid = KeycloakOpenID(server_url=os.getenv('PYTHON_APP_KEYCLOAK_URL'),
                                 client_id=os.getenv('PYTHON_APP_KEYCLOAK_CLIENT_ID'),
                                 realm_name=os.getenv('PYTHON_APP_KEYCLOAK_REALM'),
                                 client_secret_key=os.getenv('PYTHON_APP_KEYCLOAK_SECRET_KEY'))
    try:
        token_info = keycloak_openid.introspect(token)
    except Exception as e:
        logger.info(f'Error with token {e}')
        return False
    roles = token_info['realm_access']['roles']
    status = token_info['active']
    logger.info(f'Token {str(status)} from user with role {str(roles)}')
    if access_role in roles and status:
        logger.info('Good role')
        return True
    logger.info('Bad Role')    
    return False

@app.route('/reports', methods=['GET'])
def get_reports():
    # Получаем токен из заголовка Authorization
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({'error': 'Authorization header is missing'}), 401
    token = auth_header.split(" ")[1]  # Извлекаем токен
    # Валидация токена
    token_info = check_token(token)
    if not token_info:
        return jsonify({'error': 'Invalid token or role'}), 401
    reports = [
        {"id": 1, "title": "Report 1", "content": "Content of report 1"},
        {"id": 2, "title": "Report 2", "content": "Content of report 2"},
        {"id": 3, "title": "Report 3", "content": "Content of report 3"},
    ]
    return jsonify(reports)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9090, debug=True)