"""
Description:
  Calculates intersections in a black and white image and
  saves a geojson FeatureCollection of features with Point
  geometries and 'radius' properties.

Usage:
  get_intersections.py --thresh-image <filename> --output <filename>
  get_intersections.py -h | --help

Options:
  -h --help                  Show this screen.
  --thresh-image <filename>  Filename of black and white input image.
  --output <filename>        Filename of geojson output.

"""

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
    in_file = arguments["--thresh-image"]
    out_file = arguments["--output"]

    if (in_file and out_file):
      from src.intersection_detection import find_intersections_from_file_path
      intersections = find_intersections_from_file_path(in_file)
      intersections.exportAsGeoJSON(out_file)
    else:
      print(arguments)
