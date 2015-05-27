# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 13:58:26 2015

@author: benamy
"""

from lib.timer import timeStart, timeEnd

import numpy as np
from skimage.morphology import (medial_axis, watershed, binary_erosion, square)
from scipy.ndimage import label
from skimage import color
from skimage.filters import sobel, threshold_otsu
from skimage.feature import canny

from reverse_medial_axis import reverse_medial_axis
from binarization import fill_corners
from classes import segment, get_ridge_line
from geojson import LineString, Feature, FeatureCollection

def get_segments(img_gray, img_bin, img_skel, dist, img_intersections, 
         ridges_h, ridges_v, figure=False):
  timeStart("canny edge detection")
  image_canny = canny(img_gray)
  timeEnd("canny edge detection")

  timeStart("bitwise & and ~")
  img_bin = img_bin & (~ fill_corners(image_canny))
  timeEnd("bitwise & and ~")
  
  timeStart("sobel filter")
  image_sobel = sobel(img_gray)
  timeEnd("sobel filter")

  timeStart("otsu threshold")
  steep_slopes = image_sobel > threshold_otsu(image_sobel)
  timeEnd("otsu threshold")

  timeStart("binary erosion")
  steep_slopes = binary_erosion(steep_slopes, square(3, dtype=bool))
  timeEnd("binary erosion")

  timeStart("bitwise & and ~")
  segments_bin = (img_skel & (~ img_intersections) & (~ image_canny) & 
          (~ steep_slopes))
  timeEnd("bitwise & and ~")

  timeStart("reverse medial axis")
  rmat = reverse_medial_axis(segments_bin, dist)
  timeEnd("reverse medial axis")

  # maybe, instead of running medial_axis again, do nearest-neighbor interp    
  timeStart("skeletonize")
  _, rmat_dist = medial_axis(rmat, return_distance=True)
  timeEnd("skeletonize")

  timeStart("label segments")
  image_segments, num_segments = label(segments_bin, np.ones((3,3)))
  timeEnd("label segments")

  timeStart("watershed")
  image_segments = watershed(-rmat_dist, image_segments, mask = rmat)
  timeEnd("watershed")

  print "found %s segments" % np.amax(image_segments)

  segments = img_seg_to_seg_objects(image_segments)

  timeStart("add ridges to segments")
  add_ridges_to_segments(ridges_h, ridges_v, segments)
  timeEnd("add ridges to segments")

  if figure == False:
    return segments
  else:
    return (segments, image_segments)

'''
store segments in objects
'''

def img_seg_to_seg_objects(img_seg):
  '''
  Creates segment objects from an array of labeled pixels.    
  
  Parameters
  ------------
  img_seg : 2-D numpy array of ints
    An array with each pixel labeled according to its segment. 
  
  Returns
  --------
  segments : list of segments
    A list containing all the trace segments.
  '''

  timeStart("get segment coordinates")
  it = np.nditer(img_seg, flags=['multi_index'])
  segment_coordinates = {}
  while not it.finished:
    label_num = str(it[0])
    if (label_num not in segment_coordinates):
      segment_coordinates[label_num] = []
    
    segment_coordinates[label_num].append(np.array(it.multi_index))
    it.iternext()
  timeEnd("get segment coordinates")

  dims = img_seg.shape
  segments = {}
  timeStart("create segment objects")
  for (label_num, pixel_coords) in segment_coordinates.iteritems():
    segments[label_num] = segment(np.array(pixel_coords), dims, ID=label_num)
  timeEnd("create segment objects")

  return segments

def add_ridges_to_segments(ridges_h, ridges_v, segments):
  for seg in segments.itervalues():
    seg.add_ridge_line(get_ridge_line(ridges_h, ridges_v, seg.region))

def image_overlay(img, overlay, mask = None):
  if img.ndim == 2:
    img = color.gray2rgb(img)
  if overlay.ndim == 2:
    overlay = color.gray2rgb(overlay)
  if mask.ndim == 2:
    mask = np.dstack((mask, mask, mask))
  images_combined = 0.5 * (img + overlay)
  return np.where(mask, img, images_combined)

def segments_to_geojson(segments):
  geojson_line_segments = []
  for seg in segments.itervalues():
    if seg.has_center_line == True:
      center_line = zip(seg.center_line.x, seg.center_line.y)
      feature = Feature(geometry = LineString(center_line))
      geojson_line_segments.append(feature)
  geojson_line_segments = FeatureCollection(geojson_line_segments)
  return geojson_line_segments
