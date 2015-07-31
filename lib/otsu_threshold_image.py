from skimage.filters import threshold_otsu
from numpy.ma.core import MaskedArray

def otsu_threshold_image(grayscale_image):
  if (type(grayscale_image) is MaskedArray):
    threshold_value = threshold_otsu(grayscale_image.compressed())
  else:
    threshold_value = threshold_otsu(grayscale_image)
  black_and_white_image = (grayscale_image > threshold_value)
  return black_and_white_image
