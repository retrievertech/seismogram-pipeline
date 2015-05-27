# -*- coding: utf-8 -*-
"""
Description:

Usage:
  pipeline.py --image <filename> --output <directory> [--scale <scale>] [--debug <directory>]
  pipeline.py -h | --help

Options:
  -h --help             Show this screen.
  --image <filename>    Filename of seismogram.
  --output <directory>  Save metadata in <directory>.
  --scale <scale>       1 for a full-size seismogram, 0.25 for quarter-size, etc. [default: 1]
  --debug <directory>   Save intermediate steps as images for inspection in <directory>.

"""

from docopt import docopt

def analyze_image(in_file, out_dir, scale=1, debug_dir=False):
  from lib.dir import ensure_dir_exists
  
  if debug_dir:
    ensure_dir_exists(debug_dir)

  ensure_dir_exists(out_dir)

  from lib.timer import timeStart, timeEnd

  from lib.load_image import get_image
  from skimage.morphology import medial_axis

  from lib.roi_detection import get_boundary, get_box_lines, get_roi_corners, corners_to_geojson
  from lib.polygon_mask import mask_image
  from lib.threshold import flatten_background
  from lib.ridge_detection import find_ridges
  from lib.binarization import local_min, binary_image
  from lib.intersection_detection import find_intersections
  from lib.trace_segmentation import get_segments, segments_to_geojson
  from lib.geojson_io import save_features
  from scipy import misc

  timeStart("get all metadata")


  timeStart("read image")
  img_gray = get_image(in_file)
  timeEnd("read image")

  print "\n--ROI--"
  timeStart("get region of interest")
  boundary = get_boundary(img_gray, scale=scale, debug_dir=debug_dir)
  lines = get_box_lines(boundary, debug_dir=debug_dir, image=img_gray)
  corners = get_roi_corners(lines, debug_dir=debug_dir, image=img_gray)
  roi_polygon = corners_to_geojson(corners)["geometry"]["coordinates"][0]
  masked_image = mask_image(img_gray, roi_polygon)
  timeEnd("get region of interest")

  if debug_dir:
    misc.imsave(debug_dir+"/masked_image.png", masked_image.filled(0))

  print "\n--FLATTEN BACKGROUND--"
  img_dark_removed, dark_pixels = flatten_background(masked_image, 0.95, 
                             return_background=True)
  
  print "\n--RIDGES--"
  timeStart("get horizontal and vertical ridges")
  background = dark_pixels | local_min(img_gray) | masked_image.mask
  ridges_h, ridges_v = find_ridges(img_dark_removed, background)
  ridges = ridges_h | ridges_v
  timeEnd("get horizontal and vertical ridges")
  
  print "\n--THRESHOLDING--"
  timeStart("get binary image")
  img_bin = binary_image(img_dark_removed, markers_trace=ridges,
               markers_background=background)
  timeEnd("get binary image")
  
  print "\n--SKELETONIZE--"
  timeStart("get medial axis skeleton and distance transform")
  img_skel, dist = medial_axis(img_bin, return_distance=True)
  timeEnd("get medial axis skeleton and distance transform")

  print "\n--INTERSECTIONS--"
  intersections = find_intersections(img_bin, img_skel, dist)
  
  print "\n--SEGMENTS--"
  timeStart("get segments")
  segments = get_segments(img_gray, img_bin, img_skel, dist, intersections,
              ridges_h, ridges_v)
  timeEnd("get segments")
  
  timeStart("convert segments to geojson")
  segments_as_geojson = segments_to_geojson(segments)
  timeEnd("convert segments to geojson")
  
  timeStart("saving segments as geojson")
  save_features(segments_as_geojson, out_file)
  timeEnd("saving segments as geojson")

  #return (img_gray, ridges, img_bin, intersections, img_seg)
  # return segments
  # detect center lines
  
  # connect segments
  
  # output data

  timeEnd("get all metadata")

if __name__ == '__main__':
  arguments = docopt(__doc__)
  in_file = arguments["--image"]
  out_dir = arguments["--output"]
  scale = float(arguments["--scale"])
  debug_dir = arguments["--debug"]

  if (in_file and out_dir):
    segments = analyze_image(in_file, out_dir, scale, debug_dir)
  else:
    print(arguments)
