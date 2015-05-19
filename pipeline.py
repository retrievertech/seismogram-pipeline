# -*- coding: utf-8 -*-
"""
Created on Tue May  5 12:21:23 2015

@author: benamy
"""
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
from skimage.morphology import medial_axis

from Threshold import flatten_background
from Ridge_Detection import find_ridges
from Binarization import local_min, binary_image
from Intersection_Detection import find_intersections
from Trace_Segmentation import get_segments

def analyze_image(img):
    # convert image to grayscale
    img_gray = rgb2gray(img)
    # get region of interest

    # (flatten background?)
    img_dark_removed, dark_pixels = flatten_background(img_gray, 0.95, 
                                                       return_background=True)
    # get horizontal and vertical ridges
    background = dark_pixels | local_min(img_gray)    
    ridges_h, ridges_v = find_ridges(img_dark_removed, background)
    ridges = (ridges_h | ridges_v)
    # get binary image
    img_bin = binary_image(img_dark_removed, markers_trace=ridges,
                           markers_background=background)
    # get medial axis skeleton and distance transform
    img_skel, dist = medial_axis(img_bin, return_distance=True)
    # detect intersections
    intersections = find_intersections(img_bin, img_skel, dist)
    # break into segments
    segments = get_segments(img_gray, img_bin, img_skel, dist, intersections)
    return (img_gray, ridges, img_bin, intersections, segments)
    # detect center lines
    
    # connect segments
    
    # output data
    
# function call
image = plt.imread('/home/benamy/Documents/Seismogram Project/Images/target.png')
image_gray, ridges, image_bin, image_intersections, img_seg = analyze_image(image)