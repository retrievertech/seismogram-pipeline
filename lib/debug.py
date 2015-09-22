from scipy import misc
from dir import ensure_dir_exists
from numpy.random import RandomState

def pad(number):
  numstr = str(number)
  return "0" + numstr if number < 10 else numstr

class Debug:

  debug_dir = None
  active = False
  global_count = 0
  stage_count = {}
  random = RandomState()

  @classmethod
  def set_directory(cls, debug_dir):
    cls.debug_dir = debug_dir

    if debug_dir is None:
      cls.active = False
    else:
      ensure_dir_exists(debug_dir)
      cls.active = True

  @classmethod
  def save_image(cls, stage, name, img):
    if not cls.active:
      return

    count = cls.stage_count[stage] = cls.stage_count.get(stage, -1) + 1
    filename = "%s.%s.%s.%s.png" % (pad(cls.global_count), stage, pad(count), name)
    misc.imsave(cls.debug_dir+"/"+filename, img)
    cls.global_count = cls.global_count + 1

  @classmethod
  def set_seed(cls, seed):
    cls.random.seed(seed)