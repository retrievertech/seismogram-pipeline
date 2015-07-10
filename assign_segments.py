# -*- coding: utf-8 -*-
"""

Description:
  Assign segments to meanlines based on average y values.
  
Usage:
  assign_segments.py --segments <filename> (--output <filename> | --output_csv <filaname>)
  get_endpoints.py -h | --help

Options:
  -h --help                Show this screen.
  --segments <filename>    Filename of segments.json
  --output <filename>      File to write geojson to.
  --output_csv <filename>  File to write CSV to.
"""
from docopt import docopt
import geojson
import numpy as np
import matplotlib.pyplot as plt
from lib.geojson_io import get_features
from lib.timer import timeStart, timeEnd
from geojson import Feature, FeatureCollection, LineString


meanline_database = {}
meanline_comp = []
domain = []
segment_arrays = []
all_segments = []
x_plot = []
y_plot = []
def assign_segments(segments, meanlines, segment_data):
    """Given segments(a geojson file of all points of segments), meanlines(start and endpoints of the meanlines)
    and segment_data(geojson output of my script get_endpoints), will assign each segment to a meanline based 
    on the average y values"""
    
    count = 0
    for meanline in meanlines["features"]:
        meanline_info = {"segments": [], "distances": [], "domain": []}
        meanline_assigned = {"meanline": 0, "slope": 0}
        meanline_assigned["meanline"] = count
        meanline_coordinates = meanlines["features"][count]["geometry"]["coordinates"]
        meanline_assigned["slope"] = (float(meanline_coordinates[1][1])-float(meanline_coordinates[0][1]))/(float(meanline_coordinates[1][0])-float(meanline_coordinates[0][0]))
        meanline_comp.append(meanline_assigned)
        meanline_database.update({count: meanline_info})
        count = count+1
    """assigns meanlines to a database with info on its slope, which segments have been assigned to any given meanline, 
    and the distance of the average y to the point on the meanline in the middle of the segment's x domain. Also 
    contains information of which x-domains are currently assigned to on the meanline, not yet in use."""

        
    for segment in segments["features"]:
        coordinates = np.array(segment["geometry"]["coordinates"])
        temp_domain = [coordinates[0,0], coordinates[len(coordinates)-1, 0]]
        domain.append(temp_domain)
    """sends the domain of each segment to a variable called domain"""
    
    segment_no = 0
    for segment in segment_data["features"]:
        dist = 15
        for meanline in xrange(len(meanline_comp)):
            seg_dist = abs(segment["properties"]["average_y"]-(meanline_comp[meanline]["slope"]*(np.mean(domain[segment["id"]]) - meanlines["features"][meanline]["geometry"]["coordinates"][0][0])+meanlines["features"][meanline]["geometry"]["coordinates"][0][1]))
            if  seg_dist < dist:
                dist = seg_dist
                
                meanline_database[meanline]["segments"].append(segment["id"])
                meanline_database[meanline]["distances"].append(dist)
                meanline_database[meanline]["domain"].append(domain[segment["id"]])
        segment_no += 1
    """finds the average y of the segment, compares it to each meanline. assigns it to a meanline if it is less than 
    15 pixels away."""    
    
    for numbers in xrange(len(meanline_database)):
        which_segments = meanline_database[numbers]["segments"]
        segment_arrays.append(which_segments)
        
    
    for meanline in xrange(len(segment_arrays)):
        each_segment = []
        x_plot_meanline = []
        y_plot_meanline = []
        for ids in xrange(len(segment_arrays[meanline])):
            index = segment_arrays[meanline][ids]
            segment_array = np.array(segments["features"][index]["geometry"]["coordinates"])
            
            each_segment.append(segment_array)
        all_segments.append(each_segment)
        for segment_no in xrange(len(each_segment)):
            for segment_length in xrange(len(each_segment[segment_no])):
                x_plot_meanline.append(each_segment[segment_no][segment_length][0])
                y_plot_meanline.append(each_segment[segment_no][segment_length][1])
        x_plot.append(x_plot_meanline)
        y_plot.append(y_plot_meanline)
    """makes a data table of arrays with x and y values for points assigned to each meanline"""
    
    plt.figure(num=1, figsize=(36, 12), dpi=1600)
    plt.plot(x_plot[0], y_plot[0], 'rs', x_plot[1], y_plot[1], 'gs', x_plot[2], y_plot[2], 'bs', x_plot[3], y_plot[3], 'rs', x_plot[4], y_plot[4], 'gs', x_plot[5], y_plot[5], 'bs', x_plot[6], y_plot[6], 'rs', x_plot[7], y_plot[7], 'gs', x_plot[8], y_plot[8], 'bs', x_plot[9], y_plot[9], 'rs', x_plot[10], y_plot[10], 'gs', x_plot[11], y_plot[11], 'bs', x_plot[12], y_plot[12], 'rs', x_plot[13], y_plot[13], 'gs', x_plot[14], y_plot[14], 'bs', x_plot[15], y_plot[15], 'rs', x_plot[16], y_plot[16], 'gs', x_plot[17], y_plot[17], 'bs', x_plot[18], y_plot[18], 'rs', x_plot[19], y_plot[19], 'gs', x_plot[20], y_plot[20], 'bs', x_plot[21], y_plot[21], 'rs', x_plot[22], y_plot[22], 'gs', x_plot[23], y_plot[23], 'bs', x_plot[24], y_plot[24], 'bs')
    plt.axis([0, 4000, 1600, 0])
    plt.show()
    plt.savefig('testplot.png')
    """plots these segments using matlibplot, different colors represent different meanlines"""

"""as of now, it is in a format where it accesses specific files on my computer. I would appreciate if somebody
could help me turn it into a command line usable format"""
        
segments = get_features('C:\Users\Lowell\Documents\GitHub\seismogram-pipeline\clean\segments.json')
meanlines = get_features('C:\Users\Lowell\Documents\GitHub\seismogram-pipeline\clean\meanlines.json')
segment_data = get_features('C:\Users\Lowell\Documents\GitHub\seismogram-pipeline\clean\endpoints.json')
assign_segments(segments, meanlines, segment_data)            
