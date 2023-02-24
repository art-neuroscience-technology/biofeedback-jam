import glob 
import os 
from PIL import Image
import numpy as np
import random 

def get_images():
    images = glob.glob("static/images/*.png")
    if len(images)>0:
        images.sort(key=os.path.getmtime)
        images.reverse()
        return images
    else:
        return []
    
def image_grid(imgs, rows, cols):
    assert len(imgs) == rows*cols

    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols*w, rows*h))
    grid_w, grid_h = grid.size
    
    for i, img in enumerate(imgs):
        grid.paste(img, box=(i%cols*w, i//cols*h))
    return grid


rowsize=6
colsize=3
images = get_images()
print(len(images))
images = random.sample(images, rowsize*colsize)
images = [Image.open(item) for item in images]

if len(images)==rowsize*colsize:
    size = images[0].size
    grid = image_grid(images, rows=rowsize, cols=colsize)
    
    print(grid.size)
    grid = grid.resize((360, 640))
    print(grid.size)
    grid.save("grid4.png","png")
    grid.show()
