import numpy as np
from skimage.transform import hough_line, hough_line_peaks

def get_hough_line_peaks(image, min_angle, max_angle, min_separation_distance, min_separation_angle):
  angles = np.deg2rad(np.arange(min_angle, max_angle, 0.5))
  hough, angles, distances = hough_line(image, angles)
  peak_hough, peak_angles, peak_distances = hough_line_peaks(hough, angles, distances,
                                              num_peaks=150,
                                              threshold=0.5*np.amax(hough),
                                              min_distance=min_separation_distance,
                                              min_angle=min_separation_angle)
  return (peak_hough, peak_angles, peak_distances)

def get_best_hough_lines(image, min_angle, max_angle, min_separation_distance, min_separation_angle):
  peak_hough, peak_angles, peak_distances = get_hough_line_peaks(image, min_angle, max_angle, min_separation_distance, min_separation_angle)
  best_hough_idx = np.argmax(peak_hough)
  return get_line_endpoints_in_image(image, peak_angles[best_hough_idx], peak_distances[best_hough_idx])

def get_all_hough_lines(image, min_angle, max_angle, min_separation_distance, min_separation_angle):
  _, peak_angles, peak_distances = get_hough_line_peaks(image, min_angle, max_angle, min_separation_distance, min_separation_angle)
  return [ get_line_endpoints_in_image(image, angle, radius) for angle, radius in zip(peak_angles, peak_distances)]

def get_line_endpoints_in_image(image, angle, radius):
  rows, cols = image.shape
  # from r = y * sin(theta) + x cos(theta)
  if (np.sin(angle) == 0):
    # vertical line at x = radius
    x0 = radius.astype(int)
    x1 = radius.astype(int)
    y0 = 0
    y1 = rows - 1
  else:
    # TODO: solve for points that are on the image boundary
    # instead of always using x0 = 0 and x1 = cols - 1
    x0 = 0
    x1 = cols - 1
    y0 = int((radius - x0 * np.cos(angle)) / np.sin(angle))
    y1 = int((radius - x1 * np.cos(angle)) / np.sin(angle))
  return ((x0, y0), (x1, y1))
