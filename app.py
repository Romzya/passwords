from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'aboltus_key' 

def init_db():
    conn = sqlite3.connect('passwords.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS user_passwords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            site TEXT NOT NULL,
            login TEXT NOT NULL,
            password TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('passwords.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    passwords = conn.execute('''
        SELECT * FROM user_passwords 
        WHERE user_id = ? 
        ORDER BY site
    ''', (session['user_id'],)).fetchall()
    conn.close()
    
    return render_template('index.html', 
                         passwords=passwords, 
                         username=session['username'])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username and password:
            conn = get_db_connection()
            try:
                hashed_password = generate_password_hash(password)
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                           (username, hashed_password))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                error = 'Пользователь с таким именем уже существует'
                return render_template('register.html', error=error)
            finally:
                conn.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            error = 'Неверное имя пользователя или пароль'
            return render_template('login.html', error=error)
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/add', methods=['POST'])
def add_password():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    site = request.form['site']
    login = request.form['login']
    password = request.form['password']
    
    if site and login and password:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO user_passwords (user_id, site, login, password) 
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], site, login, password))
        conn.commit()
        conn.close()
    
    return redirect(url_for('index'))

@app.route('/delete/<int:password_id>')
def delete_password(password_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    conn.execute('DELETE FROM user_passwords WHERE id = ? AND user_id = ?', 
                (password_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5123)