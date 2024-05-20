<h1 align="center">🚀 tinyticker 🚀</h1>
<div align="center">
  <img  src="https://i.imgur.com/J4k3PCM.png" height=400>
  <img src="https://i.imgur.com/QWP7bpH.png" height=400>
</div>
<p align="center">
  <a href="https://pypi.org/project/tinyticker/"><img src="https://img.shields.io/pypi/v/tinyticker"></a>
  <a href="./LICENSE.md"><img src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
  <a href="https://github.com/loiccoyle/tinyticker/actions/workflows/ci.yml"><img src="https://github.com/loiccoyle/tinyticker/actions/workflows/ci.yml/badge.svg"></a>
</p>
<hr/>

`tinyticker` uses a Raspberry Pi zero W and a small ePaper display to periodically display a stock or crypto chart.

A `flask` web interface is created to set the ticker options and control the Raspberry Pi.

`tinyticker` uses the [`cryptocompare`](https://github.com/lagerfeuer/cryptocompare) API to query the crypto price information, you'll need to get yourself a free [API key](https://min-api.cryptocompare.com/pricing). As well as the [`yfinance`](https://github.com/ranaroussi/yfinance) package to get the stock financial data.

## 🛒 Hardware

Shopping list:

- [Raspberry Pi Zero WH](https://www.adafruit.com/product/3708)
- One of these ePaper displays:
  - [Waveshare ePaper 2.13in Black & White](https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT)
  - [Waveshare ePaper 2.13in Black, White & Red](<https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT_(B)>)
  - [Waveshare ePaper 2.13in Black, White & Yellow](<https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT_(C)>)
- A micro sd card

## 📦 Installation

### Recommended setup

Flash the [tinyticker image](https://drive.google.com/drive/folders/1U-PGzkOtSynN6FGDq2MsXF9kXGdkzd0D) onto a SD card and you should be good to go.

> [!NOTE]
> To build your own image, see the [`pi-gen`](https://github.com/loiccoyle/pi-gen) repo.

### Manual setup

> [!NOTE]
> This is much more involved than the recommended setup and will most likely require some debugging.

 <details>
  <summary>Expand</summary>

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

  - Install `pip`:

  ```sh
  sudo apt install python3-pip
  ```

  - Install dependency requirements:

  ```sh
  sudo apt install libxml2-dev libxslt1-dev libatlas-base-dev ninja-build patchelf libopenjp2-7 libtiff-dev libjpeg-dev
  ```

  - Install `tinyticker`:

  ```sh
  pip install tinyticker
  ```

  - To setup `tinyticker` to start on boot, copy over the [`systemd` unit files](./systemd) and enable them.
  - On boot, a qrcode linking to the `flask` app will be flashed on the display
  - Leave a star, reboot and HODL !

</details>

## 👢 First boot

On first boot, you will need to connect your RPi to your wifi network.

- Connect to the `tinyticker` wifi AP
- Select the wifi network you want your RPi to connect to
- Enter the wifi password

Your RPi will now connect to your wifi and the `tinyticker` services will start.

Once the web app is running, head over to `http://tinyticker.local` to configure it.

> The RPi zero isn't very fast, so be patient :)
