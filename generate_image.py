
from PIL import Image

final_size = (306,991)

im1 = Image.new('RGB', final_size, color = (255,255,255))

im2 = Image.open('qr-ant.png') #330x330 
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
im1.paste(im5, box=(145,812))

im1.save('test.png')

#brother_ql -b pyusb -p usb://0x04f9:0x209b -m QL-800 print -l 29x90 test.png