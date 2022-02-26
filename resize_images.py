import generator
from PIL import Image
import tensorflow as tf
import os


esrgran_interpreter,esrgran_input_details, esrgran_output_details = generator.load_model(model_path='ESRGAN.tflite')

images_path = 'images'

for img in os.listdir(f'{images_path}/'):
  try:
    generated_image = tf.io.read_file(f'{images_path}/{img}')
    generated_image = tf.image.decode_jpeg(generated_image)
    generated_image = tf.expand_dims(generated_image, axis=0)
    generated_image = tf.cast(generated_image, tf.float32)
    
    print('Invoke esrgran')
    esrgran_interpreter.set_tensor(esrgran_input_details['index'], generated_image)
    esrgran_interpreter.invoke()

    # Extract the output and postprocess it
    print('Process output from esrgran')
    generated_image = esrgran_interpreter.get_tensor(esrgran_output_details['index'])
    generated_image = tf.squeeze(generated_image, axis=0)
    generated_image = tf.clip_by_value(generated_image, 0, 255)
    generated_image = tf.round(generated_image)
    generated_image = tf.cast(generated_image, tf.uint8)
    generated_image = generated_image.numpy()
    generated_image = Image.fromarray(generated_image)
    os.remove(f'{images_path}/{img}')
    generated_image.save(f'{images_path}/{img}.png')
  except Exception as ex:
    print(ex)
  

