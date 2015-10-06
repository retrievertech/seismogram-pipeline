from timer import timeStart, timeEnd
from lib.debug import Debug

import numpy as np
import cv2
from skimage.filters import threshold_otsu
from skimage.morphology import disk
from skimage.segmentation import find_boundaries
from scipy.ndimage.measurements import label

from skimage.transform import hough_line, hough_line_peaks, probabilistic_hough_line
import skimage.draw as skidraw
from skimage.color import gray2rgb

from line_intersection import seg_intersect
from hough_lines import get_best_hough_lines
from otsu_threshold_image import otsu_threshold_image

import matplotlib.pyplot as plt
import geojson

PARAMS = {
  "disk-size": lambda scale: int(17*scale)
}

def get_boundary(grayscale_image, scale=1):
  timeStart("threshold image")
  black_and_white_image = otsu_threshold_image(grayscale_image)
  timeEnd("threshold image")

  timeStart("morphological open image")
  filter_element = disk(PARAMS["disk-size"](scale))
  opened_image = cv2.morphologyEx(255*black_and_white_image.astype(np.uint8), cv2.MORPH_OPEN, filter_element)
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

  Debug.save_image("roi", "black_and_white_image", black_and_white_image)
  Debug.save_image("roi", "opened_image", opened_image)
  Debug.save_image("roi", "image_boundaries", image_boundaries)
  Debug.save_image("roi", "region_of_interest_boundary", region_of_interest_boundary)

  return region_of_interest_boundary

def get_hough_lines(image, min_angle, max_angle):
  min_separation_distance = 5
  min_separation_angle = 5
  return get_best_hough_lines(image, min_angle, max_angle, min_separation_distance, min_separation_angle)

def get_box_lines(boundary, image = None):
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
    "top": np.array(get_hough_lines(image_regions["top"], min_angle = -120, max_angle = -70)),
    "bottom": np.array(get_hough_lines(image_regions["bottom"], min_angle = -120, max_angle = -70))
  }
  timeEnd("get hough lines")

  hough_lines["bottom"] += [0, half_height]
  hough_lines["right"] += [half_width, 0]

  print "found these hough lines:"
  print hough_lines

  if Debug.active:
    image = gray2rgb(boundary)
    line_coords = [ skidraw.line(line[0][1], line[0][0], line[1][1], line[1][0]) for line in hough_lines.itervalues() ]
    for line in line_coords:
      rr, cc = line
      mask = (rr >= 0) & (rr < image.shape[0]) & (cc >= 0) & (cc < image.shape[1])
      image[rr[mask], cc[mask]] = [255, 0, 0]
    Debug.save_image("roi", "hough_lines", image)

  return hough_lines

def get_corners(lines, image = None):
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

  if Debug.active:
    image_copy = np.copy(image)
    inner_circles = { corner_name: skidraw.circle(corner[1], corner[0], 10, shape=image.shape) for corner_name, corner in corners.iteritems() }
    outer_circles = { corner_name: skidraw.circle(corner[1], corner[0], 50, shape=image.shape) for corner_name, corner in corners.iteritems() }
    for corner_name in inner_circles:
      image_copy[outer_circles[corner_name]] = 0.0
      image_copy[inner_circles[corner_name]] = 1.0
    Debug.save_image("roi", "roi_corners", image_copy)

  return corners

def get_roi(image, scale):
  boundary = get_boundary(image, scale=scale)
  lines = get_box_lines(boundary, image=image)
  corners = get_corners(lines, image=image)
  return corners

def corners_to_geojson(corners):
  newPolygon = geojson.Polygon([[corners["top_left"], corners["top_right"], corners["bottom_right"], corners["bottom_left"], corners["top_left"]]])
  newFeature = geojson.Feature(geometry = newPolygon)
  return newFeature
