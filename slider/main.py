
from flask import Flask, render_template, request, redirect, url_for, make_response
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import os
import glob

app = Flask(__name__)

@app.route('/')
def show():
    return render_template('index.html')
  
@app.route('/show', methods = ['GET'])
def show_page():
   response = render_template('index.html')
   filename = ''
   if request.method == 'GET':
         files = glob.glob("static/images/*")
         files.sort(key=os.path.getmtime)
         files.reverse()
         response = render_template('index.html', files=files)
   else:
         response = render_template('index.html')
   return response  
  
  
# main driver function
if __name__ == '__main__':

    app.run(debug=True, port=7000)