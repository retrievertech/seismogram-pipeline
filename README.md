# seismogram-pipeline

## Directory structure
- `lib/` the meat of the repo: image processing scripts and utilities
- `/` command line entry points for the various scripts in `lib/`
- `/in` sample input files

## Dependencies

The python scripts are written for Python 2.7. An easy way to install most of the dependencies is with [Anaconda](http://continuum.io/downloads).

You'll also need [geojson](https://github.com/frewsxcv/python-geojson):
```
pip install geojson
```

and [docopt](https://github.com/docopt/docopt):
```
pip install docopt==0.6.1
```

There may eventually be Netlogo, MATLAB, or javascript files in this repository.