from PIL import Image
import numpy as np
import qrcode

import numpy as np
from threading import Timer
from functools import reduce
import pandas as pd
import random
import qrcode
from PIL import Image
import subprocess
import shutil

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


def save_mosaic(images, result_path, rowsize):
        images = np.random.choice(images,rowsize*rowsize)
        images = [Image.open(item) for item in images]
        image_list = []
        for i in range(1,rowsize+1):
            image_list.append(images[rowsize*(i-1):rowsize*i])
            
        get_concat_tile_resize(image_list).save(result_path)

def generate_qr(identifier):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f'http://doafy.me/{identifier}')
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    qr_path = f"/home/pi/biofeedback-jam/qrs/{identifier}.png"
    img.save(qr_path)
    return qr_path

    

def build_image(identifier, path):
    final_size = (306,991)

    im1 = Image.new('RGB', final_size, color = (255,255,255))

    im2 = Image.open(f'qrs/{identifier}.png') #330x330 
    im2 = im2.resize((300,300))

    im3 = Image.open('logos/logoANT.png') #996x580
    im3 = im3.resize((249, 146))
    im3 = im3.rotate(90, expand=True)


    im4 = Image.open('logos/logoRS.png') #996x580
    im4 = im4.resize((249, 146))
    im4 = im4.rotate(90, expand=True)


    im5 = Image.open('logos/logoDaofy.png') #717x174
    im5 = im5.resize((143, 35))
    im5 = im5.rotate(90, expand=True)

    im1.paste(im2, box=(3,2))
    im1.paste(im3, box=(55,280))
    im1.paste(im4, box=(58,552))
    im1.paste(im5, box=(145,814))
    im1.save(path)
    return path

def print_image(path, backup_path):
    subprocess.run(["brother_ql", "-b pyusb", "-p usb://0x04f9:0x209b", "-m QL-800", "print -l 29x90", path])
    if (result.stdout contains 'successful'):
        return True
    else:
        return False

    
