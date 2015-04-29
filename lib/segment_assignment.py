from timer import timeStart, timeEnd

from random import sample, randint
import json

def assign_segments_to_meanlines(segments, meanlines):
  # Generate dummy assignments for now
  meanline_ids = [line.id for line in meanlines.features]
  segment_ids = [segment.id for segment in segments.features]
  avg_segments_per_meanline = len(segment_ids) / len(meanline_ids)
  assignments = {}
  for meanline_id in meanline_ids:
    assignments[meanline_id] = [segment_ids.pop(i) for i in sorted(sample(range(len(segment_ids)), randint(0, avg_segments_per_meanline)), reverse=True)]
  return assignments

def save_assignments_as_json(assignments, filepath):
  timeStart("saving to "+ filepath)
  with open(filepath, 'w') as outfile:
    json.dump(assignments, outfile)
  timeEnd("saving to "+ filepath)
