"""
Description:
  Calculates intersections in a black and white image and
  saves a geojson FeatureCollection of features with Point
  geometries and 'radius' properties.

Usage:
  get_intersections.py --roi <filename> --thresh-image <filename> --output <filename> [--debug <directory>]
  get_intersections.py -h | --help

Options:
  -h --help                  Show this screen.
  --roi <filename>           Filename of geojson Polygon representing region-of-interest.
  --thresh-image <filename>  Filename of black and white input image.
  --output <filename>        Filename of geojson output.
  --debug <directory>        Save debug images in <directory>.

"""

from docopt import docopt

def get_intersections(in_file, out_file, roi_file, debug_dir=False):
  if debug_dir:
    from lib.dir import ensure_dir_exists
    ensure_dir_exists(debug_dir)

  from lib.timer import timeStart, timeEnd
  from lib.intersection_detection import find_intersections
  from lib.load_image import get_image
  from lib.load_geojson import get_features
  from lib.polygon_mask import mask_image

  timeStart("DONE", immediate=False)

  timeStart("read image")
  grayscale_image = get_image(in_file)
  timeEnd("read image")

  roi_polygon = get_features(roi_file)["geometry"]["coordinates"][0]

  timeStart("mask image")
  masked_image = mask_image(grayscale_image, roi_polygon)
  timeEnd("mask image")

  intersections = find_intersections(masked_image.filled(False), figure=False)

  timeStart("saving to "+ out_file)
  intersections.exportAsGeoJSON(out_file)
  timeEnd("saving to "+ out_file)

  if debug_dir:
    debug_filepath = debug_dir + "/intersections.png"
    timeStart("saving to "+ debug_filepath)
    intersections.exportAsImage(debug_filepath)
    timeEnd("saving to "+ debug_filepath)

  timeEnd("DONE", immediate=False)

if __name__ == '__main__':
  arguments = docopt(__doc__)
  in_file = arguments["--thresh-image"]
  roi_file = arguments["--roi"]
  out_file = arguments["--output"]
  debug_dir = arguments["--debug"]

  if (in_file and out_file):
    get_intersections(in_file, out_file, roi_file, debug_dir)
  else:
    print(arguments)
