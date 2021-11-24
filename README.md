<h1 align="center">🚀 tinyticker 🚀</h5>
<h3 align="center"><img src="https://i.imgur.com/2mF86LQ.png" width=500><img src="https://i.imgur.com/BPiGmxo.png" height=600 align=right></h3>
<h5 align="center">size doesn't matter</h5>
<p align="center">
  <a href="https://pypi.org/project/tinyticker/"><img src="https://img.shields.io/pypi/v/tinyticker"></a>
  <a href="./LICENSE.md"><img src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
</p>

`tinyticker` uses a Raspberry Pi zero W and a small ePaper display to periodically display a stock or crypto chart.

A `flask` web interface is created to set the ticker options and control the Raspberry Pi.

`tinyticker` uses the [`cryptocompare`](https://github.com/lagerfeuer/cryptocompare) API to query the crypto price information, you'll need to get yourself a free [API key](https://min-api.cryptocompare.com/pricing). As well as the [`yfinance`](https://github.com/ranaroussi/yfinance) package to get the stock financial data.

## Hardware

Shopping list:

- [Raspberry Pi Zero WH](https://www.adafruit.com/product/3708)
- One of these ePaper displays:
  - [Waveshare ePaper 2.13in Black & White](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT)
  - [Waveshare ePaper 2.13in Black, White & Red](<https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT_(B)>)
  - [Waveshare ePaper 2.13in Black, White & Yellow](<https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT_(C)>)
- A micro sd card

## Recommended setup

I highly recommend using [comitup](https://github.com/davesteele/comitup) to setup the networking on your RPi.

- Write the `comitup` [image](https://davesteele.github.io/comitup/latest/comitup-lite-img-latest.html) to your sd card
- Boot up the RPi and setup the networking
- ssh into your RPi, you'll probably want to change the password while you're at it
- Enable the [SPI interface](https://www.raspberrypi-spy.co.uk/2014/08/enabling-the-spi-interface-on-the-raspberry-pi/)
- (Optional) rename the hostname of your RPi by editing the `/etc/hostname` and `/etc/hosts` file
- (Optional) rename the Wifi AP name by editing the `/etc/comitup.conf` file
- Install the `BCM2835` driver:
  ```sh
  curl http://www.airspayce.com/mikem/bcm2835/bcm2835-1.60.tar.gz | tar xzv
  cd bcm2835-1.60/
  ./configure
  make
  make install
  ```
- Install `pipx` depdencies:
  ```sh
  sudo apt install python3-pip python3-venv
  ```
- Install `pipx`:
  ```sh
  python3 -m pip install --user pipx
  ```
- Install dependency requirements:
  ```sh
  sudo apt install libatlas-base-dev libopenjp2-7 libtiff5 libxml2-dev libxslt1-dev
  ```
- Install `tinyticker` (the `CFLAGS` variable is required for `RPi.GPIO` to install):
  ```sh
  FCLAGS=-fcommon pipx install tinyticker
  ```
- Setup `tinyticker` to start on boot:
  ```sh
  tinyticker --start-on-boot -vv
  ```
  - This will write and enable 3 `systemd` unit files `tinyticker.service`, `tinyticker-qrcode.service` and `tinyticker-web.service`.
  - On boot, a qrcode linking to the `flask` app will be flashed on the display
- Leave a star, reboot and HODL !

Note: the Raspberry Pi zero isn't very fast so be patient :)
