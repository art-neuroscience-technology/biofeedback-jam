from flask import Flask, render_template, request, redirect, url_for
from threading import Thread
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from time import sleep
from distutils.util import strtobool

import os
import glob
import uuid
import s3_uploader
import utils
import shutil
import time
from generator import Generator
import utils
import os
import config 
import processor
import file_manager

config = config.Config()

# sensors ('TP9','AF7','AF8','TP10') 
SENSORS=['AF7','AF8']
start_timestamp = -1
identifier = -1
image_generator = None
max_model_id = 0

eeg_processor = None


WAVES = [] 

app = Flask(__name__)


"""Creates a map between paths and actions"""  
def get_dispatcher():
    dispatcher = Dispatcher()
    dispatcher.map("/muse/elements/delta_absolute", eeg_processor.wave_handler)
    dispatcher.map("/muse/elements/theta_absolute", eeg_processor.wave_handler)
    dispatcher.map("/muse/elements/alpha_absolute", eeg_processor.wave_handler)
    dispatcher.map("/muse/elements/beta_absolute", eeg_processor.wave_handler)
    dispatcher.map("/muse/elements/gamma_absolute", eeg_processor.wave_handler)
    
    return dispatcher

def initialize():
    global image_generator
    global max_model_id
    global eeg_processor

    image_generator = Generator(models_path=config.models_path,
                                images_path=config.images_path)
    
    max_model_id = image_generator.get_models_count() -1

    file_managment = file_manager.FileEEGManager(config.result_eeg_path, 
                                                 config.eeg_backup_folder, 
                                                 config.s3_bucket, 
                                                 config.aws_access_key_id, 
                                                 config.aws_secret_access_key)
    
    eeg_processor = processor.Processor(sensors=SENSORS, 
                                        max_model_id=max_model_id, 
                                        save_mode=config.save_mode_mind_monitor, 
                                        file_manager=file_managment, 
                                        interval=config.interval,
                                        image_generator=image_generator)
        
    if (config.save_mode_mind_monitor):
        utils.create_dir(config.result_eeg_path)
        utils.create_dir(config.eeg_backup_folder)
    
    if (config.generate_qr):
        utils.create_dir(config.qrs_path)
        utils.create_dir(config.qrs_backup_path)
    
    utils.create_dir(config.result_grid_path)
    utils.create_dir(config.result_grid_path_backup)
    utils.create_dir(config.images_path)

# Set up the OSC server in a separate thread
def run_osc_server():
    dispatcher = get_dispatcher()
    server = BlockingOSCUDPServer((config.osc_ip, config.osc_port), dispatcher)
    print(f"OSC server listening on {config.osc_ip}:{config.osc_port}...")
    server.serve_forever()


@app.route("/")
def hello_world():
    return "<p>BIOFFEDBACK</p>"


@app.route('/show', methods = ['GET', 'POST'])
def show():
   global identifier
   images = utils.get_images(config.images_path)
   if len(images)>0:
       files = list(map(lambda x: x.split('slider/')[1] ,images))
       response = render_template('index.html', files=files, identifier=identifier)
   else:
       response = render_template('index.html', identifier=identifier)
   return response  
  
@app.route('/start', methods=['GET', 'POST'])  
def start():
    global identifier

    if request.method == 'GET':
        return redirect(url_for('show'))
        
    #remove images 
    images = utils.get_images(config.images_path)
    for file_name in images:
        os.remove(file_name)
        
    #remove grid images     
    images = glob.glob(f'{config.result_grid_path}*.png') 
    for file_name in images:
        os.remove(file_name)
    
    #remove qrs 
    images = glob.glob(f'{config.qrs_path}/*.png')
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
        images = utils.get_images(config.images_path)
        print(f'Recieve END sing from identifier {identifier}')
  
        #generate grid
        if (len(images) >= config.row_size*config.col_size):
            if (config.generate_qr):
                print('Generate grid')
                
                qr_path = f"{config.qrs_path}{identifier}.png"
                utils.generate_qr(identifier, qr_path)
                utils.build_image_62mm(identifier, qr_path, config.logos_path)
                
                print(f'Printing image {identifier}.png')
                ok = utils.print_image(qr_path,'62', config.ql_path)
        
                if (ok):
                    os.remove(qr_path)
                else:
                    shutil.move(qr_path, f'{config.qrs_backup_path}/{identifier}.png')

            result = f'{config.result_grid_path}/{identifier}.png'
            print(f"Uploading file {result}")
            utils.save_grid(images, result, config.row_size, config.col_size)
            
            if (config.save_mode_slider):
                ok = s3_uploader.upload_to_s3(result, 
                    config.s3_bucket, 
                    f'{identifier}.png', 
                    config.aws_access_key_id, 
                    config.aws_secret_access_key)
                if ok:
                    os.remove(result)
                else:
                    shutil.move(result, config.result_grid_path_backup)
            else:
                shutil.move(result, config.result_grid_path_backup)

        for file_name in images:
            os.remove(file_name)

    except Exception as ex:
        print(f'Error:{ex}')

    identifier = ''
    eeg_processor.reset()
    time.sleep(2)
    return render_template('index.html', identifier='', visibility="visible")




if __name__ == "__main__":
    initialize()
    thread = Thread(target=run_osc_server)
    thread.start()
    thread2 = Thread(target=eeg_processor.process_signal)
    thread2.start()

    app.run(host='0.0.0.0', port=7001)