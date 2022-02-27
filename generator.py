from PIL import Image
import numpy as np
from numpy.random import randn
import math
import os
from tflite_runtime.interpreter import Interpreter

def load_model(model_path):
    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]
    return interpreter, input_details, output_details

class Generator:

  def __init__(self, models_path, images_path):
    self.images_path = images_path

    # init models
    self.models_path = models_path
    self.models = []
    for model in os.listdir(models_path):
      self.models.append(load_model(f'{models_path}/{model}'))

  def get_models_count(self):
    return len(self.models)


  def predict(self, noise, interpreter_id, identifier):
    print('Gengerate image with GAN model')
#     noise = tf.convert_to_tensor(noise, dtype=tf.float32)
    noise = noise.astype(np.float32)
    interpreter = self.models[interpreter_id]
    interpreter[0].set_tensor(interpreter[1]['index'], noise)
    interpreter[0].invoke()
    generated_image = interpreter[0].get_tensor(interpreter[2]['index'])
    generated_image = 0.5 * generated_image + 0.5
    generated_image = generated_image * 255
    generated_image = generated_image.reshape(128,128,3).astype(np.uint8)
    Image.fromarray(generated_image).save(f'{self.images_path}/{identifier}.png')

