from timer import timeStart, timeEnd

timeStart("import libs")
from threshold_image import threshold_image
from hough_lines import get_hough_lines
from skimage.morphology import remove_small_objects
from scipy import misc
import numpy as np
import skimage.draw as skidraw
from skimage.color import gray2rgb
import geojson
timeEnd("import libs")

PARAMS = {
  "small-object-size": lambda scale: int(500*scale*scale)
}

def detect_meanlines(masked_image, scale=1, debug_dir=False):
  timeStart("threshold image")
  black_and_white_image = threshold_image(masked_image)
  timeEnd("threshold image")

  if debug_dir:
    misc.imsave(debug_dir+"/thresholded_image.png", black_and_white_image)

  timeStart("remove small objects")
  filtered_image = remove_small_objects(black_and_white_image, PARAMS["small-object-size"](scale))
  timeEnd("remove small objects")

  if debug_dir:
    misc.imsave(debug_dir+"/filtered_image.png", filtered_image)

  timeStart("get hough lines")
  lines = get_hough_lines(filtered_image, min_angle=-120, max_angle=-70, min_separation_distance=9 , min_separation_angle=25)
  timeEnd("get hough lines")

  if debug_dir:
    debug_image = gray2rgb(np.copy(masked_image))
    line_coords = [ skidraw.line(line[0][1], line[0][0], line[1][1], line[1][0]) for line in lines ]
    for line in line_coords:
      rr, cc = line
      mask = (rr >= 0) & (rr < debug_image.shape[0]) & (cc >= 0) & (cc < debug_image.shape[1])
      debug_image[rr[mask], cc[mask]] = [1.0, 0, 0]
    misc.imsave(debug_dir+"/mean_lines.png", debug_image)

  return lines

def meanlines_to_geojson(lines):
  lines = [ geojson.Feature(geometry = geojson.LineString(line), id = idx) for idx, line in enumerate(lines) ]
  newFeature = geojson.FeatureCollection(lines)
  return newFeature
