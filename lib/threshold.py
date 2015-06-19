# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 13:05:12 2015

@author: benamy
"""

from lib.timer import timeStart, timeEnd

import numpy as np
from scipy.interpolate import SmoothBivariateSpline as spline2d 
from scipy.ndimage import distance_transform_edt
from skimage.morphology import (convex_hull_image)
from numpy.ma.core import MaskedArray
from mitchells_best_candidate import best_candidate_sample
  
def threshold(a, threshold_function, num_blocks, block_dims = None, 
        smoothing = 0.003, debug_dir = None):
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
  smoothing : float, optional
    A parameter to adjust the smoothness of the 2-D smoothing spline. A
    higher number increases the smoothness of the output. An input of zero
    is equivalent to interpolation.
  *args : float, optional
    All other args are passed along to threshold_function
  
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
    return (np.ones_like(a) * threshold_function(a))

  if (type(a) is MaskedArray):
    mask = a.mask
  else:
    mask = np.zeros(a_dims, dtype=bool)

  candidate_coords = np.transpose(np.nonzero(~mask))
  
  if block_dims is None:
    block_dim = int(round(np.sqrt(2 * a.size / num_blocks)))
    block_dims = (block_dim, block_dim)

  timeStart("select block centers")
  points = best_candidate_sample(candidate_coords, num_blocks)
  timeEnd("select block centers")

  timeStart("calculate thresholds for blocks of size %s" % block_dim)
  th = []
  for p in points:
    block = get_block(a, p, block_dims)
    if (type(block) is MaskedArray):
      threshold = threshold_function(block.compressed())
    else:
      threshold = threshold_function(block)
    th.append(threshold)
  th = np.asarray(th)
  timeEnd("calculate thresholds for blocks of size %s" % block_dim)

  timeStart("fit 2-D spline")
  # Maybe consider using lower-order spline for large images 
  # (if large indices create problems for cubic functions)
  fit = spline2d(points[:,0], points[:,1], th, 
           bbox = [0, a_dims[0], 0, a_dims[1]], 
           kx = spline_order, ky = spline_order,
           s = num_blocks * smoothing)
  th_new = fit(x = np.arange(a_dims[0]), y = np.arange(a_dims[1])) 
  th_new = fix_border(th_new, points)
  timeEnd("fit 2-D spline")
  return th_new

def debug_blocks(a, points, block_dims, threshold_function, debug_dir):
  from scipy import misc
  from skimage.draw import line, circle
  from skimage.color import gray2rgb

  bad_block_points = []
  
  for p in points:
    block = get_block(a, p, block_dims)
    try:
      if (type(block) is MaskedArray):
        threshold_function(block.compressed())
      else:
        threshold_function(block)

    except Exception, e:
      print "threshold block error"
      print e
      bad_block_points.append(p)
      misc.imsave(debug_dir+"/bad_block_"+str(p)+".png", block)

  debug_image = gray2rgb(np.copy(a))
  
  def get_block_corners(center, size):
    half_side = size/2
    return [
      (center[0]+half_side, center[1]+half_side),
      (center[0]+half_side, center[1]-half_side),
      (center[0]-half_side, center[1]-half_side),
      (center[0]-half_side, center[1]+half_side)
    ]

  block_corners = [ get_block_corners(center, block_dims[0]) for center in bad_block_points ]
  block_line_coords = [
    [
      line(*corners[0]+corners[1]),
      line(*corners[1]+corners[2]),
      line(*corners[2]+corners[3]),
      line(*corners[3]+corners[0])
    ] for corners in block_corners
  ]
  
  for block in block_line_coords:
    for line_coords in block:
      rr, cc = line_coords
      mask = (rr >= 0) & (rr < debug_image.shape[0]) & (cc >= 0) & (cc < debug_image.shape[1])
      debug_image[rr[mask], cc[mask]] = [1.0, 0, 0]

  for center in points:
    rr, cc = circle(center[0], center[1], 20)
    debug_image[rr, cc] = [1.0, 0, 0]

  misc.imsave(debug_dir+"/threshold_blocks.png", debug_image)

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

def get_hist_and_background_count(a):
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
  
  Returns 
  --------
  hist, bin_edges, background_count : 1-D numpy arrays
    The histogram bin values and edges, and the expected distribution of values
    for background (i.e. non-trace) pixels.
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

  peak_pixel_color = get_most_common_background_pixel_color(hist)
  
  # Copy the histogram values from 0 -> peak into background_count
  background_count = np.zeros((256))
  background_count[0:(peak_pixel_color + 1)] = hist[0:(peak_pixel_color + 1)]

  # Reflect the histogram values from 0 -> peak and copy them
  # into background_count[peak -> end]; this assumes the distribution
  # of background pixel values is symmetrical about its peak
  background_count[(peak_pixel_color + 1):(2 * peak_pixel_color + 1)] = hist[(peak_pixel_color - 1)::-1]
  
  return hist, bin_edges, background_count

def get_most_common_background_pixel_color(hist):
  # Assume the most common pixel value < 128 is the peak
  # of the background pixel distribution
  return np.argmax(hist[0:128])

def make_background_thresh_fun(prob_background = 1):

  def get_background_thresh(a):
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
    hist, bin_edges, background_count = get_hist_and_background_count(a)
    probabilities = np.minimum(background_count / hist, 0.99)
    peak_pixel_color = get_most_common_background_pixel_color(hist)
    probabilities[0:(peak_pixel_color + 1)] = 1
    th = bin_edges[np.argmin(probabilities >= prob_background) - 1]
    return th

  return get_background_thresh

def make_foreground_thresh_fun(prob_foreground = 0.99):

  def get_foreground_thresh(a):
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
    hist, bin_edges, background_count = get_hist_and_background_count(a)
    probabilities = 1 - np.minimum(background_count / hist, 1)
    th = bin_edges[np.argmax(probabilities >= prob_foreground)]
    return th

  return get_foreground_thresh

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

  get_background_thresh = make_background_thresh_fun(prob_background)
  
  return threshold(img, get_background_thresh, num_blocks, block_dims,
                   smoothing=0.003)
  
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
  
  get_foreground_thresh = make_foreground_thresh_fun(prob_foreground)
  
  return threshold(img, get_foreground_thresh, num_blocks, block_dims,
                   smoothing=0.003)

def flatten_background(img, prob_background = 1, num_blocks = None, 
             block_dims = None, return_background = False, debug_dir = None):
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

  timeStart("calculate background threshold with %s blocks" % num_blocks)
  get_background_thresh = make_background_thresh_fun(prob_background)
  background_level = threshold(img, get_background_thresh, num_blocks, 
                               block_dims, smoothing=0.003, debug_dir=debug_dir)
  timeEnd("calculate background threshold with %s blocks" % num_blocks)

  timeStart("select background pixels")
  background = img < background_level
  timeEnd("select background pixels")

  timeStart("raise background pixels")
  flattened = np.where(background, background_level, img)
  timeEnd("raise background pixels")

  if return_background is False:
    return flattened
  else:
    return (flattened, background)
