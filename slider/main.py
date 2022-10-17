
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import os
import glob
import sys, getopt
from pythonosc import udp_client
import uuid
import time

ip_mind_monitor = "192.168.0.199"
port_mind_monitor = 5001
 

app = Flask(__name__)

def process_files():
    files = glob.glob("static/images/*.png")
    if len(files)>0:
        files.sort(key=os.path.getmtime)
        files.reverse()
        identifier = files[0].split('_')[0].split('/')[2]
        return files, identifier
    else:
        return [], ''

@app.route('/', methods = ['GET', 'POST'])
def show():
   response = render_template('index.html')
   filename = ''
   if request.method == 'GET':
       files, identifier = process_files()
       if len(files)>0:
           response = render_template('index.html', files=files, identifier=identifier)
       else:
           response = render_template('index.html')
   else:
       response = render_template('index.html')
   return response  
  
@app.route('/start', methods=['GET', 'POST'])  
def start():
   if request.method == 'GET':
    return show()
    
   #generate identifier
   if request.form.get('identifier'):
        return show() 
   identifier = uuid.uuid4()
   print(f'Created identifier {identifier}') 
   
   #initialize client
   client = udp_client.SimpleUDPClient(ip_mind_monitor, port_mind_monitor)
   client.send_message('/start', str(identifier))
   response = render_template('index.html', identifier=identifier, visibility="hidden")
   return response


@app.route('/stop', methods=['GET', 'POST'])  
def stop():
   if request.method == 'GET':
      return show()
   identifier = request.form.get("identifier")   
   if identifier=='':
      return render_template('index.html', identifier='', visibility="visible")
   client = udp_client.SimpleUDPClient(ip_mind_monitor, port_mind_monitor)
   client.send_message('/stop', str(identifier))
   time.sleep(10)
   response = render_template('index.html', identifier='', visibility="visible")
   return response




# main driver function
if __name__ == '__main__':

    app.run(debug=True, port=7000)