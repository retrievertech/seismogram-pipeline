# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 13:58:26 2015

@author: benamy
"""

import numpy as np
from skimage.morphology import (medial_axis, watershed, binary_erosion, square)
from scipy.ndimage import label
from skimage import color
from skimage.filter import sobel, canny, threshold_otsu

from reverse_medial_axis import reverse_medial_axis
from binarization import fill_corners
from classes import segment, get_ridge_line

def get_segments(img_gray, img_bin, img_skel, dist, img_intersections, 
         ridges_h, ridges_v, figure=False):
  image_canny = canny(img_gray)
  img_bin = img_bin & (~ fill_corners(image_canny))
  
  image_sobel = sobel(img_gray)
  steep_slopes = image_sobel > threshold_otsu(image_sobel)
  steep_slopes = binary_erosion(steep_slopes, square(3, dtype=bool))
  segments_bin = (img_skel & (~ img_intersections) & (~ image_canny) & 
          (~ steep_slopes))
          
  rmat = reverse_medial_axis(segments_bin, dist)
  # maybe, instead of running medial_axis again, do nearest-neighbor interp    
  _, rmat_dist = medial_axis(rmat, return_distance=True)
  image_segments, num_segments = label(segments_bin, np.ones((3,3)))
  image_segments = watershed(-rmat_dist, image_segments, mask = rmat)
  segments = img_seg_to_seg_objects(image_segments)
  add_ridges_to_segments(ridges_h, ridges_v, segments)
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
  dims = img_seg.shape
  num_segments = np.amax(img_seg)    
  segments = {}
  for i in np.arange(1, num_segments + 1):
    pixel_coords = np.argwhere(img_seg == i)
    segments[i] = segment(pixel_coords, dims, ID=i)
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
