from timer import timeStart, timeEnd

from numpy.random import rand, randint
import geojson

def get_segments(image, intersections):
  # Generate dummy segments for now
  shape = image.shape
  min_num_points = 3
  max_num_points = 15
  num_lines = randint(50, 200)
  line_array = [(shape * rand(randint(min_num_points, max_num_points), 2)).astype(int) for i in range(num_lines)]
  line_array = [map(tuple, line) for line in line_array]
  return line_array

def save_segments_as_geojson(segments, filepath):
  timeStart("saving to "+ filepath)
  for line in segments:
    print line
  segment_features = [ geojson.Feature(geometry = geojson.LineString(line)) for line in segments ]
  collection = geojson.FeatureCollection(segment_features)
  with open(filepath, 'w') as outfile:
    geojson.dump(collection, outfile)
  timeEnd("saving to "+ filepath)
