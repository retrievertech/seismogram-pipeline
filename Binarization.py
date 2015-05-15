# -*- coding: utf-8 -*-
"""
Created on Wed Feb  4 16:48:13 2015

@author: benamy
"""
import numpy as np
from scipy.ndimage.filters import gaussian_filter1d, gaussian_laplace
from math import sqrt, hypot, log
from skimage import color
from skimage import io
from skimage.util import img_as_float
from skimage.feature import peak_local_max
from skimage.transform import integral_image
from scipy.signal import argrelextrema
from skimage.morphology import dilation, erosion
from scipy.signal import convolve2d
from skimage.morphology import watershed, remove_small_objects
from scipy.interpolate import bisplrep, bisplev

from scipy.ndimage import maximum_filter

from skimage.filter import canny, sobel, gaussian_filter, threshold_otsu

import Threshold

def binary_image(image, markers_trace=None, markers_background=None,
                 min_trace_size=6, min_background_size=4):
    '''
    Creates a binary image.
    
    Parameters
    ------------
    image : numpy array
        Can either be a color (3-D) or grayscale (2-D) image.
    
    Returns
    ---------
    image_bin : 2-D Boolean numpy array
        A 2-D array with the same shape as the input image. Foreground pixels
        are True, and background pixels are False.
    '''
    if image.ndim != 2:
        image = color.rgb2gray(image)
    if markers_background == None:
        markers_background = get_background_markers(image)
    if markers_trace == None: 
        markers_trace = get_trace_markers(image)
    image_bin = watershed_segmentation(image, markers_trace, markers_background)
    #image_bin = image_bin & (~ fill_corners(canny(image)))
    image_bin = remove_small_segments_and_edges(image_bin, min_trace_size, 
                                                min_background_size)
    return image_bin

def watershed_segmentation(image_gray, markers_trace, markers_background,
                           ??force_breaks=True):
                               
# give option to exclude the canny edges from image_bin, to force breaks
# along the edges and help with segmentation later on
    '''    
    Segments the image into regions with one of two types (i.e. foreground
    and background) using a watershed algorithm.
    
    Parameters
    -----------
    image_gray : 2-D numpy array
        A grayscale image.
    markers_trace : 2-D Boolean numpy array
        An array with the same shape as image_gray, where the seeds of
        the trace regions are True.
    markers_background : 2-D Boolean numpy array
        An array with the same shape as image_gray, where the seeds of
        the background regions are True. 
        
    Returns
    ---------
    image_bin : 2-D Boolean numpy array
        A 2-D array with the same shape as the input image. Foreground pixels
        are True, and background pixels are False.
    '''
    bin_markers = np.zeros_like(image_gray, dtype=int)
    bin_markers = np.where(markers_trace, 2, 0)
    bin_markers = np.where(markers_background, 1, bin_markers)
    
    #image_sobel = sobel(gaussian_filter(image_gray, 1))
    image_sobel = sobel(image_gray) 
    image_canny = canny(image_gray)
    edges = np.maximum(image_canny.astype(float), image_sobel)
    
    image_bin = watershed(edges, bin_markers)
    image_bin = image_bin == 2
    return image_bin

def get_background_markers(image_gray):
    '''
    Finds the pixels that definitely belong in background regions.
    
    Parameters
    -----------
    image_gray : 2-D numpy array
        A grayscale image.
        
    Returns
    -----------
    markers_background : 2-D Boolean numpy array
        An array with the same shape as image_gray, where the seeds of
        the background regions are True. 
    '''
    dark_threshold = threshold_by_blocks(image_gray, 20, background_intensity)
    dark_pixels = image_gray <= dark_threshold
    image_smooth = gaussian_filter(image_gray, 1)    
    otsu = image_gray > threshold_otsu(image_gray)
    #minima = local_min(image_smooth) & np.logical_not(otsu)
    #minima = local_min(image_gray) & (~ otsu)    
    minima = local_min(image_gray)    
    
    markers_background = dark_pixels | minima
    return markers_background

def get_trace_markers(image_gray):
    '''
    Finds the pixels that definitely belong to traces.    
        
    Parameters
    -----------
    image_gray : 2-D numpy array
        A grayscale image.
        
    Returns
    -----------
    markers_trace : 2-D Boolean numpy array
        An array with the same shape as image_gray, where the seeds of
        the trace regions are True. 
    '''
    
    return find_all_ridges(image_gray)    
   
def remove_small_segments_and_edges(image_bin, min_trace_size = 6, 
                                    min_edge_length = 4): 
    '''
    placeholder docstring
    '''
    remove_small_objects(image_bin, min_size = min_trace_size, connectivity=2,
                         in_place = True)
    image_bin = ~image_bin
    remove_small_objects(image_bin, min_size = min_edge_length, connectivity=2,
                         in_place = True)
    image_bin = ~image_bin
    return image_bin

def fill_corners(image_bin):
    arr = np.where(image_bin, 1, -1)    
    
    ul_kernel = np.array([[-1, 1, 0], [1, 0, 0], [0, 0, 0]])    
    ur_kernel = np.array([[0, 1, -1], [0, 0, 1], [0, 0, 0]])    
    ll_kernel = np.array([[0, 0, 0], [1, 0, 0], [-1, 1, 0]])    
    lr_kernel = np.array([[0, 0, 0], [0, 0, 1], [0, 1, -1]])            
    
    upper_left = convolve2d(arr, ul_kernel, mode = 'same', boundary = 'symm')
    upper_right = convolve2d(arr, ur_kernel, mode = 'same', boundary = 'symm')
    lower_left = convolve2d(arr, ll_kernel, mode = 'same', boundary = 'symm')
    lower_right = convolve2d(arr, lr_kernel, mode = 'same', boundary = 'symm')
    corners = ((upper_left == 3) | (upper_right == 3) | (lower_left == 3) | 
                (lower_right == 3))
    return image_bin | corners

def peak_local_max_rows(a, include_border=False):    
    maxima = np.zeros_like(a,dtype=bool)
    maxima = np.logical_and( \
                        np.hstack((np.ones((a.shape[0],1)) * include_border, 
                              a[:,1:] >= a[:,:-1])), \
                        np.hstack((a[:,:-1] >= a[:,1:], 
                              np.ones((a.shape[0],1)) * include_border)))
    return maxima
    
def peak_local_max_cols(a, include_border=False):    
    maxima = np.zeros_like(a,dtype=bool)
    maxima = np.logical_and( \
                        np.vstack((np.ones((1,a.shape[1])) * include_border, 
                              a[1:,:] >= a[:-1,:])), \
                        np.vstack((a[:-1,:] >= a[1:,:], 
                              np.ones((1,a.shape[1])) * include_border)))
    return maxima

def local_min(image, min_distance=2):
    if np.amax(image) <= 1:
        image = np.uint8(image * 255)
    selem = np.ones((2 * min_distance + 1, 2*min_distance + 1))
    img = erosion(image, selem)
    return image == img

def local_max(image, min_distance=2):
    if np.amax(image) <= 1:
        image = np.uint8(image * 255)
    selem = np.ones((2 * min_distance + 1, 2*min_distance + 1))
    img = dilation(image, selem)
    return image == img

'''
def threshold_by_blocks(a, num_blocks, threshold_function, *args):
    a_dims = a.shape
    block_dims = [0,0]
    block_dims[0] = int(round(a_dims[0] /   \
                        round(np.sqrt(num_blocks * a_dims[0] / a_dims[1]))))
    block_dims[1] = int(round(a_dims[1] /   \
                        round(np.sqrt(num_blocks * a_dims[1] / a_dims[0]))))
    x = []
    y = []
    th = []    
    for row in xrange(0, a_dims[0], block_dims[0]):
        for col in xrange(0, a_dims[1], block_dims[1]):
            x.append(float(row) + (block_dims[0] - 1) / 2)   
            y.append(float(col) + (block_dims[1] - 1) / 2) 
            threshold = threshold_function(a[row:row + block_dims[0], \
                col:col + block_dims[1]], *args)
            th.append(threshold)
    x = np.asarray(x)    
    y = np.asarray(y)
    th = np.asarray(th)
    
    #fit = bisplrep(x,y,th,xb=0,xe=a_dims[0]-1,yb=0,ye=a_dims[1]-1)
    fit = bisplrep(x,y,th)    
    th_new = bisplev(np.arange(a_dims[0]), np.arange(a_dims[1]), fit)
    return th_new
    
def background_intensity(a):
    if np.amax(a) <= 1:
        bins = np.linspace(0, 1, num = 257)
    else:
        bins = np.arange(257)
    hist, bin_edges = np.histogram(a, bins = bins)
    i = np.argmax(hist)
    return bin_edges[i]
'''