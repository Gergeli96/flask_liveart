from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
import pymysql.cursors
import psycopg2
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
import os
from werkzeug import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             db='josi',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

conn = psycopg2.connect("dbname=josi user=postgres password=root host=localhost")

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/galery')
def galery():
    return render_template('galery.html')



class UploadForm(Form):
    chategory = StringField('chategory', [validators.Length(min=1, max=50)])


UPLOAD_FOLDER = 'static/uploadedImages'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/boss', methods=['GET', 'POST'])
@is_logged_in
def upload_file():
    form = UploadForm(request.form)
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect('name')
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect('home')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            category = form.chategory.data
            cur = conn.cursor()
            cur.execute("INSERT INTO images (name, category) VALUES (%s, %s)", (filename, category))
            conn.commit()
            cur.close()

            return redirect(url_for('upload_file', filename=filename))

    return render_template('boss.html', form=form)


class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')


# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username, password))
        conn.commit()
        cur.close()


        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']

        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if cur.rowcount > 0:
            # Get stored hash
            data = cur.fetchone()
            print('adatok')
            print(data[4])
            print(password_candidate)
            password = data[4]

            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('upload_file'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error)

    return render_template('login.html')


# Logout
@app.route('/logout')
#@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
