#!/bin/env python
# This script listens for button presses on the 2.7" e-Paper HAT.
# The buttons are on pins 5, 6, 13 and 19.

import shutil
import signal

from gpiozero import Button

from tinyticker.paths import CONFIG_DIR, CONFIG_FILE
from tinyticker.web.command import next_ticker, previous_ticker, refresh

btn1 = Button(5)
btn2 = Button(6)
btn3 = Button(13)
btn4 = Button(19)


def cycle_config():
    other_config = CONFIG_DIR / (CONFIG_FILE.name + ".next")
    if not other_config.exists():
        shutil.copy(CONFIG_FILE, other_config)

    tmp_config = CONFIG_DIR / (CONFIG_FILE.name + ".tmp")

    # config -> config.tmp
    shutil.copyfile(CONFIG_FILE, tmp_config)
    # config.next -> config
    shutil.copyfile(other_config, CONFIG_FILE)
    # config.tmp -> config.next
    shutil.move(tmp_config, other_config)


btn1.when_pressed = next_ticker
btn2.when_pressed = previous_ticker
btn3.when_pressed = cycle_config
btn4.when_pressed = refresh

while True:
    signal.pause()
