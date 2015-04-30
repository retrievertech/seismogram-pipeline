"""
Description:
  Given a list of segments and a list of meanlines, assigns each segment to
  a meanline. Outputs a json object of the form:
    {
      meanline_id: [ segment_id, another_segment_id, ... ],
      ...
    }

Usage:
  get_segment_assignments.py --meanlines <filename> --segments <filename> --output <filename>
  get_segment_assignments.py -h | --help

Options:
  -h --help               Show this screen.
  --meanlines <filename>  Filename of meanline metadata.
  --segments <filename>   Filename of segment metadata.
  --output <filename>     Filename of json output.

"""

from docopt import docopt

def get_segment_assignments(segments_file, meanlines_file, out_file):
  from lib.timer import timeStart, timeEnd
  from lib.load_geojson import get_features
  from lib.segment_assignment import assign_segments_to_meanlines
  from lib.segment_assignment import save_assignments_as_json

  timeStart("DONE", immediate=False)
  segments = get_features(segments_file)
  meanlines = get_features(meanlines_file)
  
  timeStart("assign segments to meanlines")
  assignments = assign_segments_to_meanlines(segments, meanlines)
  timeEnd("assign segments to meanlines")
  
  save_assignments_as_json(assignments, out_file)
  timeEnd("DONE", immediate=False)

if __name__ == '__main__':
  arguments = docopt(__doc__)
  segments_file = arguments["--segments"]
  meanlines_file = arguments["--meanlines"]
  out_file = arguments["--output"]

  if (segments_file and meanlines_file):
    get_segment_assignments(segments_file, meanlines_file, out_file)
  else:
    print(arguments)
