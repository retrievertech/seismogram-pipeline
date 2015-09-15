# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 22:24:55 2015

@author: benamy
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Feb 11 18:20:36 2015

@author: benamy
"""

from lib.timer import timeStart, timeEnd
from lib.debug import Debug, pad

import numpy as np
from math import log
from scipy import ndimage
from scipy.ndimage.filters import gaussian_filter1d, gaussian_laplace
from skimage.feature import peak_local_max
from skimage.filters import threshold_otsu
from skimage.morphology import remove_small_objects

from lib.utilities import normalize

def ridge_region_vert(ridges, shape):
  '''
  ridges are tuples like (row, col, sigma, max_value)
  ridge width is sqrt(2) * sigma
  '''
  img = np.zeros(shape, dtype=float)

  for r in ridges:
    width = np.sqrt(2) * r[2]
    #width = r[2]
    lower_bound = max(0, round(r[1] - width))
    upper_bound = min(shape[1]-1, round(r[1] + width))
    img[r[0], lower_bound:upper_bound] = r[3]
  return img

def ridge_region_horiz(ridges, shape):
  '''
  ridges are tuples like (row, col, sigma, max_value)
  ridge width is sqrt(2) * sigma
  '''
  img = np.zeros(shape, dtype=float)

  for r in ridges:
    width = np.sqrt(2) * r[2]
    #width = r[2]
    lower_bound = max(0, round(r[0] - width))
    upper_bound = min(shape[0]-1, round(r[0] + width))
    img[lower_bound:upper_bound, r[1]] = r[3]
  return img

def find_ridges(img, dark_pixels, min_sigma = 0.7071, max_sigma = 30,
            sigma_ratio = 1.6, min_ridge_length = 15,
            low_threshold = 0.002, high_threshold = 0.006,
            convex_threshold = 0.00015, figures=True):
  '''

  '''
  #preliminaries
  timeStart("gaussian_laplace filter")
  laplacian = gaussian_laplace(img, sigma=2)
  timeEnd("gaussian_laplace filter")

  Debug.save_image("ridges", "gaussian_laplace", laplacian)

  # convex_pixels is an image of regions with positive second derivative
  convex_pixels = laplacian > convex_threshold

  Debug.save_image("ridges", "convex_pixels", convex_pixels)

  timeStart("sobel filters x & y")
  abs_isobel = np.abs(ndimage.sobel(img, axis=0))
  abs_jsobel = np.abs(ndimage.sobel(img, axis=1))
  timeEnd("sobel filters x & y")

  timeStart("otsu thresholds x & y")
  vertical_slopes = abs_isobel > threshold_otsu(abs_isobel)
  horizontal_slopes = abs_jsobel > threshold_otsu(abs_jsobel)
  timeEnd("otsu thresholds x & y")

  Debug.save_image("ridges", "vertical_slopes", vertical_slopes)
  Debug.save_image("ridges", "horizontal_slopes", horizontal_slopes)

  num_scales = int(log(float(max_sigma) / min_sigma, sigma_ratio)) + 1
  timeStart("create gaussian image pyramid at %s scales" % num_scales)
  # a geometric progression of standard deviations for gaussian kernels
  sigma_list = np.array([min_sigma * (sigma_ratio ** i)
              for i in range(num_scales + 1)])

  gaussian_blurs_h = [gaussian_filter1d(img, s, 0) \
            for s in sigma_list]
  gaussian_blurs_v = [gaussian_filter1d(img, s, 1) \
            for s in sigma_list]
  timeEnd("create gaussian image pyramid at %s scales" % num_scales)

  image_cube_h = np.zeros((img.shape[0], img.shape[1], num_scales))
  image_cube_v = np.zeros((img.shape[0], img.shape[1], num_scales))
  exclusion = np.zeros((img.shape[0], img.shape[1], num_scales), dtype=bool)

  timeStart("find horizontal ridges")
  exclusion_layer = dark_pixels | convex_pixels | horizontal_slopes
  Debug.save_image("ridges", "horizontal_exclusion_layer_base", exclusion_layer)
  for i in range(num_scales):
    image_cube_h[:,:,i] = ((gaussian_blurs_h[i] - gaussian_blurs_h[i + 1]))
    # add to the exclusion layer all convex pixels in image_cube_h[:,:,i]
    exclusion_layer = (exclusion_layer | (image_cube_h[:,:,i] < -convex_threshold))
    Debug.save_image("ridges", "horizontal_exclusion_layer-" + pad(i), exclusion_layer)
    exclusion[:,:,i] = exclusion_layer

  footprint_h = np.ones((3,1,3), dtype=bool)
  image_cube_h_norm = normalize(image_cube_h)

  # maxima_h is a boolean array
  maxima_h = peak_local_max(image_cube_h_norm, indices=False, min_distance=1,
          threshold_rel=0, threshold_abs=0, exclude_border=False,
          footprint=footprint_h)
  maxima_h = maxima_h & (~exclusion) & (image_cube_h >= low_threshold)


  # ridges_h is a 2D array that is true everywhere that
  # that maxima_h has at least one true value across all scales
  ridges_h = np.amax(maxima_h, axis=-1)

  image_cube_h = np.where(maxima_h, image_cube_h, 0)
  # the same as:
  # image_cube_h[~maxima_h] = 0

  max_values_h = np.amax(image_cube_h, axis=-1)

  timeEnd("find horizontal ridges")

  timeStart("find vertical ridges")
  exclusion_layer = dark_pixels | convex_pixels | vertical_slopes
  Debug.save_image("ridges", "vertical_exclusion_layer_base", exclusion_layer)
  for i in range(num_scales):
    image_cube_v[:,:,i] = ((gaussian_blurs_v[i] - gaussian_blurs_v[i + 1]))
    # add to the exclusion layer all convex pixels in image_cube_v[:,:,i]
    exclusion_layer = (exclusion_layer | (image_cube_v[:,:,i] < convex_threshold))
    Debug.save_image("ridges", "vertical_exclusion_layer-" + pad(i), exclusion_layer)
    exclusion[:,:,i] = exclusion_layer

  footprint_v = np.ones((1,3,3), dtype=bool)
  image_cube_v_norm = normalize(image_cube_v)
  maxima_v = peak_local_max(image_cube_v_norm, indices=False, min_distance=1,
          threshold_rel=0, threshold_abs=0,
          footprint=footprint_v)
  maxima_v = maxima_v & (~exclusion) & (image_cube_v >= low_threshold)
  ridges_v = np.amax(maxima_v, axis=-1)

  image_cube_v = np.where(maxima_v, image_cube_v, 0)
  max_values_v = np.amax(image_cube_v, axis = -1)
  timeEnd("find vertical ridges")

  # Horiztonal ridges need to be prominent
  ridges_h = ridges_h & (max_values_h >= high_threshold)

  # Vertical ridges need to either be prominent or highly connected
  ridges_v = (ridges_v & ((max_values_v >= high_threshold) |
              remove_small_objects(ridges_v, min_ridge_length,
                         connectivity = 2)))

  timeStart("aggregate information about maxima of horizontal ridges")
  sigmas_h = np.argmax(image_cube_h, axis=-1)
  sigmas_h = min_sigma * np.power(sigma_ratio, sigmas_h)
  indices_h = np.argwhere(ridges_h)
  sigmas_h = sigmas_h[ridges_h]
  max_values_h = max_values_h[ridges_h]
  maxima_h = np.hstack((indices_h, sigmas_h[:,np.newaxis],
              max_values_h[:,np.newaxis]))
  timeEnd("aggregate information about maxima of horizontal ridges")

  timeStart("prioritize horizontal regions")
  horizontal_regions = ridge_region_horiz(maxima_h, img.shape)
  ridges_v = ridges_v & (horizontal_regions == 0)
  timeEnd("prioritize horizontal regions")

  Debug.save_image("ridges", "vertical_ridges", ridges_v)
  Debug.save_image("ridges", "horizontal_ridges", ridges_h)

  if figures == True:
    return (ridges_h, ridges_v)
  else:
    # Aggregate information about maxima of vertical ridges
    sigmas_v = np.argmax(image_cube_v, axis=-1)
    sigmas_v = min_sigma * np.power(sigma_ratio, sigmas_v)
    indices_v = np.argwhere(ridges_v)
    sigmas_v = sigmas_v[ridges_v]
    max_values_v = max_values_v[ridges_v]
    maxima_v = np.hstack((indices_v, sigmas_v[:,np.newaxis],
                max_values_v[:,np.newaxis]))
    return (maxima_h, maxima_v)
