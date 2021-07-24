"""Plugin to manage the RGB lights via GPIO."""

import pibooth
import board
import neopixel
import time
import threading
from pibooth.utils import LOGGER

__version__ = "0.0.1"
num_pixels = 48
pixel_pin = board.D18
ORDER = neopixel.GRB

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b) if ORDER in (neopixel.RGB, neopixel.GRB) else (r, g, b, 0)


def thread_cycle(pixels):
    t = threading.currentThread()
    LOGGER.info("Got to thread cycle")
    LOGGER.info(pixels)
    while getattr(t, "do_run", True):
        rainbow_cycle(0.001, pixels, t)
    print("Stopping")
    pixels.fill((0,0,0))
    pixels.show()

def countdown(time_seconds, pixels):
    raw_time_between_pixels = time_seconds / num_pixels
    time_between_pixels = raw_time_between_pixels * 0.95

    pixels.fill((0, 255, 0))
    pixels.show()
    for i in range(0, num_pixels):
        pixels[num_pixels - i - 1] = (0, 0, 0)
        pixels.show()
        time.sleep(time_between_pixels)

def rainbow_cycle(wait, pixels, t):
    # LOGGER.info("running rainbow cycle")
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
        if getattr(t, "do_run", False):
            LOGGER.info("stopping rainbow cycle")
            return
        else:
            pixels.show()
            time.sleep(wait)


@pibooth.hookimpl
def pibooth_startup(app):
    LOGGER.info("Starting up")
    pixels = neopixel.NeoPixel(
        pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=ORDER
    )
    app.pixels = pixels

@pibooth.hookimpl
def state_wait_enter(app):
    LOGGER.info("Starting proc")
    proc = threading.Thread(target=thread_cycle, args=[app.pixels])
    proc.daemon = True
    proc.start()
    app.neopixels_proc = proc;

def state_wait_do(app):
    LOGGER.info("wait do")

@pibooth.hookimpl
def state_wait_exit(app):
    LOGGER.info("Stopping rainbow process")
    app.neopixels_proc.do_run = False
    LOGGER.info("Stopped rainbow process")

@pibooth.hookimpl
def state_choose_enter(app):
    LOGGER.info("choosing enter")
    app.pixels.fill((0,0,0))
    app.pixels.show()

@pibooth.hookimpl
def state_preview_enter(app):
    app.pixels.fill((0,0,0))
    app.pixels.show()

    proc = threading.Thread(target=countdown, args=[3, app.pixels])
    proc.daemon = True
    proc.start()
    app.neopixels_proc = proc;
    LOGGER.info("In preview enter")

@pibooth.hookimpl
def state_preview_exit(app):
    app.neopixels_proc.do_run = False
    app.pixels.fill((255,255,255))
    app.pixels.show()
    LOGGER.info("In preview exit")


@pibooth.hookimpl
def state_capture_exit(app):
    app.pixels.fill((0,0,0))
    app.pixels.show()
    LOGGER.info("In capture exit")
