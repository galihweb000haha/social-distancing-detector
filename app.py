import os
from flask import (Flask, render_template, url_for, request, abort, redirect, make_response, session, flash, abort, jsonify)
from werkzeug.utils import secure_filename
# from pprint import pprint
import importlib
# from nacak import nacak
# from social_distance_detector import cobacoba
from social_distance_detector import start
from live_yolo_opencv import start_cam
# import random
# import string
from cryptography.fernet import Fernet
from uuid import uuid4


app = Flask(__name__)
app.secret_key = 'uripkayakietemenyah'

ALLOWED_EXTENSION = set(['mp4', 'jpg', 'png'])

key = Fernet.generate_key()
fernet = Fernet(key)


app.config['UPLOAD_FOLDER'] = 'upload'
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSION

def make_unique(string):
    ident = uuid4().__str__()[:8]
    return f"{ident}-{string}"

@app.route('/upload', methods=['GET', 'POST'])
def uploadFile():
    if request.method == 'POST':
        file = request.files['file']
        if 'file' not in request.files:
            return redirect(request.url)
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filename = make_unique(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('File has been uploaded successfully..!', 'success')

            encMessage = fernet.encrypt(filename.encode())

            return redirect(url_for('index', f=encMessage))
    return render_template('index.html')

@app.route('/')
def index():
    encMessage = request.args.get('f')
    # decMessage = ''
    # if encMessage is not None:
    #     encMessage = encMessage.encode()
    #     decMessage = fernet.decrypt(encMessage).decode()
    return render_template('index.html', filename=encMessage)
    
@app.route('/render', methods=['GET', 'POST'])
def render():
    if request.method == 'POST':
        encMessage = request.form['f'].encode()
        decMessage = fernet.decrypt(encMessage).decode()
    # format = request.args.get('format')

    start( ('upload/'+decMessage), ('output/'+decMessage+'.avi'), 0)
    return jsonify(decMessage)
@app.route('/oncam')
def oncam():
    start_cam()
    return "<a href='/'>RETURN</a>"

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
