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
  coords_in_mask = (rr >= 0) & (rr < image.shape[0]) & (cc >= 0) & (cc < image.shape[1])
  mask[rr[coords_in_mask], cc[coords_in_mask]] = 0
  return ma.masked_array(image, mask=mask)
