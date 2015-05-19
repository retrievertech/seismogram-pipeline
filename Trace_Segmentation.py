# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 13:58:26 2015

@author: benamy
"""

import numpy as np
from skimage.morphology import (medial_axis, watershed, square, binary_erosion,
                                square)
from scipy.ndimage import label
from skimage import color
from skimage.filter import sobel, canny, threshold_otsu

from Reverse_Medial_Axis import reverse_medial_axis
from Binarization import fill_corners

def get_segments(img_gray, img_bin, img_skel, dist, img_intersections):
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
    return image_segments

'''
store segments in objects
'''

'''
dims = image_segments.shape
ridge_crests = find_all_ridges(img_dark_removed)

segments = []
for i in np.arange(1, num_segments + 1):
    pixel_coords = np.argwhere(image_segments == i)
    seg = segment(pixel_coords, dims, ID=i)
    seg.add_ridge_line(np.argwhere(seg.binary_image() & ridge_crests))
    seg.plot_pixel_series()
    #seg.plot_center_line()
    segments.append(seg)
'''

def image_overlay(img, overlay, mask = None):
    if img.ndim == 2:
        img = color.gray2rgb(img)
    if overlay.ndim == 2:
        overlay = color.gray2rgb(overlay)
    if mask.ndim == 2:
        mask = np.dstack((mask, mask, mask))
    images_combined = 0.5 * (img + overlay)
    return np.where(mask, img, images_combined)
    
def ridges_to_centerline(ridge_h, ridge_v):
    domain_h = np.array([np.amin(ridge_h[:,1]), np.amax(ridge_v[:,1])],
                         dtype=int)
    domain_v = np.array([np.amin(ridge_v[:,1]), np.amax(ridge_v[:,1])],
                         dtype=int)
    if domain_v[0] < domain_h[0]:
        ridge_v = ridge_v[(ridge_v[:,1] != domain_v[0]),:]
    if domain_v[1] > domain_h[1]:
        ridge_v = ridge_v[(ridge_v[:,1] != domain_v[1]),:]
    ridge = np.vstack(ridge_h, ridge_v)
    return ridge_line_to_series(ridge)
