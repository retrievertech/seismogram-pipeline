"""
Description:
  Generates all metadata for a seismogram:
    roi.json
    meanlines.json
    intersections.json
    segments.json
    segment_assignments.json

Usage:
  get_all_metadata.py --image <filename> --output <directory> [--scale <scale>]
  get_all_metadata.py -h | --help

Options:
  -h --help             Show this screen.
  --image <filename>    Filename of seismogram.
  --output <directory>  Directory in which to save metadata.
  --scale <scale>       1 for a full-size seismogram, 0.25 for quarter-size, etc. [default: 1]

"""

from docopt import docopt

def get_all_metadata(in_file, out_dir, scale=1):
  from lib.dir import ensure_dir_exists
  ensure_dir_exists(out_dir)

  from lib.timer import timeStart, timeEnd
  from get_thresholded_image import get_thresholded_image
  from get_roi import get_roi
  from get_meanlines import get_meanlines
  from get_intersections import get_intersections
  from get_segments import get_segments
  from get_segment_assignments import get_segment_assignments

  paths = {
    "thresholded": out_dir+"/thresholded.png",
    "roi": out_dir+"/roi.json",
    "meanlines": out_dir+"/meanlines.json",
    "intersections": out_dir+"/intersections.json",
    "segments": out_dir+"/segments.json",
    "segment_assignments": out_dir+"/segment_assignments.json"
  }

  timeStart("ALL DONE", immediate=False)

  print "\n--ROI--"
  get_roi(in_file, paths["roi"], scale)
  print "\n--MEANLINES--"
  get_meanlines(in_file, paths["meanlines"], paths["roi"], scale)
  print "\n--INTERSECTIONS--"
  # TODO: don't write the thresholded image to a file
  get_thresholded_image(in_file, paths["thresholded"])
  get_intersections(paths["thresholded"], paths["intersections"], paths["roi"])
  print "\n--SEGMENTS--"
  get_segments(in_file, paths["segments"], paths["intersections"])
  print "\n--SEGMENT ASSIGNMENTS--"
  get_segment_assignments(paths["segments"], paths["meanlines"], paths["segment_assignments"])

  print "\n"
  timeEnd("ALL DONE", immediate=False)

if __name__ == '__main__':
  arguments = docopt(__doc__)
  in_file = arguments["--image"]
  out_dir = arguments["--output"]
  scale = float(arguments["--scale"])

  if (in_file and out_dir):
    get_all_metadata(in_file, out_dir, scale)
  else:
    print(arguments)
