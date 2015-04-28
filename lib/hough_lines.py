import numpy as np
from skimage.transform import hough_line, hough_line_peaks

def get_hough_lines(image, min_angle, max_angle, min_separation_distance, min_separation_angle):
  angles = np.deg2rad(np.arange(min_angle, max_angle, 1))
  hough, angles, distances = hough_line(image, angles)
  peak_hough, peak_angles, peak_distances = hough_line_peaks(hough, angles, distances, num_peaks = 150, threshold = 0.5*np.amax(hough), min_distance = min_separation_distance, min_angle = min_separation_angle)

  lines = []
  rows, cols = image.shape
  for angle, dist in zip(peak_angles, peak_distances):
    # from r = y * sin(theta) + x cos(theta)
    if (np.sin(angle) == 0):
      y0 = 0
      y1 = 1
    else:
      y0 = int((dist - 0 * np.cos(angle)) / np.sin(angle))
      y1 = int((dist - (cols-1) * np.cos(angle)) / np.sin(angle))

    lines.append(((y0, 0), (y1, cols-1)))
    
  return lines
