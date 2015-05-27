import sys
from time import time

timeDict = {}
depth = 0
justCalledTimeStart = False

def timeStart(key):
  global depth, justCalledTimeStart

  timeDict[key] = time()
  
  printStart(key, justCalledTimeStart)

  depth += 1
  justCalledTimeStart = True

def timeEnd(key):
  global depth, justCalledTimeStart

  depth -= 1
    
  printEnd(key, justCalledTimeStart)
  del timeDict[key]

  justCalledTimeStart = False

def printStart(key, justCalledTimeStart):
  if (justCalledTimeStart is True):
    sys.stdout.write("\n")

  sys.stdout.write(getIndent() + key + " ... ")
  sys.stdout.flush()

def printEnd(key, justCalledTimeStart):
  if (justCalledTimeStart is False):
    sys.stdout.write(getIndent())

  sys.stdout.write(str(time() - timeDict[key]) + "s \n")

def getIndent():
  return ''.join(["  " for i in range(depth)])