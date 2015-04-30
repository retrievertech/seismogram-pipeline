"""
Description:
  Calculates the corners of the region of interest in a grayscale
  seismogram image.

Usage:
  get_roi.py --image <filename> --output <filename> [--debug <directory>]
  get_roi.py -h | --help

Options:
  -h --help            Show this screen.
  --image <filename>   Filename of grayscale input image.
  --output <filename>  Filename of geojson output.
  --debug <directory>  Save intermediate steps as images for inspection in <directory>.

"""

from docopt import docopt

def get_roi(in_file, out_file, debug_dir=False):
  if debug_dir:
    from lib.dir import ensure_dir_exists
    ensure_dir_exists(debug_dir)

  from lib.timer import timeStart, timeEnd
  from lib.load_image import get_image
  from lib.roi_detection import get_boundary, get_box_lines, get_roi_corners, save_corners_as_geojson

  timeStart("DONE", immediate=False)

  timeStart("read image")
  image = get_image(in_file)
  timeEnd("read image")

  boundary = get_boundary(image, debug_dir=debug_dir)
  lines = get_box_lines(boundary, debug_dir=debug_dir, image=image)
  corners = get_roi_corners(lines, debug_dir=debug_dir, image=image)
  save_corners_as_geojson(corners, out_file)

  timeEnd("DONE", immediate=False)

if __name__ == '__main__':
  arguments = docopt(__doc__)
  in_file = arguments["--image"]
  out_file = arguments["--output"]
  debug_dir = arguments["--debug"]

  if (in_file and out_file):
    get_roi(in_file, out_file, debug_dir)
  else:
    print(arguments)
