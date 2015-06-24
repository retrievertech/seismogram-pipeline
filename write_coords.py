# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 15:58:38 2015

@author: Lowell
"""

import geojson

def get_features(filename):
  with open(filename, "r") as myfile:
    data = myfile.read()
    features = geojson.loads(data)
    return features

def save_features(features, filename):
  with open(filename, 'w') as outfile:
    geojson.dump(features, outfile)

features = get_features('C:\Users\Lowell\Documents\GitHub\seismogram-pipeline\metadata\segments.json')
from lib.timer import timeStart, timeEnd
x_coords = []
y_coords = []
all_x = []
all_y = []
timeStart("get coordinates")
for dicts in xrange(len(get_features('C:\Users\Lowell\Documents\GitHub\seismogram-pipeline\metadata\segments.json')["features"])):
    timeStart("coordinate dict")
    for coords in xrange(len(get_features('C:\Users\Lowell\Documents\GitHub\seismogram-pipeline\metadata\segments.json')["features"][dicts]["geometry"]["coordinates"])):
        timeStart("coordinate")
        coordinate = features["features"][dicts]["geometry"]["coordinates"][coords]
        x_coords.append(coordinate[0])
        y_coords.append(coordinate[1])
        timeEnd("coordinate")
    all_x.append(x_coords)
    x_coords = []
    all_y.append(y_coords)
    y_coords = []
    timeEnd("coordinate dict")
timeEnd("get coordinates")

"""for pack in xrange(len(all_x)):
    all_x[pack] = str(all_x[pack])
    all_y[pack] = str(all_y[pack])"""


