"""
Description:
  Given a grayscale seismogram and a geojson Polygon feature
  representing the seismogram's region-of-interest, estimates
  the meanlines of the seismogram data, and saves as a geojson
  FeatureCollection of features with LineString geometries.

Usage:
  get_meanlines.py --roi <filename> --image <filename> --output <filename> [--debug <directory>]
  get_meanlines.py -h | --help

Options:
  -h --help            Show this screen.
  --roi <filename>     Filename of geojson Polygon representing region-of-interest.
  --image <filename>   Filename of grayscale seismogram.
  --output <filename>  Filename of geojson output.
  --debug <directory>  Save intermediate steps as images for inspection in <directory>.

"""

from docopt import docopt

if __name__ == '__main__':
    arguments = docopt(__doc__)
    in_file = arguments["--image"]
    out_file = arguments["--output"]
    roi_file = arguments["--roi"]
    debug_dir = arguments["--debug"]

    if (in_file and out_file and roi_file):
      from lib.timer import timeStart, timeEnd
      from lib.load_image import get_image
      from lib.load_geojson import get_features
      from lib.polygon_mask import mask_image
      from lib.meanline_detection import get_meanlines
      from lib.meanline_detection import save_meanlines_as_geojson

      timeStart("DONE", immediate=False)

      timeStart("read image")
      image = get_image(in_file)
      timeEnd("read image")

      roi_polygon = get_features(roi_file)["geometry"]["coordinates"]

      timeStart("mask image")
      masked_image = mask_image(image, roi_polygon)
      timeEnd("mask image")
      
      meanlines = get_meanlines(masked_image, debug_dir=debug_dir)
      save_meanlines_as_geojson(meanlines, out_file)

      timeEnd("DONE", immediate=False)
    else:
      print(arguments)
      
