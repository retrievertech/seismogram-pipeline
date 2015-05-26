import sys
from time import time

timeDict = {}
depth = 0
nested = False

def timeStart(key, immediate=True):
  global depth, nested

  timeDict[key] = time()
  if immediate:
    printStart(key, nested)

  depth += 1
  nested = True

def timeEnd(key, immediate=True):
  global depth, nested

  if not immediate:
    printStart(key)
  printEnd(key)
  del timeDict[key]

  depth -= 1
  nested = False

def printStart(key, nested):
  indent = getIndent()
  if (nested is True):
    sys.stdout.write("\n")
  sys.stdout.write(indent+key+" ... ")
  sys.stdout.flush()

def printEnd(key):
  sys.stdout.write(str(time() - timeDict[key]) + "s \n")

def getIndent():
  return ''.join(["  " for i in range(depth)])