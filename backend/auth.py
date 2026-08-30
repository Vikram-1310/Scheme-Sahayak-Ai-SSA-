import hashlib
import os
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
import jwt

DATABASE_FILE = Path(__file__).resolve().parent.parent / 'data' / 'scheme_sahayak.db'
SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'SIH26092-local-development-secret-change-me')
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def get_connection():
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    return connection

def initialize_auth_table():
    connection = get_connection()
    connection.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'beneficiary',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    connection.commit(); connection.close()

def hash_password(password):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
    return f'{salt}${digest}'

def verify_password(password, stored_password):
    try:
        salt, password_hash = stored_password.split('$', 1)
        digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex()
        return secrets.compare_digest(digest, password_hash)
    except ValueError:
        return False

def create_user(username, password, role='beneficiary'):
    connection = get_connection()
    try:
        cur = connection.execute('INSERT INTO users(username,password_hash,role) VALUES (?,?,?)', (username, hash_password(password), role))
        connection.commit()
        return {'id': cur.lastrowid, 'username': username, 'role': role}
    except sqlite3.IntegrityError:
        return None
    finally:
        connection.close()

def get_user(username):
    connection = get_connection()
    row = connection.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
    connection.close()
    return dict(row) if row else None

def get_user_by_id(user_id):
    connection = get_connection()
    row = connection.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
    connection.close()
    return dict(row) if row else None

def create_access_token(user_id, username, role):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({'sub': str(user_id), 'username': username, 'role': role, 'exp': expire}, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('sub') is None: return None
        return payload
    except jwt.PyJWTError:
        return None
