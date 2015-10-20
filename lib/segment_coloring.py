import numpy as np
import matplotlib.pyplot as plt
from skimage import color

def gray2prism(gray):
  cmap = plt.get_cmap('prism')
  # convert to prism colors and remove alpha channel
  rgb_img = cmap(gray)[:, :, :-1]
  return rgb_img

def image_overlay(img, overlay, mask = None):
  if img.ndim == 2:
    img = color.gray2rgb(img)
  if overlay.ndim == 2:
    overlay = color.gray2rgb(overlay)
  if mask.ndim == 2:
    mask = np.dstack((mask, mask, mask))
  images_combined = 0.5 * (img + overlay)
  return np.where(mask, img, images_combined)
