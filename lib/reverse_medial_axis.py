# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 17:59:00 2014

@author: benamy
"""
import numpy as np
from lib.draw import circle

def reverse_medial_axis(mat, dist):
  '''
  Returns the reverse medial axis transform.

  Parameters
  ---------------
  mat : ndarray of bools
    Medial axis transform of the image.
    True (or positive) at the medial axis.
  dist : ndarray of ints
    Distance transform of the image.
    dist should have same dimensions as mat and be positive
    where mat is True.

  Returns
  ---------
  r_mat : ndarray of bools
    The reverse medial axis transform.
  '''
  dims = mat.shape
  r_mat = np.zeros_like(mat, dtype=bool)
  mat_pixels = np.argwhere(mat)
  for p in mat_pixels:
    radius = max(dist[p[0], p[1]], 1)
    rr, cc = circle(p[0], p[1], radius, dims)
    r_mat[rr, cc] = True
  return r_mat
