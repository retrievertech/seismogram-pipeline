"""
Description:
  Resize and save an image.

Usage:
  resize_image.py --image <filename> --output <filename> --scale <scale>
  resize_image.py -h | --help

Options:
  -h --help             Show this screen.
  --image <filename>    Path to original image.
  --output <filename>   Path to new image.
  --scale <scale>       1 for a full-size seismogram, 0.25 for quarter-size, etc. [default: 1]

"""

from docopt import docopt
from scipy.misc import imresize, imsave
from lib.load_image import get_image
from lib.timer import timeStart, timeEnd

def resize_image(in_file, out_file, scale):
  timeStart("load image")
  image = get_image(in_file)
  timeEnd("load image")

  timeStart("resize image")
  resized_image = imresize(image, scale)
  timeEnd("resize image")

  timeStart("save image")
  imsave(out_file, resized_image)
  timeEnd("save image")

if __name__ == '__main__':
  arguments = docopt(__doc__)
  in_file = arguments["--image"]
  out_file = arguments["--output"]
  scale = float(arguments["--scale"])

  if (in_file and out_file and scale):
    resize_image(in_file, out_file, scale)
  else:
    print(arguments)
