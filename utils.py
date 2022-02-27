import numpy as np
from PIL import Image
import numpy as np
from threading import Timer
from functools import reduce
import pandas as pd


"""Calls function {function} every {interval} seconds """
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False

def transform_EEG(df, seconds, noise_shape, scale):
  #to seconds
  min_value = df['timestamp'].min()
  df['timestamp'] = round(df['timestamp'] - min_value)
  df = df.groupby(['wave_name','timestamp']).median().reset_index()

  #fill out 0 with random values 
  df['AF7'] = df.A.replace(to_replace =0.0, value =  np.random.normal(0,1))
  df['AF8'] = df.A.replace(to_replace =0.0, value =  np.random.normal(0,1))
  
  #create columns for each tuple wave_name and sensor_name
  waves_dict = df.groupby('wave_name').groups
  dfs = []
  for w in waves_dict:
    df_aux=df[df['wave_name']==w][['AF7','AF8', 'timestamp']]
    df_aux[f'AF7_{w}']=df_aux['AF7']
    df_aux[f'AF8_{w}']=df_aux['AF8']
    df_aux.drop(['AF7','AF8'], axis=1, inplace=True)
    dfs.append(df_aux)

  #merge created columns by timestamp value 
  df = reduce(lambda x, y: pd.merge(x, y, on = 'timestamp'), dfs)
  df.drop('timestamp', axis=1, inplace=True)
  #keep only last values 
  df = df.tail(seconds)

  #transform dataframe to numpy array
  if (df.shape[0]<seconds):
    return np.random.normal(0, 1, (1,100))

  df = df.values
  df = df.reshape(noise_shape)  

  #rescale
  df = 2.*(df - np.min(df))/np.ptp(df)-scale
  return df

def save_mosaic(images, result_path, rowsize, colsize, imgShape):
  margin = 16
  image_array = np.full((margin + (rowsize * (imgShape+margin)), 
    margin + (colsize * (imgShape+margin)), 3), 
  255, dtype=np.uint8)
  image_count = 0
  for row in range(rowsize):
    for col in range(colsize):
      r = row * (imgShape+margin) + margin
      c = col * (imgShape+margin) + margin
      image_array[r:r+imgShape,c:c+imgShape] = images[image_count] 
      image_count += 1

  im = Image.fromarray(image_array)
  im.save(result_path)
    