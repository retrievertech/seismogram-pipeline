from skimage import io, img_as_float

def get_image(filename):
  grayscale_image = io.imread(filename, as_grey=True)
  return img_as_float(grayscale_image)
