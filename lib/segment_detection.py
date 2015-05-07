from timer import timeStart, timeEnd

from numpy.random import rand, randint
import geojson
import math

def get_segments(image, intersections):
  # Generate dummy segments
  def random_phase():
    return rand() * math.pi * 2

  def random_freq():
    return randint(1, 20) * math.pi * 2 / shape[1]

  def random_amplitude():
    return randint(10, shape[0]/4)

  def random_offset():
    return randint(shape[0]/4, shape[0])

  shape = image.shape
  num_traces = 24
  line_array = []
  for i in range(num_traces):
    phase_1, phase_2 = random_phase(), random_phase()
    freq_1, freq_2 = random_freq(), random_freq()
    amp_1, amp_2 = random_amplitude(), random_amplitude()
    offset = random_offset()
    line_array.append([ (x, offset + int(amp_1*math.sin(x * freq_1 + phase_1) + amp_2*math.sin(x * freq_2 + phase_2))) for x in range(shape[1]) ])
  
  return line_array

def save_segments_as_geojson(segments, filepath):
  timeStart("saving to "+ filepath)
  features = [ geojson.Feature(geometry = geojson.LineString(line), id = idx) for idx, line in enumerate(segments) ]
  collection = geojson.FeatureCollection(features)
  with open(filepath, 'w') as outfile:
    geojson.dump(collection, outfile)
  timeEnd("saving to "+ filepath)
