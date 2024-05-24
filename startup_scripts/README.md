# Startup Scripts

This folder contains scripts that can be uploaded onto a Raspberry Pi running `Tinyticker` to enable extra functionality.
They will be run as the `tinyticker-web` web interface starts up.

To upload files on the Raspberry Pi, head over to [`http://tinyticker.local/startup`](http://tinyticker.local/startup) and drop the files there.

- **[`buttons_2in7.py`](buttons_2in7.py)**

  This script is for the Waveshare 2.7inch e-Paper HAT. It listens for button presses and sends the appropriate command to the `Tinyticker` server.

  - Key 1: Next ticker
  - Key 2: Previous ticker
  - Key 3: Cycle config
  - Key 4: Refresh
