
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
import os
import glob
import sys, getopt
import uuid
import time
import s3_uploader
import logging
import utils
import shutil
import time 


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
start_timestamp = -1
rowsize = 6
colsize = 3

app = Flask(__name__)

save_mode = True

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
   images = get_images()
   if len(images)>0:
       response = render_template('index.html', files=images, identifier=identifier)
   else:
       response = render_template('index.html', identifier=identifier)
   return response  
  
@app.route('/start', methods=['GET', 'POST'])  
def start():
    global identifier
    global start_timestamp
    if request.method == 'GET':
        return redirect(url_for('show'))
    
    start_timestamp = time.time()
    
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
    id = f'{str(1)}{str(uuid.uuid4())}'
    id_aux = ''
    for c in id:
        if(c.isnumeric()):
            id_aux = id_aux + c
    identifier = id_aux
    logger.info(f'Created identifier {identifier}') 
   
    time.sleep(2)
    return render_template('index.html', identifier=identifier, visibility="hidden")


@app.route('/stop', methods=['GET', 'POST'])  
def stop():
    global identifier
    global start_timestamp
    global aws_access_key_id
    global aws_secret_access_key
    
    if request.method == 'GET':
        return redirect(url_for('show'))
    try:
        images = get_images()
        if len(images)>0:
            logger.info(f'Recieve END sing from identifier {identifier}')
        
        end_timestamp = time.time()
        with open('/home/pi/biofeedback-jam/slider/timestamp_users.csv', 'a') as file:
            file.write(f'{start_timestamp};{end_timestamp};{identifier}\n')
        
        start_timestamp = -1    
        #generate grid
        if (len(images) >= rowsize*colsize):
            logger.info('Generate grid')
            
            qr_path = f"/home/pi/biofeedback-jam/qrs/{identifier}.png"
            utils.generate_qr(identifier, qr_path)
            utils.build_image_62mm(identifier, qr_path)
            
            logger.info(f'Printing image {identifier}.png')
            ok = utils.print_image(qr_path,'62',logger)
     
            if (ok):
                os.remove(qr_path)
            else:
                shutil.move(qr_path, f'/home/pi/biofeedback-jam/backup_qrs/{identifier}.png')

            result = f'/home/pi/biofeedback-jam/result/{identifier}.png'
            logger.info(f"Uploading file {result}")
            utils.save_grid(images, result, rowsize, colsize)
            
            if (save_mode):
                ok = s3_uploader.upload_to_s3(result, 
                    bucket, 
                    f'{identifier}.png', 
                    aws_access_key_id, 
                    aws_secret_access_key,
                    logger)
                if ok:
                    os.remove(result)
                else:
                    shutil.move(result, f'/home/pi/biofeedback-jam/to_upload/')
            else:
                shutil.move(result, f'/home/pi/biofeedback-jam/to_upload/')

        for file_name in images:
            os.remove(file_name)

    except Exception as ex:
        logger.error(f'Error:{ex}')

    identifier = ''
    time.sleep(2)
    return render_template('index.html', identifier='', visibility="visible")

def main(argv):    
    global aws_access_key_id
    global aws_secret_access_key
    global bucket
    global save_mode
    
    opts, args = getopt.getopt(argv,"hb:a:s:m:",["access_key=","secret_key=","mode="])
    for opt, arg in opts:
       if opt == '-h':
          print ('main.py -a <access_key> -s <secret_key> -m <mode>')
          sys.exit()
       elif opt in ("-a", "--access_key"):
          aws_access_key_id = arg
       elif opt in ("-s", "--secret_key"):
          aws_secret_access_key = arg
       elif opt in ("-m", "--mode"):
           save_mode = eval(arg)
       

    app.run(debug=True, port=7000)
    

if __name__ == "__main__":
   main(sys.argv[1:])