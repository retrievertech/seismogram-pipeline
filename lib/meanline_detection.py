from timer import timeStart, timeEnd
from debug import Debug

from otsu_threshold_image import otsu_threshold_image
from hough_lines import get_all_hough_lines
from skimage.morphology import remove_small_objects
import numpy as np
import skimage.draw as skidraw
from skimage.color import gray2rgb
import numpy.ma as ma
import geojson

PARAMS = {
  "small-object-size": lambda scale: int(500*scale*scale),
  "trace-spacing": lambda scale: int(150*scale)
}

def detect_meanlines(masked_image, corners, scale=1, return_stats=False):
  padding = PARAMS["trace-spacing"](scale) / 2

  timeStart("bound image")
  # effectively shrink the roi by a distance **padding**
  top_bound = padding + np.amax([corners["top_left"][1], corners["top_right"][1]])
  bottom_bound = -padding + np.amin([corners["bottom_left"][1], corners["bottom_right"][1]])
  left_bound = padding + np.amax([corners["bottom_left"][0], corners["top_left"][0]])
  right_bound = -padding + np.amin([corners["top_right"][0], corners["bottom_right"][0]])

  # mask all image values outside of this shrunken roi
  bounded_image = masked_image.copy()
  bounded_image[:top_bound, :] = ma.masked
  bounded_image[bottom_bound:, :] = ma.masked
  bounded_image[:, :left_bound] = ma.masked
  bounded_image[:, right_bound:] = ma.masked
  timeEnd("bound image")

  Debug.save_image("meanlines", "bounded_image", bounded_image.filled(0))

  timeStart("threshold image")
  black_and_white_image = otsu_threshold_image(bounded_image)
  timeEnd("threshold image")

  Debug.save_image("meanlines", "thresholded_image", black_and_white_image)

  timeStart("remove small objects")
  filtered_image = remove_small_objects(black_and_white_image, PARAMS["small-object-size"](scale))
  timeEnd("remove small objects")

  Debug.save_image("meanlines", "filtered_image", filtered_image)

  timeStart("get hough lines")  
  min_separation_distance = int((2.0/3) * PARAMS["trace-spacing"](scale))
  lines, stats = get_all_hough_lines(filtered_image, min_angle=-100, max_angle=-80,
                              min_separation_distance=min_separation_distance,
                              min_separation_angle=5, return_stats=True)
  timeEnd("get hough lines")

  if Debug.active:
    debug_image = gray2rgb(np.copy(masked_image))
    line_coords = [ skidraw.line(line[0][1], line[0][0], line[1][1], line[1][0]) for line in lines ]
    for line in line_coords:
      rr, cc = line
      mask = (rr >= 0) & (rr < debug_image.shape[0]) & (cc >= 0) & (cc < debug_image.shape[1])
      debug_image[rr[mask], cc[mask]] = [1.0, 0, 0]
    Debug.save_image("meanlines", "meanlines", debug_image)

  if return_stats:
    return (lines, stats)
  else:
    return lines

def meanlines_to_geojson(lines):
  lines = [ geojson.Feature(geometry = geojson.LineString(line), id = idx) for idx, line in enumerate(lines) ]
  newFeature = geojson.FeatureCollection(lines)
  return newFeature
