from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer, ThreadingOSCUDPServer
import time
import numpy as np
import socket
import uuid
import pandas as pd 
from generator import Generator
import random
import utils
import os

import logging

# create logger
logging.config.fileConfig('logging.conf')
logger = logging.getLogger('biofeedback')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

#OCS listener
IP='0.0.0.0'
PORT = 5000

#interval in seconds
INTERVAL = 10

# sensors ('TP9','AF7','AF8','TP10') 
SENSORS=['AF7','AF8']

RESULT_PATH='/home/pi/biofeedback-jam/eeg'

WAVES = [] 

identifier = ''
start_timestamp = -1
image_generator = None
max_model_id = 0

running_mode=True

def reset():
    for file_name in os.listdir('/home/pi/biofeedback-jam/slider/static/images'):
      os.rename(f'/home/pi/biofeedback-jam/slider/static/images/{file_name}', f'/home/pi/biofeedback-jam/to_upload/{file_name}')

def create_identifier():
    global identifier
    identifier = uuid.uuid4()
    print(f'Created identifier {identifier}')
    reset()

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
    global identifier
    global running_mode
    
    if start_timestamp==-1:
        return
    save_name = ''
    try:
        df = process_waves()

        start_timestamp = time.time()                
        
        if utils.check_values(df):
            if identifier=='':
                create_identifier()
                
            logger.info(f'({identifier}) Processing waves for {start_timestamp}')
            model_id = random.randint(0, max_model_id)
            save_name = f'{identifier}_{start_timestamp}'
            #save eeg result
            df.to_csv(f'{RESULT_PATH}/{save_name}.csv') 
            
            if running_mode:
                df = utils.transform_EEG(df, INTERVAL, noise_shape=(1,100), scale=2)
                image_generator.predict(df, model_id, save_name)
           
        else:
            identifier=''

    except Exception as ex:
        logger.error(f'Error:({save_name}) {ex}')
    

"""Processes the information corresponding a wave"""  
def wave_handler(address, *args):
    global WAVES
    global start_timestamp
    global identifier
    try:
        if start_timestamp==-1:
            start_timestamp = time.time() 

        wave_name = address.split('/muse/elements/')[1].split('_')[0]
        #keep ['AF7','AF8']
        wave_value = [time.time(), wave_name] + [args[1],args[2]]
        WAVES.append(wave_value)
    except Exception as ex:
        logger.error(ex)



"""Creates a map between paths and actions"""  
def get_dispatcher():
    dispatcher = Dispatcher()
    dispatcher.map("/muse/elements/delta_absolute", wave_handler)
    dispatcher.map("/muse/elements/theta_absolute", wave_handler)
    dispatcher.map("/muse/elements/alpha_absolute", wave_handler)
    dispatcher.map("/muse/elements/beta_absolute", wave_handler)
    dispatcher.map("/muse/elements/gamma_absolute", wave_handler)
    #dispatcher.map("/muse/elements/horseshoe", horseshoe_handler)
    
    return dispatcher

"""Starts the server"""  
def start_blocking_server(ip, port):
    server = ThreadingOSCUDPServer(
      (ip, port), dispatcher)
    logger.info("Serving on {}".format(server.server_address))
    server.serve_forever()


def initialize():
    global image_generator
    global max_model_id
    global identifier
    global start_timestamp
    image_generator = Generator(models_path='tflite',
                                images_path='/home/pi/biofeedback-jam/slider/static/images')
    max_model_id = image_generator.get_models_count() -1
    identifier = ''
    start_timestamp = -1
    logger.info('Initialization completed')

if __name__ == '__main__':
    global processing_thread
    initialize()
    processing_thread = utils.RepeatedTimer(INTERVAL + 1, process_signal)
    dispatcher = get_dispatcher()
    start_blocking_server(IP, PORT)


