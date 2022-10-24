
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import os
import glob
import sys, getopt
from pythonosc import udp_client
import uuid
import time
import s3_uploader
import logging
import utils
import shutil


# create logger
logger = logging.getLogger('biofeedback')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(lineno)d - %(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

bucket = 'biofeedback'
aws_access_key_id, aws_secret_access_key = '', ''
identifier = ''

#mosaic values 
rowsize = 4

app = Flask(__name__)


def get_images():
    global identifier
    images = glob.glob("static/images/*.png")
    if len(images)>0:
        images.sort(key=os.path.getmtime)
        images.reverse()
        return images
    else:
        return []

@app.route('/show', methods = ['GET', 'POST'])
def show():
   global identifier
   response = render_template('index.html')
   filename = ''
   images = get_images()
   if len(images)>0:
       response = render_template('index.html', files=images, identifier=identifier)
   else:
       response = render_template('index.html', identifier=identifier)
   return response  
  
@app.route('/start', methods=['GET', 'POST'])  
def start():
    global identifier
    if request.method == 'GET':
        return redirect(url_for('show'))
   
    #remove images 
    images = get_images()
    for file_name in images:
        os.remove(file_name)
        
    images = glob.glob('/home/pi/biofeedback-jam/result/*.png')
    for file_name in images:
        os.remove(file_name)
    
    images = glob.glob('/home/pi/biofeedback-jam/qrs/*.png')
    for file_name in images:
        os.remove(file_name)
    

    #generate new indetifier  
    identifier = uuid.uuid4()
    logger.info(f'Created identifier {identifier}') 
   
    time.sleep(5)
    return render_template('index.html', identifier=identifier, visibility="hidden")


@app.route('/stop', methods=['GET', 'POST'])  
def stop():
    global identifier
    if request.method == 'GET':
        return redirect(url_for('show'))
    try:
        images = get_images()
        if len(images)>0:
            logger.info(f'Recieve END sing from identifier {identifier}')

        #generate mosaic
        if (len(images) >= rowsize*rowsize):
            logger.info('Generate mosaic')
            result = f'/home/pi/biofeedback-jam/result/{identifier}.png'
            utils.save_mosaic(images, result, rowsize)
            qr_path = utils.generate_qr(identifier)
            logger.info(f"Uploading file {result}")
            ok = s3_uploader.upload_to_s3(result, 
                bucket, 
                f'{identifier}.png', 
                aws_access_key_id, 
                aws_secret_access_key, logger)
            if ok:
                os.remove(result)
            else:
                shutil.move(result, f'/home/pi/biofeedback-jam/to_upload/')

        for file_name in images:
            os.remove(file_name)

    except Exception as ex:
        logger.error(f'Error:{ex}')

    identifier = ''
    time.sleep(5)
    return render_template('index.html', identifier='', visibility="visible")

    
    

if __name__ == '__main__':
    app.run(debug=True, port=7000)