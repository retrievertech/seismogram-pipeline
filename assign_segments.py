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
import json

meanline_database = {}
timing_marks = {}
meanline_comp = []
domain = []
segment_arrays = []
all_segments = []
x_plot = []
y_plot = []
stranded_segments = []
overlap = []
orphan_x = []
orphan_y = []
meanline_6_timing = []
all_timing = []
timing_x = []
timing_y = []
timing_spacing = 232

    
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
    contains information of which x-domains are currently assigned to on the meanline"""

        
    for segment in segments["features"]:
        coordinates = np.array(segment["geometry"]["coordinates"])
        temp_domain = [coordinates[0,0], coordinates[len(coordinates)-1, 0]]
        domain.append(temp_domain)
    """sends the domain of each segment to a variable called domain"""
    
    for segment in segment_data["features"]:
        which_meanline = 0
        dist = 20
        overlap_points = 0
        seg_isin = []
        #Distance depends on scale: play with this parameter

        for meanline in xrange(len(meanline_comp)):
            seg_dist = abs(segment["properties"]["average_y"]-(meanline_comp[meanline]["slope"]*(np.mean(domain[segment["id"]]) - meanlines["features"][meanline]["geometry"]["coordinates"][0][0])+meanlines["features"][meanline]["geometry"]["coordinates"][0][1]))
            if  seg_dist < dist:
                dist = seg_dist
                which_meanline = meanline
        if dist == 20:
            dist = "null"
        
        for domain_check in xrange(len(meanline_database[which_meanline]["domain"])):
            overlapping = list(set(range(meanline_database[which_meanline]["domain"][domain_check][0], meanline_database[which_meanline]["domain"][domain_check][1])).intersection(range(int(domain[segment["id"]][0]), int(domain[segment["id"]][1]+1)))) 
            if len(overlapping) != 0:
                seg_isin.append(meanline_database[which_meanline]["segments"][domain_check])
            overlap_points += len(overlapping)
        
            
            
        if overlap_points <= 20 and dist != "null":
            meanline_database[which_meanline]["segments"].append(segment["id"])
            meanline_database[which_meanline]["distances"].append(dist)
            meanline_database[which_meanline]["domain"].append(domain[segment["id"]])
        
        elif dist == "null":
            stranded_segments.append(segment["id"])

        else:
            for seg2seg in seg_isin:
                if meanline_database[which_meanline]["distances"][meanline_database[which_meanline]["segments"].index(seg2seg)] > dist:
                    meanline_database[which_meanline]["distances"].pop(meanline_database[which_meanline]["segments"].index(seg2seg))
                    meanline_database[which_meanline]["domain"].pop(meanline_database[which_meanline]["segments"].index(seg2seg))
                    stranded_segments.append(meanline_database[which_meanline]["segments"].pop(meanline_database[which_meanline]["segments"].index(seg2seg)))
        
    """finds the average y of the segment, compares it to each meanline. assigns it to a meanline if it is less than
    15 pixels away."""  
    

    
    for meanline_time in xrange(len(meanline_comp)):
        meanline_timing = []
        for stranded_timing in stranded_segments:
            if 5 < meanline_comp[meanline_time]["slope"]*((segments["features"][stranded_timing]["geometry"]["coordinates"][0][0]) - meanlines["features"][meanline_time]["geometry"]["coordinates"][0][0]) + meanlines["features"][meanline_time]["geometry"]["coordinates"][0][1] - segments["features"][stranded_timing]["geometry"]["coordinates"][0][1] < 100 and len(segments["features"][stranded_timing]["geometry"]["coordinates"]) < 15 and segment_data["features"][stranded_timing]["properties"]["standard_deviation"] < 8:
                meanline_timing.append(stranded_timing)
        print meanline_time
        certain = []
        for timings in meanline_timing:
            timing_list = []
            timing_guess = range(segment_data["features"][timings]["geometry"]["coordinates"][0][0], 4000, 232)
            number_included = 0
            for comb in meanline_timing:
                for guesses in timing_guess:
                    if abs(segment_data["features"][comb]["geometry"]["coordinates"][0][0] - guesses) < 11:
                        number_included += 1
                        timing_list.append(comb)
            print timing_list
        
            if len(timing_list) > len(certain):
                certain = timing_list
                print certain
        print meanline_timing
        print certain
        meanline_timing = certain
        print meanline_timing
        each_timing = []
        x_plot_timing = []
        y_plot_timing = []
        for times in meanline_timing:
            times_array = np.array(segments["features"][times]["geometry"]["coordinates"])
            
            each_timing.append(times_array)
        all_timing.append(each_timing)
        for timing_no in xrange(len(each_timing)):
            for timing_length in xrange(len(each_timing[timing_no])):
                x_plot_timing.append(each_timing[timing_no][timing_length][0])
                y_plot_timing.append(each_timing[timing_no][timing_length][1])
        timing_x.append(x_plot_timing)
        timing_y.append(y_plot_timing)
        timing_marks.update({meanline_time: meanline_timing})
        
    
    
    
    
    
    """
    still_going = True
    while still_going:
        to_pop = []
        go_check = 0
        for values in stranded_segments:
            try:
                for next_to in xrange(len(meanline_database)):
                    for seg_val in meanline_database[next_to]["segments"]:
                        if (0 <= (segment_data["features"][seg_val]["geometry"]["coordinates"][0][0]-segment_data["features"][values]["geometry"]["coordinates"][1][0]) < 40) and (abs(segment_data["features"][seg_val]["geometry"]["coordinates"][0][1]-segment_data["features"][values]["geometry"]["coordinates"][1][1]) < 100):
                            grey_left = segments["features"][values]["properties"]["values"]
                            left_values = []
                            for grey_values in grey_left:
                                left_values.append(grey_left)
                            left_avg = np.mean(left_values[len(left_values)-1] + left_values[len(left_values)-2] + left_values[len(left_values)-3])
                            grey_right = segments["features"][seg_val]["properties"]["values"]
                            right_values = []
                            for grey_values in grey_right:
                                right_values.append(grey_right)
                            right_avg = np.mean(right_values[0] + right_values[1] + right_values[2])
                            domain_overlap = []    
                            for missing_domain in meanline_database[next_to]["domain"]:
                                overlap_list = list(set(range(int(missing_domain[0]), int(missing_domain[1]))).intersection(range(int(segment_data["features"][values]["geometry"]["coordinates"][0][0]), int(segment_data["features"][values]["geometry"]["coordinates"][1][0]))))
                                if  overlap_list != []:
                                    domain_overlap.append(overlap_list)
                            if len(domain_overlap) < 1 and abs(left_avg - right_avg) < 100:
                                meanline_database[next_to]["segments"].append(values)
                                meanline_database[next_to]["distances"].append(100)
                                meanline_database[next_to]["domain"].append(domain[values])
                                to_pop.append(values)
                                go_check = 1
                            
                        elif (0 <= (segment_data["features"][values]["geometry"]["coordinates"][0][0]-segment_data["features"][seg_val]["geometry"]["coordinates"][1][0]) < 40) and (abs(segment_data["features"][values]["geometry"]["coordinates"][0][1]-segment_data["features"][seg_val]["geometry"]["coordinates"][1][1]) < 100):
                            grey_left = segments["features"][seg_val]["properties"]["values"]
                            left_values = []
                            for grey_values in grey_left:
                                left_values.append(grey_left)
                            left_avg = np.mean(left_values[len(left_values)-1] + left_values[len(left_values)-2] + left_values[len(left_values)-3])
                            grey_right = segments["features"][values]["properties"]["values"]
                            right_values = []
                            for grey_values in grey_right:
                                right_values.append(grey_right)
                            right_avg = np.mean(right_values[0] + right_values[1] + right_values[2])
                            domain_overlap = []    
                            for missing_domain in meanline_database[next_to]["domain"]:
                                overlap_list = list(set(range(int(missing_domain[0]), int(missing_domain[1]))).intersection(range(int(segment_data["features"][values]["geometry"]["coordinates"][0][0]), int(segment_data["features"][values]["geometry"]["coordinates"][1][0]))))
                                if  overlap_list != []:
                                    domain_overlap.append(overlap_list)
                            if len(domain_overlap) < 1 and abs(left_avg - right_avg) < 100:
                                meanline_database[next_to]["segments"].append(values)
                                meanline_database[next_to]["distances"].append(100)
                                meanline_database[next_to]["domain"].append(domain[values])
                                to_pop.append(values)
                                go_check = 1
            except IndexError:
                pass
        try:
            for the_segments in to_pop:
                stranded_segments.pop(stranded_segments.index(the_segments))         
        except ValueError:
            pass
        if go_check == 0:
            still_going = False
    """
    
    """still_going loop will assign orphaned segments to a meanline where segments have already been assigned, working backwards from the nearest orphaned segment. It will rerun the loop until there are no more 
    orphaned segments being assigned to neighboring segments' meanlines."""      
        
        
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
      
    
    
    
    orphan_array = []
    for orphan in stranded_segments:
        each_orphan = np.array(segments["features"][orphan]["geometry"]["coordinates"])
        orphan_array.append(each_orphan)
    
    for orphan_no in xrange(len(orphan_array)):
        for orphan_length in xrange(len(orphan_array[orphan_no])):
            orphan_x.append(orphan_array[orphan_no][orphan_length][0])
            orphan_y.append(orphan_array[orphan_no][orphan_length][1])
            
    plt.figure(num=1, figsize=(36, 16), dpi=2000)
    plt.plot(timing_x[0], timing_y[0], 'bs', timing_x[1], timing_y[1], 'go', timing_x[2], timing_y[2], 'ro', timing_x[3], timing_y[3], 'co', timing_x[4], timing_y[4], 'mo', timing_x[5], timing_y[5], 'yo', timing_x[6], timing_y[6], 'ko', timing_x[7], timing_y[7], 'wo')
    plt.axis([0, 3600, 1600, 0])
    plt.show()
    
    plt.figure(num=2, figsize=(36, 16), dpi=2000)
    plt.plot(x_plot[0], y_plot[0], 'bs', x_plot[1], y_plot[1], 'go', x_plot[2], y_plot[2], 'ro', x_plot[3], y_plot[3], 'co', x_plot[4], y_plot[4], 'mo', x_plot[5], y_plot[5], 'yo', x_plot[6], y_plot[6], 'ko', x_plot[7], y_plot[7], 'wo')
    plt.axis([0, 3600, 1600, 0])
    plt.show()
    

        
    
    
    plt.figure(num=3, figsize=(36, 16), dpi=2000)
    plt.plot(orphan_x, orphan_y, 'bo')
    plt.axis([0, 3600, 1600, 0])
    plt.show()
    
    """plt.figure(num=1, figsize=(51, 17), dpi=2000)
    plt.plot(x_plot[0], y_plot[0], 'bs', x_plot[1], y_plot[1], 'go', x_plot[2], y_plot[2], 'ro', x_plot[3], y_plot[3], 'co', x_plot[4], y_plot[4], 'mo', x_plot[5], y_plot[5], 'yo', x_plot[6], y_plot[6], 'ko', x_plot[7], y_plot[7], 'wo', x_plot[8], y_plot[8], 'b^', x_plot[9], y_plot[9], 'go', x_plot[10], y_plot[10], 'ro', x_plot[11], y_plot[11], 'co', x_plot[12], y_plot[12], 'mo', x_plot[13], y_plot[13], 'yo', x_plot[14], y_plot[14], 'ko', x_plot[15], y_plot[15], 'wo', x_plot[16], y_plot[16], 'bo', x_plot[17], y_plot[17], 'go', x_plot[18], y_plot[18], 'ro', x_plot[19], y_plot[19], 'co', x_plot[20], y_plot[20], 'mo', x_plot[21], y_plot[21], 'yo', x_plot[22], y_plot[22], 'ko', x_plot[23], y_plot[23], 'wo', x_plot[24], y_plot[24], 'ys')
    plt.axis([0, 8000, 3200, 0])
    plt.show()"""
    
    """plots these segments using matlibplot, different colors represent different meanlines"""

def generate_json(data):
    """
    Given a data dictionary (generated by get_endpoint_data), returns a GeoJson object of the data.
    """
    json_assign = {}
    for key in data.keys():    
        json_assign.update({int(key): meanline_database[key]["segments"]})
        
    with open('assignment.txt', 'w') as outfile:
        json.dump(json_assign, outfile)    
        
"""as of now, it is in a format where it accesses specific files on my computer. I would appreciate if somebody
could help me turn it into a command line usable format"""
        
segments = get_features('C:\Users\Lowell\Documents\GitHub\seismogram-pipeline\crop\segments.json')
meanlines = get_features('C:\Users\Lowell\Documents\GitHub\seismogram-pipeline\crop\meanlines.json')
segment_data = get_features('C:\Users\Lowell\Documents\GitHub\seismogram-pipeline\crop\endpoints.json')
assign_segments(segments, meanlines, segment_data)            
data = meanline_database
generate_json(data)
