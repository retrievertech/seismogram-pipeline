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

def get_ridge_region_vert(ridges, shape):
  '''
  '''
  ridge_region = np.zeros(shape, dtype=float)

  for row, col, sigma, max_value in ridges:
    ridge_width = round(np.sqrt(2) * sigma)
    bounds = np.array([col-ridge_width, col+ridge_width])
    bounds = np.clip(bounds, 0, shape[1]-1)
    ridge_region[row, bounds[0]:bounds[1]] = max_value

  return ridge_region

def get_ridge_region_horiz(ridges, shape):
  '''
  '''
  ridge_region = np.zeros(shape, dtype=float)

  for row, col, sigma, max_value in ridges:
    ridge_width = round(np.sqrt(2) * sigma)
    bounds = np.array([row-ridge_width, row+ridge_width])
    bounds = np.clip(bounds, 0, shape[0]-1)
    ridge_region[bounds[0]:bounds[1], col] = max_value

  return ridge_region

def get_slopes(img, axis):
  abs_sobel = np.abs(ndimage.sobel(img, axis=axis))
  return abs_sobel > threshold_otsu(abs_sobel)

def create_image_cube(img, sigma_list, axis):
  gaussian_blurs = [gaussian_filter1d(img, s, axis=axis) for s in sigma_list]
  num_scales = len(gaussian_blurs) - 1
  image_cube = np.zeros((img.shape[0], img.shape[1], num_scales))
  for i in range(num_scales):
    image_cube[:,:,i] = ((gaussian_blurs[i] - gaussian_blurs[i + 1]))
  return image_cube

def create_exclusion_cube(image_cube, dark_pixels, convex_pixels,
                          slopes, convex_threshold):

  exclusion_cube = np.zeros(image_cube.shape, dtype=bool)
  exclusion_cube[:,:,0] = dark_pixels | convex_pixels | slopes \
                        | (image_cube[:,:,0] < -convex_threshold)

  Debug.save_image("ridges", "exclusion_cube_base", exclusion_cube[:,:,0])

  num_scales = image_cube.shape[2]
  for i in range(1, num_scales):
    # each layer of the exclusion cube contains the previous layer
    # plus all convex pixels in the current image_cube layer
    exclusion_cube[:,:,i] = (exclusion_cube[:,:,i-1] \
                            | (image_cube[:,:,i] < -convex_threshold))
    Debug.save_image("ridges", "exclusion_cube-" + pad(i), exclusion_cube[:,:,i])

  return exclusion_cube

def find_valid_maxima(image_cube, footprint, exclusion, low_threshold):
  '''
  Returns a 3D array that is true everywhere that image_cube
  has a local maxima except in regions marked for exclusion.

  '''

  # peak_local_max expects a normalized image (values between 0 and 1)
  normalized_image_cube = normalize(image_cube)

  maxima = peak_local_max(normalized_image_cube, indices=False, min_distance=1,
                          threshold_rel=0, threshold_abs=0, exclude_border=True,
                          footprint=footprint)
  
  return maxima & (~exclusion) & (image_cube >= low_threshold)

def get_convex_pixels(img, convex_threshold):
  laplacian = gaussian_laplace(img, sigma=2)
  Debug.save_image("ridges", "gaussian_laplace", laplacian)
  return laplacian > convex_threshold

def find_ridges(img, dark_pixels, min_sigma = 0.7071, max_sigma = 30,
            sigma_ratio = 1.6, min_ridge_length = 15,
            low_threshold = 0.002, high_threshold = 0.006,
            convex_threshold = 0.00015, figures=True):
  '''

  '''
  # number of scales at which to compute a difference of gaussians
  num_scales = int(log(float(max_sigma) / min_sigma, sigma_ratio)) + 1

  # a geometric progression of standard deviations for gaussian kernels
  sigma_list = np.array([min_sigma * (sigma_ratio ** i)
              for i in range(num_scales + 1)])

  # convex_pixels is an image of regions with positive second derivative
  timeStart("get convex pixels")
  convex_pixels = get_convex_pixels(img, convex_threshold)
  timeEnd("get convex pixels")
  
  Debug.save_image("ridges", "convex_pixels", convex_pixels)

  timeStart("find horizontal ridges")

  timeStart("get slopes")
  horizontal_slopes = get_slopes(img, axis=1)
  timeEnd("get slopes")

  Debug.save_image("ridges", "horizontal_slopes", horizontal_slopes)

  timeStart("create difference of gaussian image cube at %s scales" % num_scales)
  image_cube_h = create_image_cube(img, sigma_list, axis=0)
  timeEnd("create difference of gaussian image cube at %s scales" % num_scales)

  exclusion = create_exclusion_cube(image_cube_h, dark_pixels, convex_pixels,
                                    horizontal_slopes, convex_threshold)

  footprint_h = np.ones((3,1,3), dtype=bool)

  maxima_h = find_valid_maxima(image_cube_h, footprint_h, exclusion, low_threshold)

  # ridges_h is a 2D array that is true everywhere
  # that maxima_h has at least one true value in any scale
  ridges_h = np.amax(maxima_h, axis=-1)

  image_cube_h = np.where(maxima_h, image_cube_h, 0)
  # the same as:
  # image_cube_h[~maxima_h] = 0

  max_values_h = np.amax(image_cube_h, axis=-1)
  timeEnd("find horizontal ridges")

  timeStart("find vertical ridges")

  timeStart("get slopes")
  vertical_slopes = get_slopes(img, axis=0)
  timeEnd("get slopes")

  Debug.save_image("ridges", "vertical_slopes", vertical_slopes)

  timeStart("create difference of gaussian image cube at %s scales" % num_scales)
  image_cube_v = create_image_cube(img, sigma_list, axis=1)
  timeEnd("create difference of gaussian image cube at %s scales" % num_scales)

  exclusion = create_exclusion_cube(image_cube_v, dark_pixels, convex_pixels,
                                    vertical_slopes, convex_threshold)

  footprint_v = np.ones((1,3,3), dtype=bool)

  maxima_v = find_valid_maxima(image_cube_v, footprint_v, exclusion, low_threshold)
  
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
  horizontal_regions = get_ridge_region_horiz(maxima_h, img.shape)
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
