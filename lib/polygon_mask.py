from skimage.draw import polygon
import numpy as np

def get_polygon_coordinates(polygon_feature):
  y = polygon_feature[:, 0]
  x = polygon_feature[:, 1]
  return (y, x)

def mask_image(image, polygon_feature):
  (y, x) = get_polygon_coordinates(np.array(polygon_feature))
  rr, cc = polygon(y, x)
  mask = np.zeros(image.shape)
  mask[rr, cc] = 1
  return mask * image