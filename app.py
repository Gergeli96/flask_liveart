from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
import psycopg2
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SubmitField, HiddenField
from passlib.hash import sha256_crypt
from functools import wraps
import os
from werkzeug import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)
DATABASE_URL = os.environ['DATABASE_URL']
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'XYZ')
#conn = psycopg2.connect(DATABASE_URL, sslmode='require')
conn = psycopg2.connect(DATABASE_URL)

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

    cur = conn.cursor()
    cur.execute("SELECT * FROM chategories")
    chategories = cur.fetchall()

    category = request.args.get('cat', '')
    cur = conn.cursor()
    data = []

    if not category == '':
        cur.execute("SELECT * FROM images WHERE category = %s", [category])
        data = cur.fetchall()
    else:
        cur.execute("SELECT * FROM images")
        data = cur.fetchall()

    print(request.args.get('cat', ''))
    return render_template('galery.html', data=data, chategories=chategories)



class UploadForm(Form):
    chategory = HiddenField('chategory', [validators.Length(min=1, max=50)])
    name = StringField('name', [validators.Length(min=1, max=50)])
    submit = SubmitField(label='')

class ChategoryForm(Form):
    chategory = StringField('chategory', [validators.Length(min=1, max=50)])
    submit1 = SubmitField(label='')

UPLOAD_FOLDER = 'static/uploadedImages'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/boss', methods=['GET', 'POST'])
@is_logged_in
def upload_file():
    chategoryForm = ChategoryForm(request.form)
    imageForm = UploadForm(request.form)
    cur = conn.cursor()
    cur.execute("SELECT * FROM chategories")
    chategories = cur.fetchall()

    if request.method == 'POST':

        if "submit" in request.form:
            if 'file' not in request.files:
                flash('Nem választottál ki fájlt!')
                return redirect('upload_file')
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return redirect('upload_file')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                category = imageForm.chategory.data
                cur = conn.cursor()
                cur.execute("INSERT INTO images (name, category) VALUES (%s, %s)", (filename, category))
                conn.commit()
                cur.close()
                flash('Sikeres fájl feltöltés!')
                return redirect(url_for('upload_file'))
        elif "submit1" in request.form and chategoryForm.chategory.data != '':
            category = chategoryForm.chategory.data
            cur = conn.cursor()
            cur.execute("INSERT INTO chategories (category) VALUES (%s)", (category,))
            conn.commit()
            cur.close()
            flash('Sikeres kategória feltöltés!')
            return redirect(url_for('upload_file'))
        else:
            flash('Valamit elbasztál!')
            return redirect(url_for('upload_file'))


    return render_template('boss.html', form=imageForm, chategories=chategories, chategoryForm=chategoryForm)


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
    #app.secret_key = 'drhrdtjertj45u56u5rzhrtz'
    app.run(debug=True)
