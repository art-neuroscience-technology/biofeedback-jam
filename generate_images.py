from PIL import Image
import numpy as np
import os
import pandas as pd
import Generator 
import utils
import random

#noise files' directory 
noise_files = os.listdir('noise/')

models_path='models-tflite/'
models = os.listdir(models_path)
load_models = Generator.load_models(models_path)
max_model_id = len(models)-1

esrgran_interpreter = Generator.load_ESRGAN_model()

images = []

# for each model generate an image with noise i (from EEG data)
for i in range(len(noise_files)):
	try:
		print(f"Reading EEG noise/{noise_files[i]}")
		#transform EEG waves data 
		df = pd.read_csv(f"noise/{noise_files[i]}")
		df = utils.transform_EEG(df, 10, (1,100), 2)

		#generate image with model i 
		model_id = random.randint(0, max_model_id)
		print(f'Generating image with model {models[model_id]}')
		generated_image = Generator.generate_ESRGAN_image(df, load_models[model_id], esrgran_interpreter, f'output{i}.png')

		#save generated image
		print(f'Saving image {i}')
		image = Image.fromarray(generated_image)
		image.save(f'results/output{i}.png')
		images.append(image)
	except Exception as ex:
		print(ex)


#utils.save_mosaic(images, 'mosaic.png', rowsize=4, colsize=4, imgShape=512)
