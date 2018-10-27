from flask import Flask, render_template, request, flash, redirect, url_for, session, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
import os
from werkzeug import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename


app = Flask(__name__)
#mysql = MySQL()

# MySQL configurations
#app.config['MYSQL_DATABASE_USER'] = 'root'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
#app.config['MYSQL_DATABASE_DB'] = 'josi'
#app.config['MYSQL_DATABASE_HOST'] = 'localhost'
#mysql.init_app(app)

#conn = mysql.connect()
#cursor = conn.cursor()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/galery')
def galery():
    return render_template('galery.html')

#@app.route('/boss')
#def boss():
#    return render_template('boss.html')




UPLOAD_FOLDER = 'static/uploadedImages'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/boss', methods=['GET', 'POST'])
def upload_file():
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
            return redirect(url_for('upload_file', filename=filename))


    return render_template('boss.html')



if __name__ == '__main__':
    app.run(debug=True)
