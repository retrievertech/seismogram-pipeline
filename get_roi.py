"""
Description:
  Calculates the corners of the region of interest in a grayscale
  seismogram image.

Usage:
  get_roi.py --image <filename> [--output <filename>] [--scale <scale>] [--debug <directory>]
  get_roi.py -h | --help

Options:
  -h --help            Show this screen.
  --image <filename>   Filename of grayscale input image.
  --output <filename>  Filename of geojson output.
  --scale <scale>      1 for a full-size seismogram, 0.25 for quarter-size, etc. [default: 1]
  --debug <directory>  Save intermediate steps as images for inspection in <directory>.

"""

from docopt import docopt

def get_roi(in_file, out_file, scale=1, debug_dir=False):
  if debug_dir:
    from lib.dir import ensure_dir_exists
    ensure_dir_exists(debug_dir)

  from lib.timer import timeStart, timeEnd
  from lib.load_image import get_image
  from lib.roi_detection import get_boundary, get_box_lines, get_roi_corners, corners_to_geojson
  from lib.geojson_io import save_features

  timeStart("ROI")

  timeStart("read image")
  image = get_image(in_file)
  timeEnd("read image")

  boundary = get_boundary(image, scale=scale, debug_dir=debug_dir)
  lines = get_box_lines(boundary, debug_dir=debug_dir, image=image)
  corners = get_roi_corners(lines, debug_dir=debug_dir, image=image)

  timeStart("convert to geojson")
  corners_as_geojson = corners_to_geojson(corners)
  timeEnd("convert to geojson")

  if debug_dir:
    from lib.polygon_mask import mask_image
    from scipy import misc
    roi_polygon = corners_as_geojson["geometry"]["coordinates"][0]
    timeStart("mask image")
    masked_image = mask_image(image, roi_polygon)
    timeEnd("mask image")
    misc.imsave(debug_dir+"/masked_image.png", masked_image.filled(0))

  if out_file:
    timeStart("saving as geojson")
    save_features(corners_as_geojson, out_file)
    timeEnd("saving as geojson")
  else:
    print corners_as_geojson

  timeEnd("ROI")

if __name__ == '__main__':
  arguments = docopt(__doc__)
  in_file = arguments["--image"]
  out_file = arguments["--output"]
  scale = float(arguments["--scale"])
  debug_dir = arguments["--debug"]

  if (in_file):
    get_roi(in_file, out_file, scale, debug_dir)
  else:
    print(arguments)
