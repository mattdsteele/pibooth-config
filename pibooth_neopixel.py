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
        rainbow_cycle(0.001, pixels)
    print("Stopping")
    app.pixels.fill((0,0,0))

def rainbow_cycle(wait, pixels):
    LOGGER.info("running rainbow cycle")
    for j in range(255):
        for i in range(num_pixels):
            pixel_index = (i * 256 // num_pixels) + j
            pixels[i] = wheel(pixel_index & 255)
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
    # rainbow_cycle(0.001, app.pixels)

def state_wait_do(app):
    LOGGER.info("wait do")
    # rainbow_cycle(0.001, app.pixels)

@pibooth.hookimpl
def state_wait_exit(app):
    LOGGER.info("Stopping rainbow process")
    app.neopixels_proc.do_run = False
    # app.neopixels_proc.terminate();

@pibooth.hookimpl
def state_choose_enter(app):
    app.pixels.fill((0,0,0))
    app.pixels.show()

@pibooth.hookimpl
def state_preview_enter(app):
    app.pixels.fill((0,255,0))
    app.pixels.show()
    LOGGER.info("In preview enter")

@pibooth.hookimpl
def state_preview_exit(app):
    app.pixels.fill((255,255,0))
    app.pixels.show()
    LOGGER.info("In preview exit")


@pibooth.hookimpl
def state_capture_exit(app):
    app.pixels.fill((0,0,0))
    app.pixels.show()
    LOGGER.info("In capture exit")
