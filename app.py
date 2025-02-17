# from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
# import os
# from werkzeug.utils import secure_filename
# import sqlite3

# app = Flask(__name__, template_folder='templates')
# app.secret_key = 'demo_secret_key'

# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# def get_db_connection():
#     conn = sqlite3.connect('users.db')
#     conn.row_factory = sqlite3.Row
#     return conn

# def init_db():
#     conn = get_db_connection()
#     conn.execute('''CREATE TABLE IF NOT EXISTS users
#                     (username TEXT PRIMARY KEY, password TEXT, firstname TEXT, lastname TEXT, email TEXT, filename TEXT, word_count INTEGER)''')
#     conn.commit()
#     conn.close()

# def count_words(text):
#     words = text.split()
#     return len(words)

# @app.route('/')
# def home():
#     return render_template('home.html')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         firstname = request.form['firstname']
#         lastname = request.form['lastname']
#         email = request.form['email']

#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

#         if user:
#             flash('Username already exists. Choose a different one.')
#             return redirect(url_for('register'))

#         file = request.files['file']
#         filename = None
#         word_count = 0

#         if file and file.filename != '':
#             filename = secure_filename(file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(file_path)

#             with open(file_path, 'r') as file_content:
#                 text_content = file_content.read()
#                 word_count = count_words(text_content)

#         conn.execute('INSERT INTO users (username, password, firstname, lastname, email, filename, word_count) VALUES (?, ?, ?, ?, ?, ?, ?)',
#                      (username, password, firstname, lastname, email, filename, word_count))
#         conn.commit()
#         conn.close()

#         flash('Registration successful. Please log in.')
#         return redirect(url_for('login'))

#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         conn = get_db_connection()
#         user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
#         conn.close()

#         if user:
#             session['username'] = username
#             return redirect(url_for('profile'))
#         else:
#             flash('Invalid username or password.')

#     return render_template('login.html')

# @app.route('/profile')
# def profile():
#     if 'username' not in session:
#         return redirect(url_for('login'))

#     conn = get_db_connection()
#     user = conn.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchone()
#     conn.close()

#     return render_template('profile.html', user=user)

# @app.route('/logout')
# def logout():
#     session.pop('username', None)
#     return redirect(url_for('home'))

# @app.route('/download/<username>')
# def download(username):
#     conn = get_db_connection()
#     user = conn.execute('SELECT filename FROM users WHERE username = ?', (username,)).fetchone()
#     conn.close()

#     if user and user['filename']:
#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], user['filename'])
#         return send_file(file_path, as_attachment=True)
#     else:
#         flash('No file found.')
#         return redirect(url_for('profile'))

# if __name__ == '__main__':
#     init_db()
#     os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
import os
import re
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__, template_folder='templates')
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY, 
                        password TEXT, 
                        firstname TEXT, 
                        lastname TEXT, 
                        email TEXT
                    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        filename TEXT,
                        word_count INTEGER,
                        FOREIGN KEY (username) REFERENCES users(username)
                    )''')
    conn.commit()
    conn.close()

def count_words(text):
    words = text.split()
    return len(words)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        email = request.form['email']

        # Basic validation
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            flash('Username can only contain letters, numbers, and underscores.')
            return redirect(url_for('register'))
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            flash('Invalid email format.')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('Password must be at least 6 characters long.')
            return redirect(url_for('register'))

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user:
            flash('Username already exists. Choose a different one.')
            return redirect(url_for('register'))

        conn.execute('INSERT INTO users (username, password, firstname, lastname, email) VALUES (?, ?, ?, ?, ?)',
                     (username, password, firstname, lastname, email))
        conn.commit()
        conn.close()

        flash('Registration successful. Please log in.')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()

        if user:
            session['username'] = username
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (session['username'],)).fetchone()
    files = conn.execute('SELECT * FROM files WHERE username = ?', (session['username'],)).fetchall()
    conn.close()

    return render_template('profile.html', user=user, files=files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))

    file = request.files['file']
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Only count words if the file is a text file
        try:
            with open(file_path, 'r', encoding='utf-8') as file_content:
                text_content = file_content.read()
                word_count = count_words(text_content)
        except UnicodeDecodeError:
            flash("Uploaded file is not a valid text file. Word count not calculated.")
            word_count = None  # Do not count words for non-text files

        conn = get_db_connection()
        conn.execute('INSERT INTO files (username, filename, word_count) VALUES (?, ?, ?)',
                     (session['username'], filename, word_count))
        conn.commit()
        conn.close()

        flash('File uploaded successfully.')

    return redirect(url_for('profile'))


@app.route('/download/<int:file_id>')
def download(file_id):
    conn = get_db_connection()
    file_entry = conn.execute('SELECT filename FROM files WHERE id = ?', (file_id,)).fetchone()
    conn.close()

    if file_entry:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_entry['filename'])
        return send_file(file_path, as_attachment=True)
    else:
        flash('File not found.')
        return redirect(url_for('profile'))

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))

if __name__ == '__main__':
    init_db()
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
