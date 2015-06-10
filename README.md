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

## Use

All the scripts in the `/` directory are runnable from a command line like so:
```
python name_of_script.py
```

Running a script with no arguments (like in the above example) will output a usage message that explains what arguments are required and what arguments are optional. For example, running `python get_all_metadata.py` outputs:

```
Usage:
  pipeline.py --image <filename> --output <directory> [--scale <scale>] [--debug <directory>]
  pipeline.py -h | --help
```

Arguments in `[square brackets]` are optional, whereas unbracketed arguments are required.

`python get_all_metadata.py -h` or `--help` outputs a more detailed help message:

```
Usage:
  pipeline.py --image <filename> --output <directory> [--scale <scale>] [--debug <directory>]
  pipeline.py -h | --help

Options:
  -h --help             Show this screen.
  --image <filename>    Filename of seismogram.
  --output <directory>  Save metadata in <directory>.
  --scale <scale>       1 for a full-size seismogram, 0.25 for quarter-size, etc. [default: 1]
  --debug <directory>   Save intermediate steps as images for inspection in <directory>.
```

The repository comes with a sample quarter-size seismogram in the `in/` directory. The command to generate all metadata for this image would be:

```
python get_all_metadata.py --image in/dummy-seismo-small.png --output some-directory --scale 0.25
```

And if you want to see images of the intermediate processing steps, use the `--debug` argument: `--debug some-debug-directory`.