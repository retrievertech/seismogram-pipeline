# from http://stackoverflow.com/questions/3252194/numpy-and-line-intersections
#
# line segment intersection using vectors
# see Computer Graphics by F.S. Hill
#
from numpy import dot, empty_like

def perp(a):
  b = empty_like(a)
  b[0] = -a[1]
  b[1] = a[0]
  return b

# seg_intersect returns the intersection (if any) of the infinite lines
# defined by segments seg1 and seg2

# seg1 and seg2 are each of the form [[x1, y1], [x2, y2]]

# TODO: handle divide by 0 case for parallel lines (check if denom is 0 before dividing)

def seg_intersect(seg1, seg2):
  a1, a2, b1, b2 = seg1[0], seg1[1], seg2[0], seg2[1]
  da = a2-a1
  db = b2-b1
  dp = a1-b1
  dap = perp(da)
  denom = dot(dap, db)
  num = dot(dap, dp)
  return (num / denom.astype(float))*db + b1