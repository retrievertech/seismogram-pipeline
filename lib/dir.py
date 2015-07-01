# http://stackoverflow.com/a/14364249/1457005

import os

def ensure_dir_exists(path):
  try: 
    os.makedirs(path)
  except OSError:
    if not os.path.isdir(path):
      raise
