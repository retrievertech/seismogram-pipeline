import sys
from time import time

timeDict = {}
def timeStart(key, immediate=True):
  timeDict[key] = time()
  if immediate:
    printStart(key)

def timeEnd(key, immediate=True):
  if not immediate:
    printStart(key)
  printEnd(key)
  del timeDict[key]

def printStart(key):
  sys.stdout.write(key+" ... ")
  sys.stdout.flush()

def printEnd(key):
  sys.stdout.write(str(time() - timeDict[key])[:6]+"s \n")