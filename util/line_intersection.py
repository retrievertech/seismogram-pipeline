# from http://stackoverflow.com/questions/3252194/numpy-and-line-intersections
#
# line segment intersection using vectors
# see Computer Graphics by F.S. Hill
#
from numpy import dot, empty_like

def perp( a ) :
  b = empty_like(a)
  b[0] = -a[1]
  b[1] = a[0]
  return b

# line segment a given by endpoints a1, a2
# line segment b given by endpoints b1, b2
def seg_intersect(a1,a2, b1,b2) :
  da = a2-a1
  db = b2-b1
  dp = a1-b1
  dap = perp(da)
  denom = dot(dap, db)
  num = dot(dap, dp)
  return (num / denom.astype(float))*db + b1