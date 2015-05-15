# -*- coding: utf-8 -*-
"""
Created on Sun Nov  9 21:53:26 2014

@author: benamy
"""

import numpy as np
from math import sqrt
from numpy.random import randint

def best_candidate_sample(shape, num_samples, num_candidates = 10):
    samples = [get_candidates(shape,num_candidates)[0]]
    for i in xrange(1,num_samples):
        candidates = get_candidates(shape, num_candidates)
        best_candidate = find_best_candidate(candidates, samples)
        samples.append(best_candidate)
    return np.asarray(samples)
        
def get_candidates(shape, num_candidates):
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
    