# seismogram-pipeline

## Directory structure
- `src/` the meat of the repo; image processing scripts
- `lib/` 3rd party code
- `/` command line entry points for the various scripts in `src/`

## Dependencies

The python scripts are written for Python 2.7. An easy way to install most of the dependencies is with [Anaconda](http://continuum.io/downloads).

You'll also need [geojson](https://pypi.python.org/pypi/geojson/):
```
pip install geojson
```

There may eventually be Netlogo, MATLAB, or javascript files in this repository.