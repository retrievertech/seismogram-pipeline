# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 13:58:26 2015

@author: benamy
"""

import numpy as np
from skimage.morphology import medial_axis, watershed, square
from scipy.ndimage import label
from skimage import color

image_bin = binary_image(img_dark_removed)
image_canny = canny(img_dark_removed)
image_bin = image_bin & (~ fill_corners(image_canny))

#image_bin = remove_small_segments_and_edges(image_bin, 6, 4)
image_skel, dist = medial_axis(image_bin, return_distance = True)
image_intersections = find_intersections(image_bin)
image_sobel = sobel(img_dark_removed)
steep_slopes = image_sobel > threshold_otsu(image_sobel)
steep_slopes = erosion(steep_slopes, square(3))
segments_bin = (image_skel & (~ image_intersections) & (~ image_canny) & 
                (~ steep_slopes))

rmat = reverse_medial_axis(segments_bin, dist)
_, rmat_dist = medial_axis(rmat, return_distance=True)
image_segments, num_segments = label(segments_bin, np.ones((3,3)))
image_segments = watershed(-rmat_dist, image_segments, mask = rmat)

traces_colored = normalize(image_segments)
traces_colored = gray2prism(traces_colored)
traces_colored = color_markers((~rmat), traces_colored, marker_color = [1,1,1])
traces_colored = image_overlay(image_gray, traces_colored, (~rmat))

traces_colored = black_to_white(traces_colored)
# Color background black
traces_colored = color_markers((rmat == 0), traces_colored, [0,0,0])

'''
store segments in objects
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
Doesn't work (yet)
def black_to_white(image):
    if image.ndim == 2:
        black = (image == 0)
        return np.where(black, 1, image)        
    else:
        black = (image[:,:] == np.array([0, 0, 0]))
        black = np.dstack((black, black, black))
        white_image = np.ones_like(image)
        return np.where(black, white_image, image)
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
