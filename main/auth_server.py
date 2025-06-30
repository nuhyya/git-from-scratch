from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt, datetime, os, sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecret'
DB = 'users.db'


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                 id INTEGER PRIMARY KEY,
                 username TEXT UNIQUE,
                 email TEXT,
                 password TEXT)''')
    conn.commit()
    conn.close()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    hashed_pw = generate_password_hash(data['password'])
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                  (data['username'], data['email'], hashed_pw))
        conn.commit()
        return jsonify({"msg": "User created"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "User exists"}), 409
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (data['username'],))
    row = c.fetchone()
    conn.close()
    if row and check_password_hash(row[0], data['password']):
        token = jwt.encode({
            'user': data['username'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, app.config['SECRET_KEY'], algorithm="HS256")
        return jsonify({"token": token})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route('/repos/<user>', methods=['GET'])
def view_repo(user):
    token = request.headers.get('Authorization')
    try:
        decoded = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        if decoded['user'] != user:
            return jsonify({"error": "Access denied"}), 403
        return jsonify({"repos": ["repo1", "repo2"]})
    except Exception:
        return jsonify({"error": "Invalid or expired token"}), 401

if __name__ == '__main__':
    init_db()
    app.run(port=5000)

