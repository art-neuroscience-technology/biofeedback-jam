import matplotlib.pyplot as plt

plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

images = ['models/128/results_128/output0.png',
 'models/128/results_128/output1.png', 'models/128/results_128/output2.png']

plt.axis('off')
img = None

for f in images:
   im = plt.imread(f)
   if img is None:
      img = plt.imshow(im, interpolation='nearest')
      plt.pause(3)
   else:
      img.set_data(im)
   plt.pause(3)
   plt.draw()