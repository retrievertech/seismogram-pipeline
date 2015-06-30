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
import geojson
import csv
import numpy as np
from lib.geojson_io import get_features
from lib.timer import timeStart, timeEnd
from geojson import Feature, FeatureCollection, LineString

def get_endpoint_data(features):
  """
  Given a parsed GeoJson of segment data, it returns a raw data dictionary
  of the start and endpoints of all segments as well as averages and std deviations
  on the y axis.
  """
  all_x = []
  all_y = []
  average_y = []
  std_deviation_y = []
  startpoints = []
  endpoints = []

  timeStart("get coordinates")
  for feature in features["features"]:
    coordinates = np.array(feature["geometry"]["coordinates"]) # turn the list of coords into a fancy 2D numpy array
    all_x.append(coordinates[:, 0]) # numpy arrays are indexed [row, column], so [:, 0] means "all rows, 0th column"
    all_y.append(coordinates[:, 1])
  timeEnd("get coordinates")

  for values in xrange(len(all_y)):
    average_y.append(np.mean(all_y[values]))
    std_deviation_y.append(np.std(all_y[values]))

  for starts in xrange(len(all_y)):
    x1 = all_x[starts][0]
    y1 = all_y[starts][0]
    x2 = all_x[starts][len(all_x[starts])-1]
    y2 = all_y[starts][len(all_y[starts])-1]
    startpoint = [x1, y1]
    endpoint = [x2, y2]
    startpoints.append(startpoint)
    endpoints.append(endpoint)

  return {
    "startpoints": startpoints,
    "endpoints": endpoints,
    "average_y": average_y,
    "std_deviation_y": std_deviation_y
  }

def generate_geojson(data):
  """
  Given a data dictionary (generated by get_endpoint_data), returns a GeoJson object of the data.
  """
  def segment(i):
    return Feature(
      geometry = LineString([data["startpoints"][i], data["endpoints"][i]]),
      properties = {
        "average_y": data["average_y"][i],
        "standard_deviation": data["std_deviation_y"][i]
      }
    )

  return FeatureCollection(map(segment, xrange(len(data["endpoints"]))))

def write_geojson(out_filename, geojson_data):
  """
  Writes the GeoJson to an output file.
  """
  with open(out_filename, 'w') as outfile:
    geojson.dump(geojson_data, outfile)

def write_csv(out_filename, data):
  """
  Writes the data out into a CSV file.
  """
  with open(out_filename, 'w') as csvfile:
    rowwriter = csv.writer(csvfile, delimiter=',')
    for i in xrange(len(data["endpoints"])):
      rowwriter = csv.writer(csvfile, delimiter=',')
      rowwriter.writerow(data["startpoints"][i] + data["endpoints"][i])

#coord_length = []
#for size in xrange(len(all_x)):
#  coord_length.append(len(all_x[size]))
#coord_histogram = np.histogram(coord_length, bins = range(0, np.max(coord_length)))

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
