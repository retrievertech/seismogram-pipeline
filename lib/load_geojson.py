from timer import timeStart, timeEnd
import geojson

def get_features(filename):
  timeStart("read file")
  with open(filename, "r") as myfile:
    data = myfile.read()
    features = geojson.loads(data)
    timeEnd("read file")
    return features