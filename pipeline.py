# -*- coding: utf-8 -*-
"""
Description:

Usage:
  pipeline.py --image <filename> --output <filename>
  pipeline.py -h | --help

Options:
  -h --help             Show this screen.
  --image <filename>    Filename of seismogram.
  --output <directory>  Filename of geojson output.

"""
import matplotlib.pyplot as plt
from skimage.color import rgb2gray
from skimage.morphology import medial_axis

from geojson import LineString, Feature, FeatureCollection, dump

from Threshold import flatten_background
from Ridge_Detection import find_ridges
from Binarization import local_min, binary_image
from Intersection_Detection import find_intersections
from Trace_Segmentation import get_segments

from docopt import docopt

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
    ridges = ridges_h | ridges_v
    # get binary image
    img_bin = binary_image(img_dark_removed, markers_trace=ridges,
                           markers_background=background)
    # get medial axis skeleton and distance transform
    img_skel, dist = medial_axis(img_bin, return_distance=True)
    # detect intersections
    intersections = find_intersections(img_bin, img_skel, dist)
    # break into segments
    segments = get_segments(img_gray, img_bin, img_skel, dist, intersections,
                            ridges_h, ridges_v)    
    #return (img_gray, ridges, img_bin, intersections, img_seg)
    return segments
    # detect center lines
    
    # connect segments
    
    # output data

def save_segments_as_geojson(segments, filepath):
    geojson_line_segments = []
    for seg in segments.itervalues():
        if seg.has_center_line == True:
            center_line = zip(seg.center_line.x, seg.center_line.y)
            feature = Feature(geometry = LineString(center_line))
            geojson_line_segments.append(feature)
    geojson_line_segments = FeatureCollection(geojson_line_segments)
    with open(filepath, 'w') as outfile:
        dump(geojson_line_segments, outfile)


if __name__ == '__main__':
  arguments = docopt(__doc__)
  in_file = arguments["--image"]
  out_file = arguments["--output"]

  if (in_file and out_file):
    image = plt.imread(in_file)
    segments = analyze_image(image)
    save_segments_as_geojson(segments, out_file)
  else:
    print(arguments)