from timer import timeStart, timeEnd

timeStart("import libs")
import numpy as np
from scipy import misc
from scipy.ndimage.morphology import binary_opening
from skimage.filters import threshold_otsu
from skimage.morphology import disk
from skimage.segmentation import find_boundaries
from scipy.ndimage.measurements import label

from skimage.transform import hough_line, hough_line_peaks, probabilistic_hough_line
import skimage.draw as skidraw
from skimage.color import gray2rgb

from line_intersection import seg_intersect
from hough_lines import get_hough_lines as do_hough
from threshold_image import threshold_image

import matplotlib.pyplot as plt
import geojson
timeEnd("import libs")

PARAMS = {
  "disk-size": lambda scale: int(17*scale)
}

def get_boundary(grayscale_image, scale=1, debug_dir=False):
  timeStart("threshold image")
  black_and_white_image = threshold_image(grayscale_image)
  timeEnd("threshold image")

  timeStart("morphological open image")
  filter_element = disk(PARAMS["disk-size"](scale))
  opened_image = binary_opening(black_and_white_image, filter_element)
  timeEnd("morphological open image")

  timeStart("invert image")
  opened_image = np.invert(opened_image)
  timeEnd("invert image")

  timeStart("segment image into connected regions")
  labeled_components, num_components = label(opened_image)
  timeEnd("segment image into connected regions")

  timeStart("calculate region areas")
  # Have to cast to np.intp with ndarray.astype because of a numpy bug
  # see: https://github.com/numpy/numpy/pull/4366
  areas = np.bincount(labeled_components.flatten().astype(np.intp))[1:]
  timeEnd("calculate region areas")

  timeStart("calculate region boundaries")
  image_boundaries = find_boundaries(labeled_components, connectivity=1, mode="inner", background=0)
  timeEnd("calculate region boundaries")

  timeStart("mask region of interest")
  largest_component_id = np.argmax(areas) + 1
  region_of_interest_mask = (labeled_components != largest_component_id)
  region_of_interest_boundary = np.copy(image_boundaries)
  region_of_interest_boundary[region_of_interest_mask] = 0
  timeEnd("mask region of interest")

  if debug_dir:
    misc.imsave(debug_dir+"/black_and_white_image.png", black_and_white_image)
    misc.imsave(debug_dir+"/opened_image.png", opened_image)
    misc.imsave(debug_dir+"/image_boundaries.png", image_boundaries)
    misc.imsave(debug_dir+"/region_of_interest_boundary.png", region_of_interest_boundary)

  return region_of_interest_boundary

def get_hough_lines(image, min_angle, max_angle):
  min_separation_distance = 5
  min_separation_angle = 5
  return do_hough(image, min_angle, max_angle, min_separation_distance, min_separation_angle)

def get_line_length(line):
  return np.linalg.norm(np.subtract(line[1], line[0]))

def get_box_lines(boundary, debug_dir = False, image = None):
  height, width = boundary.shape
  [half_width, half_height] = np.floor([0.5 * width, 0.5 * height]).astype(int)

  timeStart("split image")
  image_regions = {
    "left": boundary[0 : height, 0 : half_width],
    "right": boundary[0 : height, half_width : width],
    "top": boundary[0 : half_height, 0 : width],
    "bottom": boundary[half_height : height, 0 : width]
  }
  timeEnd("split image")

  timeStart("get hough lines")
  hough_lines = {
    "left": np.array(get_hough_lines(image_regions["left"], min_angle = -10, max_angle = 10)),
    "right": np.array(get_hough_lines(image_regions["right"], min_angle = -10, max_angle = 10)),
    "top": np.array(get_hough_lines(image_regions["top"], min_angle = -120, max_angle = 70)),
    "bottom": np.array(get_hough_lines(image_regions["bottom"], min_angle = -120, max_angle = 70))
  }
  timeEnd("get hough lines")

  timeStart("calculate line lengths")
  line_lengths = { region: map(get_line_length, lines) for region, lines in hough_lines.iteritems() }
  timeEnd("calculate line lengths")

  timeStart("select longest lines")
  longest_lines = { region: hough_lines[region][np.argmax(lengths)] for region, lengths in line_lengths.iteritems() }
  timeEnd("select longest lines")

  # translate lines to account for working with halved image regions
  longest_lines["bottom"] += [0, half_height]
  longest_lines["right"] += [half_width, 0]

  if debug_dir:
    image = gray2rgb(image)
    line_coords = [ skidraw.line(line[0][1], line[0][0], line[1][1], line[1][0]) for name, line in longest_lines.iteritems() ]
    for line in line_coords:
      rr, cc = line
      mask = (rr >= 0) & (rr < image.shape[0]) & (cc >= 0) & (cc < image.shape[1])
      image[rr[mask], cc[mask]] = [255, 0, 0]
    misc.imsave(debug_dir+"/longest_hough_lines.png", image)

  return longest_lines

def get_roi_corners(lines, debug_dir = False, image = None):
  timeStart("find intersections")
  corners = {
    "top_left": seg_intersect(lines["top"], lines["left"]),
    "top_right": seg_intersect(lines["top"], lines["right"]),
    "bottom_left": seg_intersect(lines["bottom"], lines["left"]),
    "bottom_right": seg_intersect(lines["bottom"], lines["right"])
  }

  # turn corners into tuples of the form (x, y), where x and y are integers
  corners = { corner_name: tuple(coord.astype(int)) for corner_name, coord in corners.iteritems() }
  timeEnd("find intersections")

  if debug_dir:
    inner_circles = { corner_name: skidraw.circle(corner[1], corner[0], 10, shape=image.shape) for corner_name, corner in corners.iteritems() }
    outer_circles = { corner_name: skidraw.circle(corner[1], corner[0], 50, shape=image.shape) for corner_name, corner in corners.iteritems() }
    for corner_name in inner_circles:
      image[outer_circles[corner_name]] = 0
      image[inner_circles[corner_name]] = 255
    misc.imsave(debug_dir+"/roi_corners.png", image)

  return corners

def save_corners_as_geojson(corners, filepath):
  timeStart("saving to "+ filepath)
  newPolygon = geojson.Polygon([corners["top_left"], corners["top_right"], corners["bottom_right"], corners["bottom_left"], corners["top_left"]])
  newFeature = geojson.Feature(geometry = newPolygon)
  with open(filepath, 'w') as outfile:
    geojson.dump(newFeature, outfile)
  timeEnd("saving to "+ filepath)
