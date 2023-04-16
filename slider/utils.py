from PIL import Image
import numpy as np
from threading import Timer
from functools import reduce
import random
import qrcode
from PIL import Image
import subprocess
import pandas as pd
import os 
import glob

def create_dir(directory): 
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"{directory} created successfully.")
    else:
        print(f"{directory} already exists.")


def get_images(image_path):
    global identifier
    images = glob.glob(f"{image_path}/*.png")
    if len(images)>0:
        images.sort(key=os.path.getmtime)
        images.reverse()
        return images
    else:
        return []


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
    
    

