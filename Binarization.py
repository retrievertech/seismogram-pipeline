# -*- coding: utf-8 -*-
"""
Created on Wed Feb  4 16:48:13 2015

@author: benamy
"""
import numpy as np
from skimage import color
from skimage.morphology import dilation, erosion
from scipy.signal import convolve2d
from skimage.morphology import watershed, remove_small_objects
from skimage.filter import canny, sobel

from Threshold import background_threshold
from Ridge_Detection import find_ridges

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
        markers_trace = get_trace_markers(image, markers_background)
    image_bin = watershed_segmentation(image, markers_trace, 
                                       markers_background)
    #image_bin = image_bin & (~ fill_corners(canny(image)))
    image_bin = remove_small_segments_and_edges(image_bin, min_trace_size, 
                                                min_background_size)
    return image_bin

def watershed_segmentation(image_gray, markers_trace, markers_background,
                           force_breaks=True):
                               
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
    dark_pixels = image_gray <= background_threshold(image_gray, 0.95)
    minima = local_min(image_gray)    
    markers_background = dark_pixels | minima
    return markers_background

def get_trace_markers(image_gray, background):
    '''
    Finds the pixels that definitely belong to traces.    
        
    Parameters
    -----------
    image_gray : 2-D numpy array
        A grayscale image.
    background : 2-D numpy array of bools
        Pixels in the dark background. 
        
    Returns
    -----------
    markers_trace : 2-D Boolean numpy array
        An array with the same shape as image_gray, where the seeds of
        the trace regions are True. 
    '''
    ridges_h, ridges_v = find_ridges(image_gray, background)
    ridges_all = ridges_h | ridges_v
    return ridges_all
   
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
    selem = np.ones((2 * min_distance + 1, 2 * min_distance + 1))
    img = erosion(image, selem)
    return image == img

def local_max(image, min_distance=2):
    if np.amax(image) <= 1:
        image = np.uint8(image * 255)
    selem = np.ones((2 * min_distance + 1, 2*min_distance + 1))
    img = dilation(image, selem)
    return image == img