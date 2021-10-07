# tinyticker

> its not the size that matters

## Installation

```
pip install tinyticker
```

to not mess with your system python, consider using [pipx](https://github.com/pypa/pipx):

```
pipx install tinyticker
```

### Dependencies

If you get the following error when installing `numpy`:

```
libf77blas.so.3: cannot open shared object file: No such file or directory
```

Install the missing library<sup>[ref](https://numpy.org/devdocs/user/troubleshooting-importerror.html#raspberry-pi)</sup>:

```
sudo apt-get install libatlas-base-dev
```

If `pillow` (PIL) complains then your missing some libraries, try:

```
sudo apt install libopenjp2-7 libtiff5
```

## TODO

- [ ] Implement stock ticking 
- [ ] Change API to one which does not require a key, maybe yahoo https://github.com/ranaroussi/yfinance
