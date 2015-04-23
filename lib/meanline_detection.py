from timer import timeStart, timeEnd

timeStart("import libs")
from threshold_image import threshold_image
from hough_lines import get_hough_lines
from skimage.morphology import remove_small_objects
from scipy import misc
import numpy as np
import skimage.draw as skidraw
import geojson
timeEnd("import libs")

debug_dir = "debug"

def get_meanlines(masked_image, debug = False):
  timeStart("threshold image")
  black_and_white_image = threshold_image(masked_image)
  timeEnd("threshold image")

  timeStart("remove small objects")
  # TODO: make the small object size parameter a function of input image size or some scale factor
  # filtered_image = remove_small_objects(black_and_white_image, 500)
  filtered_image = remove_small_objects(black_and_white_image, 30)
  timeEnd("remove small objects")

  if debug:
    misc.imsave(debug_dir+"/filtered_image.png", filtered_image)

  timeStart("get hough lines")
  lines = get_hough_lines(filtered_image, min_angle=-120, max_angle=-70, min_separation_distance=9 , min_separation_angle=25)
  timeEnd("get hough lines")

  if debug:
    debug_image = np.copy(masked_image)
    line_coords = [ skidraw.line(line[0][0], line[0][1], line[1][0], line[1][1]) for line in lines ]
    for line in line_coords:
      debug_image[line] = 255
    misc.imsave(debug_dir+"/mean_lines.png", debug_image)

  return lines

def save_meanlines_as_geojson(lines, filepath):
  timeStart("saving to "+ filepath)
  lines = [ geojson.Feature(geometry = geojson.LineString(line)) for line in lines ]
  newFeature = geojson.FeatureCollection(lines)
  with open(filepath, 'w') as outfile:
    geojson.dump(newFeature, outfile)
  timeEnd("saving to "+ filepath)
