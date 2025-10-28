from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'im_gay'

# Инициализация базы данных
conn = sqlite3.connect('my_database.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS Users (
id INTEGER PRIMARY KEY,
username TEXT NOT NULL,
password TEXT NOT NULL
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS BOB (
id INTEGER PRIMARY KEY,
Site TEXT NOT NULL,
Login TEXT NOT NULL,
Password TEXT NOT NULL
)
''')

conn.commit()
conn.close()

@app.route('/')
def index():
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')  # Исправлено
        password = request.form.get('password')  # Исправлено

        try:
            with sqlite3.connect('my_database.db') as conn:
                c = conn.cursor()        
                c.execute('INSERT INTO Users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
            return redirect('/login')
        except:
            return render_template('register.html', error='Ошибка регистрации')

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')  # Исправлено
        password = request.form.get('password')  # Исправлено

        with sqlite3.connect('my_database.db') as conn:
            c = conn.cursor()        
            c.execute('SELECT id FROM Users WHERE username = ? AND password = ?', (username, password))
            user = c.fetchone()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = username
            return redirect('/index')
        else:
            return render_template('login.html', error='Неверные данные')

    return render_template('login.html')

@app.route('/add', methods=['POST'])
def add_password():
    if 'user_id' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        Site = request.form.get('Site')  # Исправлено
        Login = request.form.get('Login')  # Исправлено
        Password = request.form.get('Password')  # Исправлено
        
        try:
            with sqlite3.connect('my_database.db') as conn:
                c = conn.cursor()
                c.execute("INSERT INTO BOB (Site, Login, Password) VALUES (?, ?, ?)", (Site, Login, Password))
                conn.commit()
            return redirect('/index')
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return render_template('index.html', error='Ошибка базы данных')
    
    return redirect('/index')

@app.route('/index')
def passwords():
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('my_database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM BOB")
    passwords = c.fetchall()
    conn.commit()
    conn.close()
    
    return render_template('index.html', 
                         passwords=passwords, 
                         username=session['username'])

@app.route('/delete/<int:password_id>')
def delete_password(password_id):
    if 'user_id' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('my_database.db')
    c = conn.cursor()
    c.execute("DELETE FROM BOB WHERE id = ?", (password_id,))  # Исправлено здесь
    conn.commit()
    conn.close()
    
    return redirect('/index')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5123)