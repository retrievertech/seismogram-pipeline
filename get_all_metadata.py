# -*- coding: utf-8 -*-
"""
Description:
  Generate all metadata (ROI, meanlines, intersections, and segments as of 6/10/2015)
  for a single seismogram.

Usage:
  pipeline.py --image <filename> --output <directory> [--stats <filename>] [--scale <scale>] [--debug <directory>] [--fix-seed]
  pipeline.py -h | --help

Options:
  -h --help             Show this screen.
  --image <filename>    Filename of seismogram.
  --output <directory>  Save metadata in <directory>.
  --stats <filename>    Write statistics (e.g. number of meanlines, size of ROI) to <filename>.
                        If <filename> already exists, stats will be appended, not overwritten.
  --scale <scale>       1 for a full-size seismogram, 0.25 for quarter-size, etc. [default: 1]
  --debug <directory>   Save intermediate steps as images for inspection in <directory>.
  --fix-seed            Fix random seed.

"""

from docopt import docopt

def analyze_image(in_file, out_dir, stats_file=False, scale=1, debug_dir=False, fix_seed=False):
  from lib.dir import ensure_dir_exists
  from lib.debug import Debug
  from lib.stats_recorder import Record

  if debug_dir:
    Debug.set_directory(debug_dir)

  if fix_seed:
    Debug.set_seed(1234567890)

  if stats_file:
    Record.activate()

  ensure_dir_exists(out_dir)

  from lib.timer import timeStart, timeEnd

  from lib.load_image import get_grayscale_image, image_as_float
  from skimage.morphology import medial_axis
  from lib.roi_detection import get_roi, corners_to_geojson
  from lib.polygon_mask import mask_image
  from lib.meanline_detection import detect_meanlines, meanlines_to_geojson
  from lib.threshold import flatten_background
  from lib.ridge_detection import find_ridges
  from lib.binarization import binary_image
  from lib.intersection_detection import find_intersections
  from lib.trace_segmentation import get_segments, segments_to_geojson
  from lib.geojson_io import save_features, save_json
  from lib.utilities import encode_labeled_image_as_rgb
  from scipy import misc
  import numpy as np

  paths = {
    "roi": out_dir+"/roi.json",
    "meanlines": out_dir+"/meanlines.json",
    "intersections": out_dir+"/intersections.json",
    "segments": out_dir+"/segments.json",
    "segment_regions": out_dir+"/segment_regions.png",
    "segment_assignments": out_dir+"/segment_assignments.json"
  }

  timeStart("get all metadata")

  timeStart("read image")
  img_gray = image_as_float(get_grayscale_image(in_file))
  timeEnd("read image")

  print "\n--ROI--"
  timeStart("get region of interest")
  corners = get_roi(img_gray, scale=scale)
  timeEnd("get region of interest")

  timeStart("convert roi to geojson")
  corners_as_geojson = corners_to_geojson(corners)
  timeEnd("convert roi to geojson")

  timeStart("saving roi as geojson")
  save_features(corners_as_geojson, paths["roi"])
  timeEnd("saving roi as geojson")


  print "\n--MASK IMAGE--"
  roi_polygon = corners_as_geojson["geometry"]["coordinates"][0]

  timeStart("mask image")
  masked_image = mask_image(img_gray, roi_polygon)
  timeEnd("mask image")

  Debug.save_image("main", "masked_image", masked_image.filled(0))

  if Record.active:
    non_masked_values = 255 * masked_image.compressed()
    bins = np.arange(257)
    image_hist, _ = np.histogram(non_masked_values, bins=bins)
    Record.record("roi_intensity_hist", image_hist.tolist())


  print "\n--MEANLINES--"
  meanlines = detect_meanlines(masked_image, corners, scale=scale)

  timeStart("convert meanlines to geojson")
  meanlines_as_geojson = meanlines_to_geojson(meanlines)
  timeEnd("convert meanlines to geojson")

  timeStart("saving meanlines as geojson")
  save_features(meanlines_as_geojson, paths["meanlines"])
  timeEnd("saving meanlines as geojson")


  print "\n--FLATTEN BACKGROUND--"
  img_dark_removed, background = \
    flatten_background(masked_image, prob_background=0.95,
                       return_background=True, img_gray=img_gray)

  Debug.save_image("main", "flattened_background", img_dark_removed)

  masked_image = None

  print "\n--RIDGES--"
  timeStart("get horizontal and vertical ridges")
  ridges_h, ridges_v = find_ridges(img_dark_removed, background)
  ridges = ridges_h | ridges_v
  timeEnd("get horizontal and vertical ridges")


  print "\n--THRESHOLDING--"
  timeStart("get binary image")
  img_bin = binary_image(img_dark_removed, markers_trace=ridges,
               markers_background=background)
  timeEnd("get binary image")

  img_dark_removed = None
  background = None

  print "\n--SKELETONIZE--"
  timeStart("get medial axis skeleton and distance transform")
  img_skel, dist = medial_axis(img_bin, return_distance=True)
  timeEnd("get medial axis skeleton and distance transform")

  Debug.save_image("skeletonize", "skeleton", img_skel)


  print "\n--INTERSECTIONS--"
  intersections = find_intersections(img_bin, img_skel, dist, figure=False)

  timeStart("convert to geojson")
  intersection_json = intersections.asGeoJSON()
  timeEnd("convert to geojson")

  timeStart("saving intersections as geojson")
  save_features(intersection_json, paths["intersections"])
  timeEnd("saving intersections as geojson")

  timeStart("convert to image")
  intersection_image = intersections.asImage()
  timeEnd("convert to image")

  Debug.save_image("intersections", "intersections", intersection_image)


  print "\n--SEGMENTS--"
  timeStart("get segments")
  segments, labeled_regions = \
    get_segments(img_gray, img_bin, img_skel, dist, intersection_image,
                 ridges_h, ridges_v, figure=True)
  timeEnd("get segments")

  timeStart("encode labels as rgb values")
  rgb_segments = encode_labeled_image_as_rgb(labeled_regions)
  timeEnd("encode labels as rgb values")

  timeStart("save segment regions")
  misc.imsave(paths["segment_regions"], rgb_segments)
  timeEnd("save segment regions")

  timeStart("convert centerlines to geojson")
  segments_as_geojson = segments_to_geojson(segments)
  timeEnd("convert centerlines to geojson")

  timeStart("saving centerlines as geojson")
  save_features(segments_as_geojson, paths["segments"])
  timeEnd("saving centerlines as geojson")

  #return (img_gray, ridges, img_bin, intersections, img_seg)
  # return segments
  # detect center lines

  # connect segments

  # output data

  time_elapsed = timeEnd("get all metadata")

  Record.record("time_elapsed", float("%.2f" % time_elapsed))

  if (stats_file):
    Record.export_as_json(stats_file)

  # TODO: refactor this into some sort of status module.
  # For now, since this is our only problematic status,
  # it's hard to know what to generalize. Eventually
  # we might want to flag several different statuses
  # for specific conditions.
  if (len(segments) > 10000):
    print "STATUS>>>problematic<<<"
  else:
    print "STATUS>>>complete<<<"

if __name__ == '__main__':
  arguments = docopt(__doc__)
  in_file = arguments["--image"]
  out_dir = arguments["--output"]
  stats_file = arguments["--stats"]
  scale = float(arguments["--scale"])
  debug_dir = arguments["--debug"]
  fix_seed = arguments["--fix-seed"]

  if (in_file and out_dir):
    segments = analyze_image(in_file, out_dir, stats_file, scale, debug_dir, fix_seed)
  else:
    print(arguments)
