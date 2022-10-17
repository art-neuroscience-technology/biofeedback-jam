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
        
def check_values(df):
    if df.empty:
        return False
    if len(df.columns)==0:
        return False
    if not 'AF7' in df.columns:
        return False
    if not 'AF8' in df.columns:
        return False
    if (df['AF7'].mean()==0.0 and df['AF8'].mean()==0.0):
        return False
    return True

def transform_EEG(df, seconds, noise_shape, scale):
  #to seconds
  min_value = df['timestamp'].min()
  df['timestamp'] = round(df['timestamp'] - min_value)
  df = df.groupby(['wave_name','timestamp']).median().reset_index()

  #fill out 0 with random values
  df['AF7'] = df['AF7'].replace(to_replace =0.0, value =  np.random.normal(0,1))
  df['AF8'] = df['AF8'].replace(to_replace =0.0, value =  np.random.normal(0,1))
  
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


def get_concat_h_multi_resize(im_list, resample=Image.BICUBIC):
    min_height = min(im.height for im in im_list)
    im_list_resize = [im.resize((int(im.width * min_height / im.height), min_height),resample=resample)
                      for im in im_list]
    total_width = sum(im.width for im in im_list_resize)
    dst = Image.new('RGB', (total_width, min_height))
    pos_x = 0
    for im in im_list_resize:
        dst.paste(im, (pos_x, 0))
        pos_x += im.width
    return dst

def get_concat_v_multi_resize(im_list, resample=Image.BICUBIC):
    min_width = min(im.width for im in im_list)
    im_list_resize = [im.resize((min_width, int(im.height * min_width / im.width)),resample=resample)
                      for im in im_list]
    total_height = sum(im.height for im in im_list_resize)
    dst = Image.new('RGB', (min_width, total_height))
    pos_y = 0
    for im in im_list_resize:
        dst.paste(im, (0, pos_y))
        pos_y += im.height
    return dst


def get_concat_tile_resize(im_list_2d, resample=Image.BICUBIC):
    im_list_v = [get_concat_h_multi_resize(im_list_h, resample=resample) for im_list_h in im_list_2d]
    return get_concat_v_multi_resize(im_list_v, resample=resample)


def save_mosaic(images, result_path, rowsize, colsize):
    try:
        images = random.choices(images, int(rowsize*colsize))
        index = int(len(images)/colsize)
        images = [Image.open(item) for item in images]
        get_concat_tile_resize([images[:index],
            images[index:index*2], 
            images[index*2:index*3], 
            images[index*3:index*4]]).save(result_path)

    except Exception as ex:
        print(f'Error:{ex}')
    
    