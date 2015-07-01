# -*- coding: utf-8 -*-
"""
Created on Sun Nov  9 21:53:26 2014

@author: benamy
"""

import numpy as np
from math import sqrt
from numpy.random import randint, choice

def best_candidate_sample(coords, num_samples, num_candidates = 10):
  '''
  Sample points randomly from a 2-D array using Mitchell's Best Candidate 
  sampling algorithm. Produces more even coverage of an array than simply
  taking a number of uniform random samples. 
  
  Parameters
  ------------
  coords : 2-D array of ints
    A list of candidate points.
  num_samples : int
    The number of samples to take. 
  num_candidates : int, optional
    The number of candidate samples to consider per sample point. 
  
  Returns
  ---------
  samples : 2-D numpy array of ints
    The coordinates of the chosen sample points. The array has two columns
    and num_samples rows. 
  '''
  samples = [get_candidates(coords,num_candidates)[0]]
  for i in xrange(1,num_samples):
    candidates = get_candidates(coords, num_candidates)
    best_candidate = find_best_candidate(candidates, samples)
    samples.append(best_candidate)
  samples = np.asarray(samples)
  return samples

def get_candidates(coords, num_candidates):
  random_indices = choice(len(coords), num_candidates)
  candidates = coords[random_indices,:]
  return candidates

def best_candidate_sample_from_rect(shape, num_samples, num_candidates = 10):
  '''
  Sample points randomly from a 2-D array using Mitchell's Best Candidate 
  sampling algorithm. Produces more even coverage of an array than simply
  taking a number of uniform random samples. 
  
  Parameters
  ------------
  shape : numpy array or tuple of ints
    The dimensions of the image array.
  num_samples : int
    The number of samples to take. 
  num_candidates : int, optional
    The number of candidate samples to consider per sample point. 
  
  Returns
  ---------
  samples : 2-D numpy array of ints
    The coordinates of the chosen sample points. The array has two columns
    and num_samples rows. 
  '''
  samples = [get_candidates_from_rect(shape,num_candidates)[0]]
  for i in xrange(1,num_samples):
    candidates = get_candidates_from_rect(shape, num_candidates)
    best_candidate = find_best_candidate(candidates, samples)
    samples.append(best_candidate)
  samples = np.asarray(samples)
  return samples
    
def get_candidates_from_rect(shape, num_candidates):
  candidates = np.zeros((num_candidates,2),dtype=int)
  candidates[:,0] = randint(0,high=shape[0],size=num_candidates)
  candidates[:,1] = randint(0,high=shape[1],size=num_candidates)
  return candidates
  
def find_best_candidate(candidates, samples):
  best_candidate = None
  furthest_d = 0
  for candidate in candidates:
    _,dist = find_closest(candidate, samples)
    if dist > furthest_d:
      best_candidate = candidate
      furthest_d = dist
  return best_candidate

def find_closest(point, points):
  closest_p = points[0]
  closest_d = distance(point, closest_p)
  for p in points:
    d = distance(point, p)
    if d < closest_d:
      closest_p = p
      closest_d = d
  return [closest_p, closest_d]

def distance(p1, p2):
  return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
  
