#!/bin/python 

from flask import Flask, render_template, request, redirect, url_for, make_response
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from fastai.vision.all import *
import os
import time
import datetime
from pathlib import Path
import re

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', 'jpeg']
app.secret_key = "OopbBPqgw95PhuJDb2lG3XSq"


@app.route('/check')
def check():
    return 'ok'

@app.route('/reset', methods = ['POST'])
def reset():
   for file_name in os.listdir('results-images'):
      os.rename(f'results-images/{file_name}', f'to_upload/{file_name}')
   response = render_template('upload.html')


@app.route('/', methods = ['GET'])
def show_page():
   response = render_template('index.html')
   filename = ''
   if request.method == 'GET':
      while(True):
         files = os.listdir('/Users/mika/Projects/biofeedback-jam/slider/results-images')
         response = render_template('upload.html', files=files)
      else:
         response = render_template('upload.html')
   return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6000)

