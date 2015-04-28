"""
Description:
  Calculates the corners of the region of interest in a grayscale
  seismogram image.

Usage:
  get_roi.py --image <filename> --output <filename> [--debug]
  get_roi.py -h | --help

Options:
  -h --help            Show this screen.
  --image <filename>   Filename of grayscale input image.
  --output <filename>  Filename of geojson output.
  -d --debug           Save intermediate steps as images for inspection in debug/.

"""

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
    in_file = arguments["--image"]
    out_file = arguments["--output"]
    debug = arguments["--debug"]

    if (in_file and out_file):
      from lib.timer import timeStart, timeEnd
      from lib.load_image import get_image
      from lib.roi_detection import get_boundary, get_box_lines, get_roi_corners, save_corners_as_geojson

      timeStart("DONE", immediate=False)
      image = get_image(in_file)
      boundary = get_boundary(image, debug=debug)
      lines = get_box_lines(boundary, debug=debug, image=image)
      corners = get_roi_corners(lines, debug=debug, image=image)
      save_corners_as_geojson(corners, out_file)
      timeEnd("DONE", immediate=False)
    else:
      print(arguments)
