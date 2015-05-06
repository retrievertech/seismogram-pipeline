from skimage.draw import polygon
import numpy as np
import numpy.ma as ma

def get_polygon_coordinates(polygon_feature):
  y = polygon_feature[:, 1]
  x = polygon_feature[:, 0]
  return (y, x)

def mask_image(image, polygon_feature):
  (y, x) = get_polygon_coordinates(np.array(polygon_feature))
  rr, cc = polygon(y, x)
  mask = np.ones(image.shape)
  mask[rr, cc] = 0
  return ma.masked_array(image, mask=mask)
