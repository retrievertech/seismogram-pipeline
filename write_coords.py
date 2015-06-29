import geojson
import numpy as np
from lib.geojson_io import get_features

features = get_features('C:\Users\Lowell\Documents\GitHub\seismogram-pipeline\metadata\segments.json')
from lib.timer import timeStart, timeEnd

x_coords = []
y_coords = []
all_x = []
all_y = []
timeStart("get coordinates")
for feature in features["features"]:
    coordinates = feature["geometry"]["coordinates"]
    for coord in coordinates:
        x_coords.append(coord[0])
        y_coords.append(coord[1])
    all_x.append(x_coords)
    x_coords = []
    all_y.append(y_coords)
    y_coords = []
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

segment_data = {"features": []}

for update_dict in xrange(len(all_y)):
    each_segment = {"geometry": {"average_y": 0, "standard_deviation": 0, "startpoints": [], "endpoints": []}}
    each_segment["geometry"]["average_y"] = average_y[update_dict]
    each_segment["geometry"]["standard_deviation"] = std_deviation_y[update_dict]
    each_segment["geometry"]["startpoints"] = startpoints[update_dict]
    each_segment["geometry"]["endpoints"] = endpoints[update_dict]
    segment_data["features"].append(each_segment)

import csv
with open('endpoints.csv', 'wb') as csvfile:
    rowwriter = csv.writer(csvfile, delimiter=',')
    for rows in xrange(len(endpoints)):
        rowwriter = csv.writer(csvfile, delimiter=',')
        rowwriter.writerow(startpoints[rows] + endpoints[rows])

coord_length = []
for size in xrange(len(all_x)):
    coord_length.append(len(all_x[size]))

coord_histogram = np.histogram(coord_length, bins = range(0, np.max(coord_length)))

with open('segment_data.json', 'w') as outfile:
    geojson.dump(segment_data, outfile)
