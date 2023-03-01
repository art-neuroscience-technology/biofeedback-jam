from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer, ThreadingOSCUDPServer
import time
import numpy as np
import socket
import pandas as pd 
from generator import Generator
import utils
import os
import glob
import random
import logging
import sys, getopt
from slider import s3_uploader
import shutil


# create logger
logger = logging.getLogger('biofeedback')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(lineno)d - %(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

aws_access_key_id = ''
aws_secret_access_key = ''
bucket = 'biofeedback'

#interval in seconds
INTERVAL = 10

# sensors ('TP9','AF7','AF8','TP10') 
SENSORS=['AF7','AF8']

WAVES = [] 

RESULT_PATH = '/home/pi/biofeedback-jam/eeg-files'

start_timestamp = -1
image_generator = None
max_model_id = 0

save_mode = True
    
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
    global aws_access_key_id
    global aws_secret_access_key
    
    if start_timestamp==-1:
        return
    save_name = ''
    try:
        df = process_waves()

        start_timestamp = time.time()                
        
        if utils.check_values(df):
                
            logger.info(f'Processing waves for {start_timestamp}')
            model_id = random.randint(0, max_model_id)
            
            save_name = f'{start_timestamp}'
            if (save_mode): #save eeg result
                result = f'{RESULT_PATH}/{save_name}.csv'
                df.to_csv(result)
                ok = s3_uploader.upload_to_s3(result, 
                    bucket, 
                    f'eeg/{save_name}.csv', 
                    aws_access_key_id, 
                    aws_secret_access_key,
                    logger)
                if ok:
                    os.remove(result)
                else:
                    shutil.move(result, f'/home/pi/biofeedback-jam/eeg/')
            
            df = utils.transform_EEG(df, INTERVAL, noise_shape=(1,100), scale=2)
            image_generator.predict(df, model_id, save_name)
            model_id2 = (model_id+1) % max_model_id
            image_generator.predict(df, model_id2, f'{save_name}-2')
            logger.info(f'{model_id},{model_id2}')

    except Exception as ex:
        logger.error(f'Error:({save_name}) {ex}')
    

"""Processes the information corresponding a wave"""  
def wave_handler(address, *args):
    global WAVES
    global start_timestamp
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
    
    return dispatcher

"""Starts the server"""  
def start_blocking_server(ip, port, dispatcher):
    server = ThreadingOSCUDPServer(
      (ip, port), dispatcher)
    logger.info("Serving on {}".format(server.server_address))
    server.serve_forever()


def initialize():
    global image_generator
    global max_model_id
    global start_timestamp
    image_generator = Generator(models_path='tflite',
                                images_path='/home/pi/biofeedback-jam/slider/static/images')
    max_model_id = image_generator.get_models_count() -1
    start_timestamp = -1
    logger.info('Initialization completed')

def main(argv):
    global processing_thread
    global aws_access_key_id
    global aws_secret_access_key
    global bucket
    global save_mode
    
    #OCS listener
    IP='0.0.0.0'
    PORT = 5000
    
    opts, args = getopt.getopt(argv,"ha:s:m:i:p:",["access_key=","secret_key=", "mode=", "ip=", "port="])
    for opt, arg in opts:
       if opt == '-h':
          print ('mind_monitor_osc_server.py -a <access_key> -s <secret_key> -m <mode> -i <ip> - p <port>')
          sys.exit()
       elif opt in ("-a", "--access_key"):
          aws_access_key_id = arg
       elif opt in ("-s", "--secret_key"):
          aws_secret_access_key = arg
       elif opt in ("-m", "--mode"):
           save_mode = eval(arg)
       elif opt in ("-i", "--ip"):
           IP = arg
       elif opt in ("-p", "--port"):
           PORT = int(arg)
          
    initialize()
    processing_thread = utils.RepeatedTimer(INTERVAL + 1, process_signal)
    dispatcher = get_dispatcher()
    start_blocking_server(IP, PORT, dispatcher)


if __name__ == "__main__":
   main(sys.argv[1:])


