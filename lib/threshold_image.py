from skimage.filters import threshold_otsu

def threshold_image(grayscale_image):
  threshold_value = threshold_otsu(grayscale_image)
  black_and_white_image = (grayscale_image > threshold_value)
  return black_and_white_image