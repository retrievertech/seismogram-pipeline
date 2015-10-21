import geojson
import json

from debug import Debug

def get_features(filename):
  with open(filename, "r") as myfile:
    data = myfile.read()
    features = geojson.loads(data)
    return features

def save_features(features, filename):
  if Debug.active:
    indent = 2
  else:
    indent = None

  with open(filename, 'w') as outfile:
    geojson.dump(features, outfile, indent=indent)

def save_json(dict, filename):
  if Debug.active:
    indent = 2
  else:
    indent = None

  with open(filename, 'w') as outfile:
    json.dump(dict, outfile, indent=indent)
