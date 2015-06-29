# -*- coding: utf-8 -*-
"""
Description:
  Extract segment endpoints from a segments.json file

Usage:
  write_coords.py --segments <filename> --output <filename>
  write_coords.py -h | --help

Options:
  -h --help              Show this screen.
  --segments <filename>  Filename of segments.json
  --output <filename>    File to write to.

"""

from docopt import docopt
import geojson
import csv
import numpy as np
from lib.geojson_io import get_features
from lib.timer import timeStart, timeEnd

#features = get_features('C:\Users\Lowell\Documents\GitHub\seismogram-pipeline\metadata\segments.json')

def get_endpoints(features):
  all_x = []
  all_y = []

  timeStart("get coordinates")
  for feature in features["features"]:
    coordinates = np.array(feature["geometry"]["coordinates"]) # turn the list of coords into a fancy 2D numpy array
    all_x.append(coordinates[:, 0]) # numpy arrays are indexed [row, column], so [:, 0] means "all rows, 0th column"
    all_y.append(coordinates[:, 1])
  timeEnd("get coordinates")

  average_y = []
  std_deviation_y = []
  x1 = []
  x2 = []
  y1 = []
  y2 = []
  startpoints = []
  endpoints = []

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

  segment_data = {
    "type": "FeatureCollection",
    "features": []
  }

  for i in xrange(len(all_y)):
    segment = {
      "geometry": [startpoints[i], endpoints[i]],
      "properties": {
        "average_y": average_y[i],
        "standard_deviation": std_deviation_y[i],
      }
    }
    segment_data["features"].append(segment)

  with open('endpoints.csv', 'wb') as csvfile:
    rowwriter = csv.writer(csvfile, delimiter=',')
    for rows in xrange(len(endpoints)):
      rowwriter = csv.writer(csvfile, delimiter=',')
      rowwriter.writerow(startpoints[rows] + endpoints[rows])

  #coord_length = []
  #for size in xrange(len(all_x)):
  #  coord_length.append(len(all_x[size]))
  #coord_histogram = np.histogram(coord_length, bins = range(0, np.max(coord_length)))

  return segment_data

if __name__ == '__main__':
  arguments = docopt(__doc__)
  print arguments
  segments_file = arguments["--segments"]
  print segments_file
  out_file = arguments["--output"]
  print out_file

  features = get_features(segments_file)
  segment_data = get_endpoints(features)

  with open(out_file, 'w') as outfile:
    geojson.dump(segment_data, outfile)
