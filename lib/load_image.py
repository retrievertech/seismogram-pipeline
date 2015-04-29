from scipy import misc

def get_image(filename):
  grayscale_image = misc.imread(filename, flatten = True)
  return grayscale_image