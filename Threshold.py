# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 13:05:12 2015

@author: benamy
"""

import numpy as np
from scipy.interpolate import SmoothBivariateSpline as spline2d 
from scipy.ndimage import distance_transform_edt
from scipy import stats
from skimage.morphology import (convex_hull_image, binary_dilation, 
                                binary_erosion, disk)

# import Mitchells_best_candidate
    
def threshold(a, threshold_function, num_blocks, block_dims = None, 
              smoothing_factor = 0.003, *args):
    a_dims = a.shape
    if num_blocks >= 16:
        spline_order = 3
    else:
        spline_order = int(np.sqrt(num_blocks) - 1)
    if spline_order == 0:
        return (np.ones_like(a) * threshold_function(a, *args))
    if block_dims is None:
        block_dim = int(round(np.sqrt(2 * a.size / num_blocks)))
        block_dims = (block_dim, block_dim)
    points = best_candidate_sample(a_dims, num_blocks)
    th = []    
    
    for p in points:
        block = get_block(a, p, block_dims)
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
    a_dims = a.shape    
    upper = max(0, center[0] - block_dims[0] / 2)
    lower = min(a_dims[0], center[0] + block_dims[0] / 2 + 1)
    left = max(0, center[1] - block_dims[1] / 2)
    right = min(a_dims[1], center[1] + block_dims[1] / 2 + 1)
    return a[upper:lower, left:right]

def get_convex_hull(points, a_dims):
    a = np.zeros(a_dims, dtype = bool)
    a[points[:,0], points[:,1]] = True
    return convex_hull_image(a)

def fix_border(spline, sample_points):
    border = (~ get_convex_hull(sample_points, spline.shape))
    ind = distance_transform_edt(border, return_distances = False, 
                                 return_indices = True)
    return spline[tuple(ind)]

def mode(a):
    return stats.mode(a.flat)[0][0]

def background_intensity(a, prob_background = 1):
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
    return bin_edges[np.argmin(probabilities >= prob_background) - 1]

def foreground_intensity(a, prob_foreground = 0.99):
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
    return bin_edges[np.argmax(probabilities >= prob_foreground)]

def background_threshold(img, prob_background = 1, num_blocks = None, 
                       block_dims = None):    
    # Default number of blocks assumes 500x500 blocks are a good size
    if num_blocks is None:
        num_blocks = int(np.ceil(2 * img.size / 250000))
    return threshold(img, background_intensity, num_blocks, block_dims, 0.003, 
                     prob_background)
    
def foreground_threshold(img, prob_foreground = 0.99, num_blocks = None, 
                         block_dims = None):    
    # Default number of blocks assumes 500x500 blocks are a good size
    if num_blocks is None:
        num_blocks = int(np.ceil(2 * img.size / 250000))
    return threshold(img, foreground_intensity, num_blocks, block_dims, 0.003, 
                     prob_foreground)

def flatten_background(img, prob_background = 1, num_blocks = None, 
                       block_dims = None):    
    # Default number of blocks assumes 500x500 blocks are a good size
    if num_blocks is None:
        num_blocks = int(np.ceil(2 * img.size / 250000))
    background_level = threshold(img, background_intensity, num_blocks, 
                                 block_dims, 0.003, prob_background)
    background = img < background_level
    return np.where(background, background_level, img)

'''
def force_monotonicity(a):
    # Force sequence to be monotonically increasing to/decreasing from maximum
    new_a = np.copy(a)    
    maximum = np.argmax(a)
    for i in np.arange(maximum, -1, -1):
'''     
    
    
