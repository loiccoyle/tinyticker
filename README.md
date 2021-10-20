<h1 align="center">🚀 tinyticker 🚀</h5>
<h3 align="center"><img src="https://i.imgur.com/RjoIULL.png" width=500><img src="https://i.imgur.com/pZmFzAK.png" height=500 align=right></h3>
<h5 align="center">size doesn't matter</h5>
<p align="center">
  <a href="https://pypi.org/project/tinyticker/"><img src="https://img.shields.io/pypi/v/tinyticker"></a>
  <a href="./LICENSE.md"><img src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
</p>

`tinyticker` uses a Raspberry Pi zero W and a small ePaper display to periodically display stock or crypto price.

A `flask` web interface is created to set the ticker options and control the Raspberry Pi.

`tinyticker` uses the [`cryptocompare`](https://github.com/lagerfeuer/cryptocompare) API to query the crypto price information, you'll need to get yourself a free [API key](https://min-api.cryptocompare.com/pricing). As well as the [`yfinance`](https://github.com/ranaroussi/yfinance) package to get the stock financial data.

## Hardware

Shopping list:

- [Raspberry Pi Zero W](https://www.raspberrypi.com/products/raspberry-pi-zero-w/)
- [Waveshare ePaper 2.13in V2 two color](https://www.amazon.com/s?k=waveshare+epaper+2.13inch)
- A micro sd card

## Recommended setup

I highly recommend using [comitup](https://github.com/davesteele/comitup) to setup the networking on your RPi.

- Write the `comitup` [image](https://davesteele.github.io/comitup/latest/comitup-lite-img-latest.html) to your sd card
- Boot up the RPi and setup the networking
- ssh into your RPi, you'll probably want to change the password while you're at it
- Enable the [SPI interface](https://www.raspberrypi-spy.co.uk/2014/08/enabling-the-spi-interface-on-the-raspberry-pi/)
- (Optional) rename the hostname of your RPi by editing the `/etc/hostname` and `/etc/hosts` file
- (Optional) rename the Wifi AP name by editing the `/etc/comitup.conf` file
- Install `pipx`: `python3 -m pip install --user pipx`
- Install `tinyticker`: `pipx install tinyticker`
- Setup `tinyticker` to start on boot: `tinyticker --start-on-boot -vv`
  - this will write and enable two `systemd` unit files `tinyticker.service` and `tinyticker-web.service`
  - On boot, a qrcode for the `flask` app will be flashed on the display
- Leave a star, reboot and HODL !

Note: the Raspberry Pi zero isn't very fast so be patient :)

### Gotchas

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

If `lxml` complains:

```
sudo apt install libxml2-dev libxslt1-dev
```
