import numpy as np
import matplotlib.pyplot as plt
from skimage import color

def gray2prism(gray):
  cmap = plt.get_cmap('prism')
  rgba_img = cmap(gray)
  return np.delete(rgba_img,3,2)

def color_markers(marker_image, background, marker_color=[1,0,0]):
  if background.ndim == 2:
    background = color.gray2rgb(background)
  image_color = np.ndarray(np.r_[marker_image.shape,3])
  image_color[:,:] = marker_color
  marker_image = np.dstack((marker_image, marker_image, marker_image))
  overlay = np.where(marker_image, image_color, background)
  marker_image = marker_image[:,:,0]
  return overlay

def image_overlay(img, overlay, mask = None):
  if img.ndim == 2:
    img = color.gray2rgb(img)
  if overlay.ndim == 2:
    overlay = color.gray2rgb(overlay)
  if mask.ndim == 2:
    mask = np.dstack((mask, mask, mask))
  images_combined = 0.5 * (img + overlay)
  return np.where(mask, img, images_combined)
