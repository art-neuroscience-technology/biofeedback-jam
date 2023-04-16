import pandas as pd 
import time 
import random
import eeg_handler

class Processor():

    def __init__(self, sensors, max_model_id, save_mode, file_manager, interval, image_generator):
          self.waves = []
          self.sensors = sensors
          self.start_timestamp = -1
          self.max_model_id = max_model_id
          self.save_mode = save_mode 
          self.file_manager = file_manager
          self.interval = interval
          self.image_generator = image_generator

    def process_waves(self):
        df = pd.DataFrame()
        try:
            df = pd.DataFrame(self.waves, columns=['timestamp', 'wave_name'] + self.sensors)
        except Exception as ex:
            print(ex)
        self.waves=[]
        return df
    
    def process_signal(self):
        while True:
            print('Processing singal data')
            if self.start_timestamp!=-1:
                save_name = ''
                try:
                    df = self.process_waves()

                    self.start_timestamp = time.time()                
                    print(f'Processing waves - {self.start_timestamp}')
                    if eeg_handler.check_values(df):
                        print(f'Processing waves for {self.start_timestamp}')
                        model_id = random.randint(0, self.max_model_id)
                        
                        save_name = f'{self.start_timestamp}'
                        if (self.save_mode): #save eeg result
                            self.file_manager.save_eeg(df, save_name)
                        
                        df = eeg_handler.transform_EEG(df, self.interval, noise_shape=(1,100), scale=2)
                        print('Generate image')
                        self.image_generator.predict(df, model_id, save_name)
                        model_id2 = (model_id+1) % self.max_model_id
                        self.image_generator.predict(df, model_id2, f'{save_name}-2')
                        print(f'{model_id},{model_id2}')
                except Exception as ex:
                    print(f'Error:({save_name}) {ex}')
            time.sleep(self.interval)
        
    def reset(self):
        self.start_timestamp = -1


    def wave_handler(self, address, *args):
        try:
            print(f"Received OSC message: {address} {args}")
            if self.start_timestamp==-1:
                self.start_timestamp = time.time()

            wave_name = address.split('/muse/elements/')[1].split('_')[0]
            #keep ['AF7','AF8']
            wave_value = [time.time(), wave_name] + [args[1],args[2]]
            self.waves.append(wave_value)
        except Exception as ex:
            print(ex)
    