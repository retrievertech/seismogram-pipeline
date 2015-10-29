import sys
from time import time

timeDict = {}
depth = 0

# keep track of whether timers are being nested
timer_open = False

def timeStart(key):
  global depth, timer_open

  timeDict[key] = time()

  printStart(key, timer_open)

  depth += 1
  timer_open = True

def timeEnd(key):
  global depth, timer_open

  depth -= 1

  time_elapsed = time() - timeDict[key]
  del timeDict[key]
  
  printEnd(key, time_elapsed, timer_open)

  timer_open = False

  return time_elapsed

def printStart(key, timer_open):
  if (timer_open is True):
    sys.stdout.write("\n")

  sys.stdout.write(getIndent() + key + " ... ")
  sys.stdout.flush()

def printEnd(key, time_elapsed, timer_open):
  if (timer_open is False):
    sys.stdout.write(getIndent())

  sys.stdout.write(str(time_elapsed) + "s \n")

def getIndent():
  return ''.join(["  " for i in range(depth)])
