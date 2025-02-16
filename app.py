from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']
        address = request.form['address']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user:
            flash('Username already exists')
            return redirect(url_for('register'))

        conn.execute('INSERT INTO users (username, password, firstname, lastname, email, address) VALUES (?, ?, ?, ?, ?, ?)',
                     (username, password, firstname, lastname, email, address))
        conn.commit()
        conn.close()

        # Handle file upload
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            
            with open(file_path, 'r') as f:
                word_count = len(f.read().split())
            
            conn = get_db_connection()
            conn.execute('UPDATE users SET filename = ?, word_count = ? WHERE username = ?', (filename, word_count, username))
            conn.commit()
            conn.close()

        return redirect(url_for('profile', username=username))

    return render_template('register.html')

@app.route('/profile/<username>')
def profile(username):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    return render_template('profile.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        if user:
            return redirect(url_for('profile', username=username))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/download/<username>')
def download(username):
    conn = get_db_connection()
    user = conn.execute('SELECT filename FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if user and user['filename']:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], user['filename']), as_attachment=True)
    else:
        flash('No file found')
        return redirect(url_for('profile', username=username))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)

