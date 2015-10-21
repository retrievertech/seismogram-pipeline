import numpy as np
from geojson import LineString, Feature
from utilities import linear_fit

class segment:
  '''
  A segment is a region of pixels and a center line that
  represents that region.
  
  '''

  def __init__(self, coords, values, id, ridge_line=None):
    self.region = region(coords, values)
    self.set_linear_fit()
    self.id = id
    if ridge_line is not None:
      self.add_ridge_line(ridge_line)

  # def binary_image(self):
  #   return self.region.binary_image()

  def add_ridge_line(self, pixel_coords):
    self.ridge_line = pixel_coords
    #self.set_pixel_series()
    if self.ridge_line.size > 2:
      self.set_center_line(self.ridge_line)
      self.has_center_line = True
    else:
      self.has_center_line = False

  def add_center_line_values(self, values):
    self.center_line.values = values

  def add_horizontal_ridges(self, coords):
    self.ridge_line_h = coords

  def add_vertical_ridges(self, coords):
    self.ridge_line_v = coords

  def to_geojson_feature(self):
    center_line = zip(map(int, self.center_line.x), map(int, self.center_line.y))
    return Feature(geometry=LineString(center_line), id=self.id)

  def to_json_properties(self):
    '''
    These properties are needed in combination with the
    geojson to reconstruct complete segment objects. This is
    useful for debugging and for more advanced segment assignment.
    
    We store the properties separately from the geojson because
    the client only needs the geojson for rendering; it shouldn't
    have to download all the extra property cruft from the server.

    '''
    region_coords = zip(map(int, self.region.ii), map(int, self.region.jj))
    properties = {
      "values": self.region.values.tolist(),
      "coords": region_coords
    }
    return properties

  # def set_pixel_series(self):
  #   self.pixel_series = ridge_line_to_series(self.ridge_line)
  #   #self.set_center_line()

  # def plot_ridge_line(self):
  #   scatter(self.ridge_line[:,1], (-self.ridge_line[:,0]))

  # def plot_pixel_series(self):
  #   scatter(self.pixel_series[:,1], (-self.pixel_series[:,0]))

  def set_linear_fit(self):
    self.linear_fit = linear_fit(self.region.coords)

  def set_center_line(self, series):
    self.center_line = series_to_center_line(series)

  # def plot_center_line(self):
  #   plt.plot(self.center_line[:,1], (-self.center_line[:,0]), '-')

class region:
  '''
  The coordinates of a collection of pixels.
  
  '''
  region_domain = np.array([0,0], dtype=int)
  region_range = np.array([0,0], dtype=int)

  # def __init__(self, pixel_coords, image_shape, region_ID=0):
  #   self.coords = pixel_coords
  #   self.ii = self.coords[:,0]
  #   self.jj = self.coords[:,1]
  #   self.dims = image_shape
  #   self.ID = region_ID
  #   self.calc_properties()
  #   self.create_binary()

  def __init__(self, coords, values):
    self.coords = coords
    self.values = values
    self.ii = self.coords[:,0]
    self.jj = self.coords[:,1]
    self.calc_properties()
    self.create_binary()

  def calc_properties(self):
    # calculate domain, range, upper-left corner,
    # centroid, width, height, and size (i.e. number of pixels in region)
    self.region_domain[0] = np.amin(self.jj)
    self.region_domain[1] = np.amax(self.jj)
    self.region_range[0] = np.amin(self.ii)
    self.region_range[1] = np.amax(self.ii)
    self.ul_corner = np.array([self.region_range[0], self.region_domain[0]], dtype=int)
    self.centroid = np.mean(self.coords, axis=0)
    self.size = self.coords.shape[0]
    self.height = self.region_range[1] - self.region_range[0] + 1
    self.width = self.region_domain[1] - self.region_domain[0] + 1

  def add_pixels(self, pixel_coords):
    pixel_list = list(self.coords)
    pixel_list = pixel_list + list(pixel_coords)
    pixel_list = map(tuple, pixel_list)
    pixel_list = list(set(pixel_list)) # remove duplicates
    pixel_list = np.asarray(tuple(pixel_list), dtype=int)
    self.coords = pixel_list
    self.calc_properties()

  def remove_pixels(self, pixel_coords):
    curr_pixels = set(map(tuple, list(self.coords)))
    pixels_to_remove = set(map(tuple, list(pixel_coords)))
    new_pixel_list = curr_pixels - pixels_to_remove
    new_pixel_list = np.asarray(tuple(new_pixel_list), dtype=int)
    self.coords = new_pixel_list
    self.calc_properties()

  def create_binary(self):
    # create two boolean arrays, one representing the region itself,
    # the other representing everything else in the bounding box that
    # contains the region
    ii_offset = self.ii - self.ul_corner[0]
    jj_offset = self.jj - self.ul_corner[1]
    self.binary = np.zeros((self.height, self.width), dtype=bool)
    self.binary[ii_offset, jj_offset] = True
    self.mask = (~self.binary)

  # def binary_image(self):
  #   img = np.zeros(self.dims, dtype=bool)
  #   img[self.coords[:,0], self.coords[:,1]] = True
  #   #for p in self.coords:
  #   #    img[p[0], p[1]] = True
  #   return img

  def is_in_region(self, pixel_coords):
    matches = np.logical_and(self.coords[:,0] == pixel_coords[0],
                 self.coords[:,1] == pixel_coords[1])
    return np.any(matches)

  def pixel_row(self, row):
    return self.coords[(self.ii == row),:]

  def pixel_column(self, col):
    return self.coords[(self.jj == col),:]

'''
Turning off splining for now
'''
def series_to_center_line(series):
  return center_line(series)

class center_line:
  def __init__(self, series):
    self.coords = series
    self.x = series[:,1]
    self.y = series[:,0]
