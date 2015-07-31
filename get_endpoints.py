# -*- coding: utf-8 -*-
"""
Description:
  Extract segment endpoints from a segments.json file

Usage:
  get_endpoints.py --segments <filename> (--output <filename> | --output_csv <filaname>)
  get_endpoints.py -h | --help

Options:
  -h --help                Show this screen.
  --segments <filename>    Filename of segments.json
  --output <filename>      File to write geojson to.
  --output_csv <filename>  File to write CSV to.
"""

from docopt import docopt
from lib.geojson_io import get_features
from lib.endpoints import get_endpoint_data, generate_geojson, write_geojson, write_csv

if __name__ == '__main__':
  arguments = docopt(__doc__)
  segments_file = arguments["--segments"]
  geojson_out_file = arguments["--output"]
  csv_out_file = arguments["--output_csv"]

  features = get_features(segments_file)
  data = get_endpoint_data(features)

  if geojson_out_file is not None:
    write_geojson(geojson_out_file, generate_geojson(data))
  else:
    write_csv(csv_out_file, data)
