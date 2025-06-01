import os

from flask import request,jsonify

TOKEN_FILE = "data/apitoken.txt"
ADMIN_PASS_FILE = "data/adminpass.txt"

def get_api_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return os.environ.get("NOSQL_API_TOKEN", "supersecrettoken123")

def set_api_token(new_token):
    with open(TOKEN_FILE, "w") as f:
        f.write(new_token)

def get_admin_password():
    if os.path.exists(ADMIN_PASS_FILE):
        with open(ADMIN_PASS_FILE, "r") as f:
            return f.read().strip()
    return os.environ.get("FILLADB_ADMIN_PASSWORD", "adminpass")

def set_admin_password(new_pass):
    with open(ADMIN_PASS_FILE, "w") as f:
        f.write(new_pass)

def token_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Always reload token (in case admin changed it)
        token = get_api_token()
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid Authorization header'}), 401
        supplied = auth.split(' ', 1)[1]
        if supplied != token:
            return jsonify({'error': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return wrapper