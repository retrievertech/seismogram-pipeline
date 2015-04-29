"""
Description:
  Calculates intersections in a black and white image and
  saves a geojson FeatureCollection of features with Point
  geometries and 'radius' properties.

Usage:
  get_intersections.py --roi <filename> --thresh-image <filename> --output <filename> [--debug]
  get_intersections.py -h | --help

Options:
  -h --help                  Show this screen.
  --roi <filename>           Filename of geojson Polygon representing region-of-interest.
  --thresh-image <filename>  Filename of black and white input image.
  --output <filename>        Filename of geojson output.
  --debug                    Save image showing intersections in debug/intersections.png.

"""

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
    in_file = arguments["--thresh-image"]
    roi_file = arguments["--roi"]
    out_file = arguments["--output"]
    debug = arguments["--debug"]
    debug_path = "debug/intersections.png"

    if (in_file and out_file):
      from lib.timer import timeStart, timeEnd
      from lib.intersection_detection import find_intersections
      from lib.load_image import get_image
      from lib.load_geojson import get_features
      from lib.polygon_mask import mask_image

      timeStart("DONE", immediate=False)

      timeStart("read image")
      grayscale_image = get_image(in_file)
      timeEnd("read image")

      roi_polygon = get_features(roi_file)["geometry"]["coordinates"]

      timeStart("mask image")
      masked_image = mask_image(grayscale_image, roi_polygon)
      timeEnd("mask image")

      intersections = find_intersections(masked_image)

      timeStart("saving to "+ out_file)
      intersections.exportAsGeoJSON(out_file)
      timeEnd("saving to "+ out_file)

      if debug:
        timeStart("saving to "+ debug_path)
        intersections.exportAsImage(debug_path)
        timeEnd("saving to "+ debug_path)

      timeEnd("DONE", immediate=False)
    else:
      print(arguments)
