#!/usr/bin/python

import argparse

parser = argparse.ArgumentParser(description=
  "Calculates intersections in a black and white "
  "image and saves as a geojson FeatureCollection "
  "of features with Point geometries and 'radius' properties.")
parser.add_argument("--thresh-image", required=True, help="black and white input image filename")
parser.add_argument("--output", required=True, help="output geojson filename")
args = parser.parse_args()


from src.intersection_detection import find_intersections_from_file_path

intersections = find_intersections_from_file_path(args.thresh_image)
intersections.exportAsGeoJSON(args.output)