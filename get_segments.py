"""
Description:
  Given a seismogram and a FeatureCollection of intersections, calculates
  the segments that compose the signal. Outputs a geojson FeatureCollection
  with one feature per segment. Each feature has a LineString geometry and
  properties (TODO: what properties?).

Usage:
  get_segments.py --image <filename> --intersections <filename> --output <filename> [--debug]
  get_segments.py -h | --help

Options:
  -h --help                   Show this screen.
  --image <filename>          Filename of grayscale input image.
  --intersections <filename>  Filename of intersection metadata.
  --output <filename>         Filename of geojson output.

"""

from docopt import docopt

def get_segments(in_file, out_file, intersections_file):
  from lib.timer import timeStart, timeEnd
  from lib.load_image import get_image
  from lib.load_geojson import get_features
  from lib.segment_detection import get_segments
  from lib.segment_detection import save_segments_as_geojson

  timeStart("get segments")

  timeStart("read image")
  image = get_image(in_file)
  timeEnd("read image")

  intersections = get_features(intersections_file)

  timeStart("calculate segments")
  segments = get_segments(image, intersections)
  timeEnd("calculate segments")

  save_segments_as_geojson(segments, out_file)
  timeEnd("get segments")

if __name__ == '__main__':
  arguments = docopt(__doc__)
  in_file = arguments["--image"]
  intersections_file = arguments["--intersections"]
  out_file = arguments["--output"]

  if (in_file and out_file and intersections_file):
    get_segments(in_file, out_file, intersections_file)
  else:
    print(arguments)
