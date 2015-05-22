import geojson

def get_features(filename):
  with open(filename, "r") as myfile:
    data = myfile.read()
    features = geojson.loads(data)
    return features

def save_features(features, filename):
  with open(filename, 'w') as outfile:
    geojson.dump(features, outfile)
