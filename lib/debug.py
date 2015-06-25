from scipy import misc
from dir import ensure_dir_exists

class Debug:

  debug_dir = None
  active = False
  stage_count = {}

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
    filename = "%s.%s.%s.png" % (stage, count, name)
    misc.imsave(cls.debug_dir+"/"+filename, img)
