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

def resize_image(in_file, out_file, scale):
  image = get_image(in_file)
  resized_image = imresize(image, scale)
  imsave(out_file, resized_image)

if __name__ == '__main__':
  arguments = docopt(__doc__)
  in_file = arguments["--image"]
  out_file = arguments["--output"]
  scale = float(arguments["--scale"])

  if (in_file and out_file and scale):
    resize_image(in_file, out_file, scale)
  else:
    print(arguments)
