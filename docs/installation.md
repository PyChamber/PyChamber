# Installation

## Stable release

The most recent release is currently available as a .exe file. I'm working on
adding OSX support.

You can also install the .whl file by downloading it from releases and running:

```console
pip install pychamber-<version>-py3-none-any.whl
```

**NOTE:** You currently must have git installed to install the .whl file

## From source

The source for PyChamber can be downloaded from
the [Github repo](https://github.com/pychamber/pychamber/).

You can either clone the public repository:

``` console
git clone git://github.com/pychamber/pychamber
```

Or download the tarball:

``` console
curl -OJL https://github.com/pychamber/pychamber/tarball/master
```

Once you have a copy of the source, you can install it using [poetry](https://python-poetry.org/docs/1.2/):

``` console
poetry install
```
