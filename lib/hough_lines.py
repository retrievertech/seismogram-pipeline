from debug import Debug
from stats_recorder import Record

import numpy as np
from skimage.transform import hough_line, hough_line_peaks
from utilities import normalize

def get_best_hough_lines(image, min_angle, max_angle, min_separation_distance,
                         min_separation_angle):

  angles = np.deg2rad(np.arange(min_angle, max_angle, 0.5))
  hough, angles, distances = hough_line(image, angles)

  peak_hough, peak_angles, peak_distances = \
    hough_line_peaks(hough, angles, distances,
                     num_peaks=150,
                     threshold=0.2*np.amax(hough),
                     min_distance=min_separation_distance,
                     min_angle=min_separation_angle)
  
  best_hough_idx = np.argmax(peak_hough)
  line = get_line_endpoints_in_image(image, peak_angles[best_hough_idx],
                                     peak_distances[best_hough_idx])
  return line

def get_all_hough_lines(image, min_angle, max_angle, min_separation_distance,
                        min_separation_angle):

  angles = np.deg2rad(np.arange(min_angle, max_angle, 0.5))
  hough, angles, distances = hough_line(image, angles)
  
  Debug.save_image("hough", "accumulator", normalize(hough))

  _, peak_angles, peak_distances = \
    hough_line_peaks(hough, angles, distances,
                     num_peaks=150,
                     threshold=0.2*np.amax(hough),
                     min_distance=min_separation_distance,
                     min_angle=min_separation_angle)

  lines = [get_line_endpoints_in_image(image, angle, radius)
    for angle, radius in zip(peak_angles, peak_distances)]

  if Debug.active:
    peak_angle_idxs = [ np.where(angles == angle)[0][0] for angle in peak_angles ]
    peak_rho_idxs = [ np.where(distances == distance)[0][0] for distance in peak_distances ]
    peak_coords = zip(peak_rho_idxs, peak_angle_idxs)
    peaks = np.zeros(hough.shape)
    for coord in peak_coords:
      peaks[coord] = 1
    Debug.save_image("hough", "accumulator_peaks", peaks)

  if Record.active:
    # Thought get_max_theta_idx might be a useful way to filter
    # real meanlines from spurious meanlines, but it's not
    # reliable when the image is saturated with incorrect
    # meanlines. Filtering lines based on the ROI angle
    # was more effective.

    # max_theta_idx = get_max_theta_idx(hough)
    # Record.record("theta_mode", angles[max_theta_idx])


  return lines

def bin_hough(hough, rho_bin_size):
  binned_hough = np.zeros([int(hough.shape[0]/rho_bin_size), hough.shape[1]])
  for rho in range(0, binned_hough.shape[0]):
    slice_start = rho*rho_bin_size
    slice_end = slice_start+rho_bin_size
    binned_hough[rho, :] = np.sum(hough[slice_start:slice_end, :], axis=0)
  return binned_hough

def get_max_theta_idx(hough):
  '''
  Returns the column (theta) of the hough transform with the
  most above-threshold bins.

  '''
  thresh_hough = threshold_hough(hough, 0.2*np.amax(hough))
  Debug.save_image("hough", "thresholded_accumulator", normalize(thresh_hough))
  # find the column with the most above-threshold bins
  sum_thresh_hough = np.sum(thresh_hough, axis=0)
  max_theta_idx = np.argmax(sum_thresh_hough)
  return max_theta_idx

def threshold_hough(hough, threshold):
  thresh_hough = np.copy(hough)
  thresh_hough[hough < threshold] = 0
  thresh_hough[hough >= threshold] = 1
  return thresh_hough

'''
Tried doing some fancier stuff with the hough accumulator matrix here, but it didn't work out.

'''
# from scipy.ndimage.filters import gaussian_filter1d
# from scipy.signal import argrelextrema

# def get_hough_meanlines(image, min_angle, max_angle, min_separation_distance, min_separation_angle):
#   angles = np.deg2rad(np.arange(min_angle, max_angle, 0.5))
#   hough, angles, distances = hough_line(image, angles)

#   rho_bin_size = min_separation_distance
#   binned_hough = np.zeros([int(hough.shape[0]/rho_bin_size), hough.shape[1]])
  
#   def bin_idx_to_idx(bin_idx):
#     return int(bin_idx*rho_bin_size + rho_bin_size/2)

#   def bin_idx_to_rho(bin_idx):
#     return distances[bin_idx_to_idx(bin_idx)]

#   for rho in range(0, binned_hough.shape[0]):
#     slice_start = rho*rho_bin_size
#     slice_end = slice_start+rho_bin_size
#     binned_hough[rho, :] = np.sum(hough[slice_start:slice_end, :], axis=0)

#   Debug.save_image("hough", "accumulator", normalize(hough))
#   Debug.save_image("hough", "binned_accumulator", normalize(binned_hough))

#   # threshold the accumulator
#   thresh_binned_hough = np.copy(binned_hough)
#   binned_threshold = 0.3*np.amax(binned_hough)
#   thresh_binned_hough[binned_hough < binned_threshold] = 0
#   thresh_binned_hough[binned_hough >= binned_threshold] = 1

#   # find the column with the most above-threshold bins
#   sum_thresh_binned_hough = np.sum(thresh_binned_hough, axis=0)
#   theta_max_idx = np.argmax(sum_thresh_binned_hough)

#   extrema = argrelextrema(binned_hough[:, theta_max_idx], np.greater)
#   print "extrema: %s" % extrema[0]
#   print "num extrema: %s" % len(extrema[0])

#   peak_angles = angles[theta_max_idx] * np.ones(len(extrema[0]))
#   peak_distances = [bin_idx_to_rho(bin_idx) for bin_idx in extrema[0]]
#   # peak_distances = [distances[bin_idx] for bin_idx in extrema[0]]

#   return [ get_line_endpoints_in_image(image, angle, radius) for angle, radius in zip(peak_angles, peak_distances)]

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
