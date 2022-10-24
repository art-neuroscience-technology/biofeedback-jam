import numpy as np
from threading import Timer
from functools import reduce
import pandas as pd
import random
import qrcode
from PIL import Image
import subprocess
import shutil


def generate_qr(identifier, path):
    import qrcode
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f'https://www.daofy.me/{identifier}')
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(path)
    return img 

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

def print_image(path, backup_path):
    subprocess.run(["brother_ql", "-b pyusb", "-p usb://0x04f9:0x209b", "-m QL-800", "print -l 29x90", path])
    if (result.stdout contains 'successful'):
        os.remove(path)
    else:
        shutil.move(path, backup_path)

    