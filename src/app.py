from flask import Flask, render_template, request, redirect, url_for
from threading import Thread
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from time import sleep
from distutils.util import strtobool

import os
import glob
import sys
import uuid
import s3_uploader
import utils
import shutil
import time
import pandas as pd 
from generator import Generator
import utils
import os
import random
import sys
import config 
import processor
import file_manager

config = config.Config()

# sensors ('TP9','AF7','AF8','TP10') 
SENSORS=['AF7','AF8']
start_timestamp = -1
identifier = -1
image_generator = Generator(models_path=config.models_path, images_path=config.images_path)

max_model_id = image_generator.get_models_count() -1

file_managment = file_manager.FileManager()
eeg_processor = processor.Processor(max_model_id=max_model_id, 
                    save_mode=config.save_mode_mind_monitor,
                     aws_access_key_id=config.aws_access_key_id, 
                     aws_secret_access_key=config.aws_secret_access_key,
                     file_manager=file_managment,
                     interval=config.interval,
                     sensors=SENSORS,
                     image_generator=image_generator)



WAVES = [] 

app = Flask(__name__)


def create_dir(directory): 
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"{directory} created successfully.")
    else:
        print(f"{directory} already exists.")


def get_images():
    global identifier
    images = glob.glob(f"{IMAGES_PATH}/*.png")
    if len(images)>0:
        images.sort(key=os.path.getmtime)
        images.reverse()
        return images
    else:
        return []
    

def process_waves():
  global WAVES
  df = pd.DataFrame()
  try:
      df = pd.DataFrame(WAVES, columns=['timestamp', 'wave_name'] + SENSORS)
  except Exception as ex:
    print(ex)
  WAVES=[]
  return df

def process_signal():
     global start_timestamp
     while True:
        if start_timestamp!=-1:
            save_name = ''
            try:
                df = process_waves()

                start_timestamp = time.time()                
                
                if utils.check_values(df):
                        
                    print(f'Processing waves for {start_timestamp}')
                    model_id = random.randint(0, max_model_id)
                    
                    save_name = f'{start_timestamp}'
                    if (SAVE_MODE_MIND_MONITOR): #save eeg result
                        result = f'{RESULT_EEG_PATH}/{save_name}.csv'
                        df.to_csv(result)
                        ok = s3_uploader.upload_to_s3(result, 
                            S3_BUCKET, 
                            f'eeg/{save_name}.csv', 
                            AWS_ACCESS_KEY_ID, 
                            AWS_SECRET_ACCESS_KEY)
                        if ok:
                            os.remove(result)
                        else:
                            shutil.move(result, EEG_BACKUP_FOLDER)
                    
                    df = utils.transform_EEG(df, INTERVAL, noise_shape=(1,100), scale=2)
                    print('Generate image')
                    image_generator.predict(df, model_id, save_name)
                    model_id2 = (model_id+1) % max_model_id
                    image_generator.predict(df, model_id2, f'{save_name}-2')
                    print(f'{model_id},{model_id2}')
            except Exception as ex:
                print(f'Error:({save_name}) {ex}')
        sleep(INTERVAL)
        

"""Processes the information corresponding a wave"""  
def wave_handler(address, *args):
    global WAVES
    global start_timestamp
    try:
        print(f"Received OSC message: {address} {args}")
        if start_timestamp==-1:
            start_timestamp = time.time()

        wave_name = address.split('/muse/elements/')[1].split('_')[0]
        #keep ['AF7','AF8']
        wave_value = [time.time(), wave_name] + [args[1],args[2]]
        WAVES.append(wave_value)
    except Exception as ex:
        print(ex)

"""Creates a map between paths and actions"""  
def get_dispatcher():
    dispatcher = Dispatcher()
    dispatcher.map("/muse/elements/delta_absolute", wave_handler)
    dispatcher.map("/muse/elements/theta_absolute", wave_handler)
    dispatcher.map("/muse/elements/alpha_absolute", wave_handler)
    dispatcher.map("/muse/elements/beta_absolute", wave_handler)
    dispatcher.map("/muse/elements/gamma_absolute", wave_handler)
    
    return dispatcher

def initialize():
    global image_generator
    global max_model_id
    global start_timestamp
    image_generator = Generator(models_path=MODELS_PATH,
                                images_path=IMAGES_PATH)
    max_model_id = image_generator.get_models_count() -1
    create_dir(QRS_PATH)
    create_dir(QRS_BACKUP_PATH)
    create_dir(RESULT_GRID_PATH)
    create_dir(RESULT_GRID_PATH_BACKUP)
    create_dir(RESULT_EEG_PATH)
    create_dir(EEG_BACKUP_FOLDER)
    create_dir(IMAGES_PATH)

# Set up the OSC server in a separate thread
def run_osc_server():
    dispatcher = get_dispatcher()
    server = BlockingOSCUDPServer((OSC_IP, OSC_PORT), dispatcher)
    print(f"OSC server listening on {OSC_IP}:{OSC_PORT}...")
    server.serve_forever()

def background_task():
    while True:
        print(WAVES)
        sleep(1)

@app.route("/")
def hello_world():
    return "<p>BIOFFEDBACK</p>"


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
        
    #remove grid images     
    images = glob.glob(f'{RESULT_GRID_PATH}*.png') 
    for file_name in images:
        os.remove(file_name)
    
    #remove qrs 
    images = glob.glob(f'{QRS_PATH}/*.png')
    for file_name in images:
        os.remove(file_name)
    
    #generate new indetifier  
    id = f'{str(1)}{str(uuid.uuid4())}'
    id_aux = ''
    for c in id:
        if(c.isnumeric()):
            id_aux = id_aux + c
    identifier = id_aux
    print(f'Created identifier {identifier}') 
   
    time.sleep(2)
    return render_template('index.html', identifier=identifier, visibility="hidden")


@app.route('/stop', methods=['GET', 'POST'])  
def stop():
    global identifier
    
    if request.method == 'GET':
        return redirect(url_for('show'))
    try:
        images = get_images()
        print(f'Recieve END sing from identifier {identifier}')
  
        
        #generate grid
        if (len(images) >= ROW_SIZE*COL_SIZE):
            if (GENERTE_QR):
                print('Generate grid')
                
                qr_path = f"{QRS_PATH}{identifier}.png"
                utils.generate_qr(identifier, qr_path)
                utils.build_image_62mm(identifier, qr_path, LOGOS_PATH)
                
                print(f'Printing image {identifier}.png')
                ok = utils.print_image(qr_path,'62', QL_PATH)
        
                if (ok):
                    os.remove(qr_path)
                else:
                    shutil.move(qr_path, f'{QRS_BACKUP_PATH}/{identifier}.png')

            result = f'{RESULT_GRID_PATH}/{identifier}.png'
            print(f"Uploading file {result}")
            utils.save_grid(images, result, ROW_SIZE, COL_SIZE)
            
            if (SAVE_MODE_SLIDER):
                ok = s3_uploader.upload_to_s3(result, 
                    S3_BUCKET, 
                    f'{identifier}.png', 
                    AWS_ACCESS_KEY_ID, 
                    AWS_SECRET_ACCESS_KEY)
                if ok:
                    os.remove(result)
                else:
                    shutil.move(result, RESULT_GRID_PATH_BACKUP)
            else:
                shutil.move(result, RESULT_GRID_PATH_BACKUP)

        for file_name in images:
            os.remove(file_name)

    except Exception as ex:
        print(f'Error:{ex}')

    identifier = ''
    time.sleep(2)
    return render_template('index.html', identifier='', visibility="visible")




if __name__ == "__main__":
    initialize()
    thread = Thread(target=run_osc_server)
    thread.start()
    thread2 = Thread(target=process_signal)
    thread2.start()

    app.run(host='0.0.0.0', port=7001)