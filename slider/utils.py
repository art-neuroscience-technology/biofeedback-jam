from PIL import Image
import numpy as np
from threading import Timer
from functools import reduce
import random
import qrcode
from PIL import Image
import subprocess
import pandas as pd


def save_grid(images, result_path, rowsize=6, colsize=3, result_size=(360, 640)):
        images = random.sample(images, rowsize*colsize)
        images = [Image.open(item) for item in images]
        w, h = images[0].size
        grid = Image.new('RGB', size=(colsize*w, rowsize*h))
        for i, img in enumerate(images):
            grid.paste(img, box=(i%colsize*w, i//colsize*h))
    
        grid = grid.resize(result_size)
        grid.save(result_path,"png")

        
def generate_qr(identifier, qr_path):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f'http://daofy.me/claim/{identifier}')
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_path)

    

def build_image_29mm(identifier, path, logos_path):
    final_size = (306,991)

    im1 = Image.new('RGB', final_size, color = (255,255,255))

    im2 = Image.open(f'{logos_path}/{identifier}.png') #330x330 
    im2 = im2.resize((300,300))

    im3 = Image.open(f'{logos_path}/logoANT.png') #996x580
    im3 = im3.resize((249, 146))
    im3 = im3.rotate(90, expand=True)


    im4 = Image.open(f'/{logos_path}/logoRS.png') #996x580
    im4 = im4.resize((249, 146))
    im4 = im4.rotate(90, expand=True)


    im5 = Image.open(f'{logos_path}/logoDaofy.png') #717x174
    im5 = im5.resize((143, 35))
    im5 = im5.rotate(90, expand=True)

    im1.paste(im2, box=(3,2))
    im1.paste(im3, box=(55,280))
    im1.paste(im4, box=(58,552))
    im1.paste(im5, box=(145,814))
    im1.save(path)
    
def build_image_62mm(identifier, path, logos_path):        
    final_size = (696,1109)

    im1 = Image.new('RGB', final_size, color = (255,255,255))

    im2 = Image.open(f'{logos_path}/logoANT.png') #1444x652
    im2 = im2.resize((577, 260))

    im3 = Image.open(f'{logos_path}/{identifier}.png') #330x330 

    im4 = Image.open(f'{logos_path}/logoRS.png') #996x580
    im4 = im4.resize((498, 290))

    im5 = Image.open(f'{logos_path}/logoDaofy.png') #717x174
    im5 = im5.resize((478, 116))

    im1.paste(im2, box=(62,4))
    im1.paste(im3, box=(185,266))
    im1.paste(im4, box=(98,598))
    im1.paste(im5, box=(108,894))
    im1.save(path)


def print_image(image_path, size, QL_PATH):
    
    print(f'Printing {image_path}')
    try:
        result = subprocess.run([QL_PATH,
                    "-b","pyusb",
                    "-p","usb://0x04f9:0x209b",
                    "-m","QL-800",
                    "print","-l",size,
                    image_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True)
        
        if('Error' not in result.stderr):
            return True
        else:
            print(f'Result = {result}')
            return False

    except Exception as ex:
        print(f'Error:{ex}')
        return False
    
        
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

    