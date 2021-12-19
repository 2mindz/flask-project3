import sqlite3
import imghdr
import os
from flask import Flask, render_template, request, url_for, flash, redirect, send_file
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = '12349K2_!4'
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.txt', '.exe', '.pdf', '.docx']
app.config['UPLOAD_PATH'] = 'uploads'


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return render_template('index.html', posts=posts)

@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template('post.html', post=post)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('create.html')

@app.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            conn = get_db_connection()
            conn.execute('UPDATE posts SET title = ?, content = ?'
                         ' WHERE id = ?',
                         (title, content, id))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))

    return render_template('edit.html', post=post)

@app.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash('"{}" was successfully deleted!'.format(post['title']))
    return redirect(url_for('index'))

@app.route('/files', defaults={'req_path': ''})
@app.route('/<path:req_path>')
def get_files(req_path):
    #https://stackoverflow.com/questions/23718236/python-flask-browsing-through-directory-with-files   Code Snippet provided by vivekagr
    BASE_DIR = '/home/ubuntu/blog/uploads'
    # Joining the base and the requested path
    abs_path = os.path.join(BASE_DIR, req_path)

    # Return 404 if path doesn't exist
    if not os.path.exists(abs_path):
        return abort(404)

    # Check if path is a file and serve
    if os.path.isfile(abs_path):
        return send_file(abs_path) 

    # Show directory contents
    files = os.listdir(abs_path)
    return render_template('files.html', files=files)

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(uploaded_file.filename)
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            #abort(400)
            return "Upload Rejected!!!"
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))
    return render_template('upload.html')

@app.route('/register', methods=['GET','POST'])
def register():
    email = request.form.get("email")
    username = request.form.get("username")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    return render_template('login.html')

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

