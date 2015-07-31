# -*- coding: utf-8 -*-
"""

Description:
  Assign segments to meanlines based on average y values.

Usage:
  assign_segments.py --segments <filename> --meanlines <filename> --output <filename>
  assign_segments.py -h | --help

Options:
  -h --help                Show this screen.
  --segments <filename>    The segments json.
  --meanlines <filename>   The meanlines json.
  --output <filename>      File to write geojson to.
"""
from docopt import docopt
from lib.geojson_io import get_features
import lib.endpoints
from lib.segment_assignment import assign_segments_to_meanlines, save_assignments_as_json

"""as of now, it is in a format where it accesses specific files on my computer. I would appreciate if somebody
could help me turn it into a command line usable format"""

if __name__ == '__main__':
    args = docopt(__doc__)
    segments_file = args['--segments']
    meanlines_file = args['--meanlines']
    output_file = args['--output']

    segments = get_features(segments_file)
    meanlines = get_features(meanlines_file)
    endpoints = lib.endpoints.generate_geojson(lib.endpoints.get_endpoint_data(segments))

    assign = assign_segments_to_meanlines(segments, meanlines, endpoints)
    save_assignments_as_json(assign, output_file)
