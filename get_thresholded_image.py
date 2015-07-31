"""
Description:
  Saves a thresholded copy of the input image. Currently uses Otsu; might get more advanced later.

Usage:
  get_thresholded_image.py --image <filename> --output <filename>
  get_thresholded_image.py -h | --help

Options:
  -h --help            Show this screen.
  --image <filename>   Filename of grayscale input image.
  --output <filename>  Filename of black and white output image.

"""

from docopt import docopt

def get_thresholded_image(in_file, out_file):
  from lib.timer import timeStart, timeEnd
  from lib.otsu_threshold_image import otsu_threshold_image
  from lib.load_image import get_image
  from scipy import misc

  timeStart("read image")
  grayscale_image = get_image(in_file)
  timeEnd("read image")

  timeStart("threshold image")
  thresholded_image = otsu_threshold_image(grayscale_image)
  timeEnd("threshold image")

  timeStart("save image")
  misc.imsave(out_file, thresholded_image)
  timeEnd("save image")

if __name__ == '__main__':
  arguments = docopt(__doc__)
  in_file = arguments["--image"]
  out_file = arguments["--output"]

  if (in_file and out_file):
    get_thresholded_image(in_file, out_file)
  else:
    print(arguments)
