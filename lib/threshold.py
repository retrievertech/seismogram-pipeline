# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 13:05:12 2015

@author: benamy
"""

import numpy as np
from scipy.interpolate import SmoothBivariateSpline as spline2d 
from scipy.ndimage import distance_transform_edt
from skimage.morphology import (convex_hull_image)
from numpy.ma.core import MaskedArray
from mitchells_best_candidate import best_candidate_sample
  
def threshold(a, threshold_function, num_blocks, block_dims = None, 
        smoothing_factor = 0.003, mask = None, *args):
  '''
  Get a smoothly varing threshold from an image by applying the threshold 
  function to multiple randomly positioned blocks of the image and using
  a 2-D smoothing spline to set the threshold across the image. 
  
  Parameters 
  ------------
  a : 2-D numpy array
    The grayscale image.
  threshold_function : a function
    The threshold function should take a grayscale image as an input and 
    output an int or float. 
  num_blocks : int
    The number of blocks within the image to which to apply the threshold
    function. A higher number will provide better coverage across the 
    image but will take longer to evaluate.
  block_dims : tuple or numpy array, optional
    The dimensions of the rectangular blocks. Dimensions should be less
    than the dimensions of the image. If left unspecified, the blocks will
    be squares with area approximately equal to two times the area of the
    image, divided by num_blocks.
  smoothing_factor : float, optional
    A parameter to adjust the smoothness of the 2-D smoothing spline. A
    higher number increases the smoothness of the output. An input of zero
    is equivalent to interpolation. 
  
  Returns
  ---------
  th_new : 2-D numpy array
    The threshold. The array is the same shape as the original input image.
  '''
  a_dims = a.shape
  if num_blocks >= 16:
    spline_order = 3
  else:
    spline_order = int(np.sqrt(num_blocks) - 1)
  if spline_order == 0:
    return (np.ones_like(a) * threshold_function(a, *args))

  if (mask is None):
    mask = np.zeros(a_dims, dtype=bool)

  candidate_coords = np.transpose(np.nonzero(~mask))
  
  if block_dims is None:
    block_dim = int(round(np.sqrt(2 * a.size / num_blocks)))
    block_dims = (block_dim, block_dim)
  points = best_candidate_sample(candidate_coords, num_blocks)
  th = []
  
  for p in points:
    block = get_block(a, p, block_dims)
    if (type(block) is MaskedArray):
      threshold = threshold_function(block.compressed(), *args)
    else:
      threshold = threshold_function(block, *args)
    th.append(threshold)
  th = np.asarray(th)

  # Maybe consider using lower-order spline for large images 
  # (if large indices create problems for cubic functions)
  fit = spline2d(points[:,0], points[:,1], th, 
           bbox = [0, a_dims[0], 0, a_dims[1]], 
           kx = spline_order, ky = spline_order,
           s = num_blocks * smoothing_factor)
  th_new = fit(x = np.arange(a_dims[0]), y = np.arange(a_dims[1])) 
  th_new = fix_border(th_new, points)
  return th_new
  
def get_block(a, center, block_dims):
  '''
  Returns the rectangular subarray of **a** centered at **center**, with
  dimensions at most equal to **block_dims**. 
  
  Parameters 
  -----------
  a : 2-D numpy array
  center : tuple or numpy array
    The coordinates of the center of the block. Should be integer-valued. 
  block_dims : tuple or numpy array
    The dimensions of the block. If **center** is too close to the edge of
    **a**, the returned block will have dimensions smaller than 
    **block_dims**.
    
  Results
  ---------
  block : 2-D numpy array
    A subarray of **a**.
  '''
  a_dims = a.shape    
  upper = max(0, center[0] - block_dims[0] / 2)
  lower = min(a_dims[0], center[0] + block_dims[0] / 2 + 1)
  left = max(0, center[1] - block_dims[1] / 2)
  right = min(a_dims[1], center[1] + block_dims[1] / 2 + 1)
  block = a[upper:lower, left:right]
  return block

def get_convex_hull(points, a_dims):
  '''
  Given an array containing the coordinates of points in a 2-D array, outputs 
  the convex hull of those points.
  '''
  a = np.zeros(a_dims, dtype = bool)
  a[points[:,0], points[:,1]] = True
  return convex_hull_image(a)

def fix_border(spline, sample_points):
  '''
  Given coordinates of points in a 2-D array, finds the convex hull defined 
  by those points. Outputs an image equal to spline within the convex hull
  and, everywhere outside the hull, equal to the value of the nearest point 
  inside the hull. 
  '''
  border = (~ get_convex_hull(sample_points, spline.shape))
  ind = distance_transform_edt(border, return_distances = False, 
                 return_indices = True)
  return spline[tuple(ind)]

def background_intensity(a, prob_background = 1):
  '''
  Identifies a threshold for pixel intensity below which pixels are part of
  the background with at least a **prob_background** estimated probability. 
  This works by assuming that most of the image is dark background, the
  single most common pixel brightness is the average brightness for a 
  background pixel, and that the brightnesses of background pixels are 
  distributed like the normal distribution. 
  
  Parameters
  ------------
  a : 2-D numpy array
    The grayscale image. Can be either floats on the interval [0,1] or
    ints on the interval [0,255]. 
  prob_background : float, optional
    The minimum (estimated) probability that a pixel is part of the 
    background. Must be <=1. Lower numbers will likely result in a higher
    returned threshold.
  
  Returns 
  --------
  th : float or int
    The threshold below which pixels in the image are likely part of the
    background. 
  '''
  if np.amax(a) <= 1:
    bins = np.linspace(0, 256/255, num = 257)
    a = np.round(255 * a) / 255
  else:
    bins = np.arange(257)
  # Assume that data from 256,000 pixels is sufficient
  if a.size > 256 * 1000:
    prob = float(256 * 1000) / a.size        
    a = a[(np.random.random(size = a.shape) < prob)]
  hist, bin_edges = np.histogram(a, bins = bins)  
  # Pad counts with 1 (to eliminate zeros)    
  hist = hist + 1
  i = np.argmax(hist)
  background_count = np.zeros((256))
  background_count[0:(i + 1)] = hist[0:(i + 1)]
  background_count[(i + 1):(2 * i + 1)] = hist[(i - 1)::-1]
  probabilities = np.minimum(background_count / hist, 0.99)
  probabilities[0:(i + 1)] = 1
  th = bin_edges[np.argmin(probabilities >= prob_background) - 1]
  return th

def foreground_intensity(a, prob_foreground = 0.99):
  '''
  Identifies a threshold for pixel intensity above which pixels are part of
  the foreground with at least a **prob_background** estimated probability. 
  This works by assuming that most of the image is dark background, the
  single most common pixel brightness is the average brightness for a 
  background pixel, and that the brightnesses of background pixels are 
  distributed like the normal distribution. 
  
  Parameters
  ------------
  a : 2-D numpy array
    The grayscale image. Can be either floats on the interval [0,1] or
    ints on the interval [0,255]. 
  prob_foreground : float, optional
    The minimum (estimated) probability that a pixel is part of the 
    background. Must be < 1. Lower numbers will likely result in a lower
    returned threshold.
  
  Returns 
  --------
  th : float or int
    The threshold above which pixels in the image are likely part of the
    foreground. 
  '''
  if np.amax(a) <= 1:
    bins = np.linspace(0, 256/255, num = 257)
    a = np.round(255 * a) / 255
  else:
    bins = np.arange(257)
  # Assume that data from 256,000 pixels is sufficient
  if a.size > 256 * 1000:
    prob = float(256 * 1000) / a.size        
    a = a[(np.random.random(size = a.shape) < prob)]
  hist, bin_edges = np.histogram(a, bins = bins)  
  # Pad counts with 1 (to eliminate zeros)    
  hist = hist + 1
  i = np.argmax(hist)
  background_count = np.zeros((256))
  background_count[0:(i + 1)] = hist[0:(i + 1)]
  background_count[(i + 1):(2 * i + 1)] = hist[(i - 1)::-1]
  probabilities = 1 - np.minimum(background_count / hist, 1)
  th = bin_edges[np.argmax(probabilities >= prob_foreground)]
  return th

def background_threshold(img, prob_background = 1, num_blocks = None, 
             block_dims = None):
  '''
  The pixel intensity at every location in the image below which the pixel
  is likely part of the dark background. The threshold varies smoothly
  across the image. 
  
  Parameters
  ------------
  img : 2-D numpy array
    The grayscale image. Can be either floats on the interval [0,1] or
    ints on the interval [0,255]. 
  prob_background : float, optional
    The minimum probability (estimated) that a pixel below the threshold
    is part of the backround. Must be <= 1. Lower numbers will result in 
    higher thresholds. 
  num_blocks : int, optional
    The number of blocks of the image to use to create the threshold. 
  block_dims : tuple or numpy array
    The dimensions of the rectangular blocks. Dimensions should be less
    than the dimensions of the image. If left unspecified, the blocks will
    be squares with area approximately equal to two times the area of the
    image, divided by num_blocks.
  
  Returns 
  ----------
  th : 2-D numpy array
    The varying threshold that separates the dark background from the rest
    of the image. Has the same size and dimensions as img. 
  '''
  # Default number of blocks assumes 500x500 blocks are a good size
  if num_blocks is None:
    num_blocks = int(np.ceil(2 * img.size / 250000))
  th = threshold(img, background_intensity, num_blocks, block_dims, 0.003, 
           prob_background)
  return th
  
def foreground_threshold(img, prob_foreground = 0.99, num_blocks = None, 
             block_dims = None):
  '''
  The pixel intensity at every location in the image above which the pixel
  is likely part of the bright foreground. The threshold varies smoothly
  across the image. 
  
  Parameters
  ------------
  img : 2-D numpy array
    The grayscale image. Can be either floats on the interval [0,1] or
    ints on the interval [0,255]. 
  prob_foreground : float, optional
    The minimum probability (estimated) that a pixel above the threshold
    is part of the foreground. Must be <= 1. Lower numbers will result in 
    lower thresholds. 
  num_blocks : int, optional
    The number of blocks of the image to use to create the threshold. 
  block_dims : tuple or numpy array
    The dimensions of the rectangular blocks. Dimensions should be less
    than the dimensions of the image. If left unspecified, the blocks will
    be squares with area approximately equal to two times the area of the
    image, divided by num_blocks.
  
  Returns 
  ----------
  th : 2-D numpy array
    The varying threshold that separates the bright foreground from the 
    rest of the image. Has the same size and dimensions as img. 
  '''
  # Default number of blocks assumes 500x500 blocks are a good size
  if num_blocks is None:
    num_blocks = int(np.ceil(2 * img.size / 250000))
  th = threshold(img, foreground_intensity, num_blocks, block_dims, 0.003, 
           prob_foreground)
  return th

def flatten_background(img, prob_background = 1, num_blocks = None, 
             block_dims = None, return_background = False, mask = None):
  '''
  Finds the pixel intensity at every location in the image below which the 
  pixel is likely part of the dark background. Pixels darker than this 
  threshold are replaced by the value of the threshold at its location. This
  eliminates unusually dark regions. 
  
  Parameters
  ------------
  img : 2-D numpy array
    The grayscale image. Can be either floats on the interval [0,1] or
    ints on the interval [0,255]. 
  prob_background : float, optional
    The minimum probability (estimated) that a pixel below the threshold
    is part of the backround. Must be <= 1. Lower numbers will result in 
    higher thresholds. 
  num_blocks : int, optional
    The number of blocks of the image to use to create the threshold. 
  block_dims : tuple or numpy array
    The dimensions of the rectangular blocks. Dimensions should be less
    than the dimensions of the image. If left unspecified, the blocks will
    be squares with area approximately equal to two times the area of the
    image, divided by num_blocks.
  
  Returns
  --------
  flattened : 2-D numpy array
    An image equal to the input grayscale image where pixels are above
    the brightness of the background threshold and equal to the threshold
    everywhere else.
  background : 2-D numpy array of bools
    The pixels below the background threshold. 
  '''
  # Default number of blocks assumes 500x500 blocks are a good size
  if num_blocks is None:
    num_blocks = int(np.ceil(2 * img.size / 250000))
  background_level = threshold(img, background_intensity, num_blocks, 
                 block_dims, 0.003, mask, prob_background)
  background = img < background_level
  flattened = np.where(background, background_level, img)
  if return_background == False:
    return flattened
  else:
    return (flattened, background)