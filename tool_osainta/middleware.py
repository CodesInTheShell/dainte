from flask import request, flash, redirect, url_for, jsonify
from functools import wraps
import jwt
from models.users import User
import os

OSAINTA_SECRET_KEY = os.environ.get('OSAINTA_SECRET_KEY')
MAX_CALLS_PER_DAY = 30


def get_current_user():
    token = request.cookies.get('access_token')
    if not token:
        return None
    try:
        payload = jwt.decode(token, OSAINTA_SECRET_KEY, algorithms=['HS256'])
        return User.find_by_username(payload['sub'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            flash('You need to log in first.')
            return redirect(url_for('login'))
        return f(user, *args, **kwargs)
    return decorated_function

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        
        if not user.check_rate_limit(MAX_CALLS_PER_DAY):
            return jsonify({'status': 'error', 'message': 'Rate limit exceeded'}), 429
        
        return f(*args, **kwargs)
    return decorated_function

def token_available_check(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401
        
        if user.tokenAvailable < 1:
            return jsonify({'status': 'error', 'message': 'You do not have enough token'}), 429
        
        return f(*args, **kwargs)
    return decorated_function