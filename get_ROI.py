from util.timer import timeStart, timeEnd
from util.load_image import get_image
from src.ROI_Detection import get_boundary, get_box_lines, get_roi_corners

# for testing
timeStart("DONE", immediate=False)
image = get_image("in/dummy-seismo-small.png")
boundary = get_boundary(image, debug=True)
lines = get_box_lines(boundary, debug=True)
get_roi_corners(lines, debug=True, image=image)
timeEnd("DONE", immediate=False)
