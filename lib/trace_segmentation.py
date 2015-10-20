# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 13:58:26 2015

@author: benamy
"""

from lib.timer import timeStart, timeEnd
from lib.debug import Debug

import numpy as np
from skimage.morphology import (medial_axis, watershed, binary_erosion, square)
from scipy.ndimage import label
from skimage import color
from skimage.filters import sobel, threshold_otsu
from skimage.feature import canny

from reverse_medial_axis import reverse_medial_axis
from binarization import fill_corners
from segment import segment
from geojson import FeatureCollection

def get_segments(img_gray, img_bin, img_skel, dist, img_intersections,
         ridges_h, ridges_v, figure=False):
  timeStart("canny edge detection")
  image_canny = canny(img_gray)
  timeEnd("canny edge detection")

  Debug.save_image("segments", "edges", image_canny)

  # Strange: just noticed that none of the below had
  # ever been getting used for as long as this file
  # has existed.

  # timeStart("fill canny corners")
  # filled_corners_canny = fill_corners(image_canny)
  # timeEnd("fill canny corners")

  # Debug.save_image("segments", "edges_with_corners", filled_corners_canny)

  # timeStart("subtract canny corners from image")
  # img_bin = img_bin & (~ filled_corners_canny)
  # timeEnd("subtract canny corners from image")

  # Debug.save_image("segments", "binary_image_minus_edges", img_bin)

  timeStart("sobel filter")
  image_sobel = sobel(img_gray)
  timeEnd("sobel filter")

  Debug.save_image("segments", "slopes", image_sobel)

  timeStart("otsu threshold")
  steep_slopes = image_sobel > threshold_otsu(image_sobel)
  timeEnd("otsu threshold")

  Debug.save_image("segments", "steep_slopes", steep_slopes)

  timeStart("binary erosion")
  steep_slopes = binary_erosion(steep_slopes, square(3, dtype=bool))
  timeEnd("binary erosion")

  Debug.save_image("segments", "eroded_steep_slopes", steep_slopes)

  timeStart("bitwise & and ~")
  segments_bin = (img_skel & (~ img_intersections) & (~ image_canny) &
          (~ steep_slopes))
  timeEnd("bitwise & and ~")

  Debug.save_image("segments", "skeleton_minus_intersections_minus_edges_minus_steep_slopes", segments_bin)

  timeStart("reverse medial axis")
  rmat = reverse_medial_axis(segments_bin, dist)
  timeEnd("reverse medial axis")

  Debug.save_image("segments", "reverse_medial_axis", rmat)

  # maybe, instead of running medial_axis again, do nearest-neighbor interp
  timeStart("get distance transform")
  _, rmat_dist = medial_axis(rmat, return_distance=True)
  timeEnd("get distance transform")

  timeStart("label segments")
  image_segments, num_segments = label(segments_bin, np.ones((3,3)))
  timeEnd("label segments")

  timeStart("watershed")
  image_segments = watershed(-rmat_dist, image_segments, mask=rmat)
  timeEnd("watershed")

  print "found %s segments" % np.amax(image_segments)

  segments = img_seg_to_seg_objects(image_segments, num_segments, ridges_h, ridges_v, img_gray)

  if Debug.active:
    from lib.segment_coloring import gray2prism, color_markers
    num_traces = np.amax(image_segments)
    traces_colored = (image_segments + num_traces * (image_segments % 4)) / float(4 * num_traces)
    traces_colored = gray2prism(traces_colored)
    # Color background black
    traces_colored = color_markers(np.logical_not(img_bin), traces_colored, [0,0,0])
    Debug.save_image("segments", "segment_regions", traces_colored)

  if figure == False: 
    return segments
  else:
    return (segments, image_segments)

def img_seg_to_seg_objects(img_seg, num_segments, ridges_h, ridges_v, img_gray):
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
  
  # segment_coordinates becomes a list of segments, where
  # each segment is a list of all of its pixel coordinates
  segment_coordinates = [[] for i in xrange(num_segments)]

  timeStart("get segment coordinates")
  it = np.nditer(img_seg, flags=['multi_index'])
  while not it.finished:
    if it[0] == 0:
      it.iternext()
      continue

    segment_idx = int(it[0] - 1)
    segment_coordinates[segment_idx].append(np.array(it.multi_index))
    it.iternext()

  # timeStart("nonzero")
  # segment_coords = np.nonzero(img_seg)
  # timeEnd("nonzero")

  # coords = np.column_stack(segment_coords)

  # timeStart("nzvals")
  # nzvals = img_seg[segment_coords[0], segment_coords[1]]
  # timeEnd("nzvals")

  # timeStart("index coords")
  # segment_coordinates = [ coords[nzvals == k] for k in range(1, num_segments + 1) ]
  # timeEnd("index coords")

  timeEnd("get segment coordinates")

  segments = {}
  timeStart("create segment objects")
  for (segment_idx, pixel_coords) in enumerate(segment_coordinates):
    segment_id = segment_idx + 1
    pixel_coords = np.array(pixel_coords)
    values = get_image_values(img_gray, pixel_coords)
    ridge_line = get_ridge_line(ridges_h, ridges_v, pixel_coords)
    
    new_segment = segment(coords=pixel_coords,
                          values=np.array(values),
                          id=segment_id,
                          ridge_line=ridge_line)

    if (new_segment.has_center_line):
      center_line_values = get_image_values(img_gray, new_segment.center_line.coords)
      new_segment.add_center_line_values(center_line_values)

    segments[segment_idx] = new_segment
  timeEnd("create segment objects")

  return segments

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
  geojson_line_segments = \
    [seg.to_geojson_feature() for seg in segments.itervalues() if seg.has_center_line]
  return FeatureCollection(geojson_line_segments)

def get_ridge_line(ridges_h, ridges_v, region):
  '''
  Parameters
  ------------
  ridges_h : 2-D boolean array
    Image containing the horizontal ridge lines.
  ridges_v : 2-D boolean array
    Image containing the vertical ridge lines.
  region : 2-D numpy array
    A list of coordinates defining the region for which you want to
    generate a center line.

  Returns
  ---------
  ridge_line : 2-D numpy array
    List of coordinates defining the center line of the region.

  '''
  ridge_h_coords = get_ridge_coords_in_region(ridges_h, region)
  ridge_v_coords = get_ridge_coords_in_region(ridges_v, region)
  ridge_line = ridges_to_centerline(ridge_h_coords, ridge_v_coords)
  return ridge_line

def get_image_values(img_gray, coords):
  return map(lambda pt : int(255*img_gray[tuple(pt)]), coords)

def get_ridge_coords_in_region(ridges, coord_list):
  '''
  Filter through a list of coordinates, returning only those
  that correspond to a true value in **ridges**.

  Parameters
  ------------
  ridges : 2-D boolean array
    The image containing the ridge lines.
  coord_list : 2-D numpy array
    The coordinates that you want to filter through.

  Returns
  ---------
  ridge_coords : numpy array
    The subset of coordinates in **coord_list** that correspond
    to ridges.
  
  '''
  coord_is_a_ridge = ridges[coord_list[:,0], coord_list[:,1]]
  ridge_coords = coord_list[coord_is_a_ridge]
  return ridge_coords

def ridges_to_centerline(ridge_h_coords, ridge_v_coords):
  '''
  Still figuring out the purpose of this function. My current
  hypothesis is that it limits the use of vertical ridges when
  calculating the center line coords. I think the goal is to
  include vertical ridges in centerline estimation *only* when
  there are horizontal ridges at the same x-coordinate.
  
  '''
  if (ridge_h_coords.size == 0) and (ridge_v_coords.size == 0):
    return np.array([[-1, -1]])

  ridge_v_cols = ridge_v_coords[:,1]
  ridge_h_cols = ridge_h_coords[:,1]

  if ridge_v_coords.size > 0:
    domain_v = np.array([ np.amin(ridge_v_cols), np.amax(ridge_v_cols) ], dtype=int)
    truncate = True
  else:
    truncate = False

  if ridge_h_coords.size > 0:
    domain_h = np.array([ np.amin(ridge_h_cols), np.amax(ridge_h_cols) ], dtype=int)
  else:
    domain_h = domain_v[::-1]

  # print ""
  # print "ridge_v_coords %s" % ridge_v_coords
  # print "ridge_v_cols %s" % ridge_v_cols
  # print "ridge_h_cols %s" % ridge_h_cols
  
  # If ridges vertical at ends, truncate
  if truncate:
    # print "TRUNCATING RIDGE!"
    # print "domain_h %s" % domain_h
    # print "domain_v %s" % domain_v
    if domain_v[0] <= domain_h[0]:
      ridge_v_coords = \
        ridge_v_coords[(ridge_v_coords[:,1] != domain_v[0]),:]
    if domain_v[1] >= domain_h[1]:
      ridge_v_coords = \
        ridge_v_coords[(ridge_v_coords[:,1] != domain_v[1]),:]
    # print "trunacted ridge_v_coords %s" % ridge_v_coords

  ridge = np.vstack((ridge_h_coords, ridge_v_coords))
  return ridge_line_to_series(ridge)

def ridge_line_to_series(coords):
  '''
  Parameters
  ------------
  coords : 2-D int array
    An array of all pixel coordinates that define the ridge. Coordinates
    get averaged in the y direction to estimate the center line coords.

  Returns
  ---------
  series : 2-D int array
    An array of all pixel coordinates that define the ridge center line.

  '''
  if coords.size == 0:
    return np.array([[0,0]])
  
  x_coords = coords[:,1]
  domain = (min(x_coords), max(x_coords))
  series = []
  for x in range(domain[0], domain[1] + 1):
    coords_with_this_x_value = coords[coords[:,1] == x]
    y_vals = coords_with_this_x_value[:,0]
    if y_vals.size > 0:
      avg_y = np.mean(y_vals)
      series.append(np.array([avg_y, x]))
  series = np.asarray(series)
  return series
