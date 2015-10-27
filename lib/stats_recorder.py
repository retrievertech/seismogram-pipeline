import json

class Record:
  stats = {}

  @classmethod
  def record(cls, key, value):
    cls.stats[key] = value

  @classmethod
  def export_as_json(cls, filename):
    try:
      with open(filename, "rw") as myfile:
        data = myfile.read()
        prev_stats = json.loads(data)
    except IOError:
      # no previous stats recorded, so
      # initialize an empty dict of stats
      prev_stats = {key: [] for key in cls.stats}

    # append all the new stats to the old stats
    for key, record in cls.stats.iteritems():
      try:
        prev_stats[key].append(record)
      except KeyError:
        print "WARN: Failed to save a new statistic, %s, to an existing record" % key

    with open(filename, "w") as myfile:
      json.dump(prev_stats, myfile)