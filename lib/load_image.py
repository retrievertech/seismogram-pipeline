from skimage import io, img_as_float

def get_image_as_float(img):
  return img_as_float(img)

def get_grayscale_image(filename):
  grayscale_image = io.imread(filename, as_grey=True)
  return grayscale_image
