from timer import timeStart, timeEnd
from scipy import misc

def get_image(filename):
  timeStart("read image")
  grayscale_image = misc.imread(filename, flatten = True)
  timeEnd("read image")
  return grayscale_image