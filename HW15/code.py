# requires adafruit_ov7670.mpy and adafruit_st7735r.mpy in the lib folder
import time
from displayio import (
    Bitmap,
    Group,
    TileGrid,
    FourWire,
    release_displays,
    ColorConverter,
    Colorspace,
)
from adafruit_st7735r import ST7735R
import board
import busio
import digitalio
from adafruit_ov7670 import (
    OV7670,
    OV7670_SIZE_DIV1,
    OV7670_SIZE_DIV8,
    OV7670_SIZE_DIV16,
)
from ulab import numpy as np

release_displays()
spi = busio.SPI(clock=board.GP2, MOSI=board.GP3)
display_bus = FourWire(spi, command=board.GP0, chip_select=board.GP1, reset=None)
display = ST7735R(display_bus, width=160, height=128, rotation=90)


# Ensure the camera is shut down, so that it releases the SDA/SCL lines,
# then create the configuration I2C bus

with digitalio.DigitalInOut(board.GP10) as reset:
    reset.switch_to_output(False)
    time.sleep(0.001)
    bus = busio.I2C(board.GP9, board.GP8) #GP9 is SCL, GP8 is SDA

# Set up the camera (you must customize this for your board!)
cam = OV7670(
    bus,
    data_pins=[
        board.GP12,
        board.GP13,
        board.GP14,
        board.GP15,
        board.GP16,
        board.GP17,
        board.GP18,
        board.GP19,
    ],  # [16]     [org] etc
    clock=board.GP11,  # [15]     [blk]
    vsync=board.GP7,  # [10]     [brn]
    href=board.GP21,  # [27/o14] [red]
    mclk=board.GP20,  # [16/o15]
    shutdown=None,
    reset=board.GP10,
)  # [14]

width = display.width
height = display.height

bitmap = None
# Select the biggest size for which we can allocate a bitmap successfully, and
# which is not bigger than the display
for size in range(OV7670_SIZE_DIV1, OV7670_SIZE_DIV16 + 1):
    #cam.size = size # for 4Hz
    #cam.size = OV7670_SIZE_DIV16 # for 30x40, 9Hz
    cam.size = OV7670_SIZE_DIV8 # for 60x80, 9Hz
    if cam.width > width:
        continue
    if cam.height > height:
        continue
    try:
        bitmap = Bitmap(cam.width, cam.height, 65536)
        break
    except MemoryError:
        continue

print(width, height, cam.width, cam.height)
if bitmap is None:
    raise SystemExit("Could not allocate a bitmap")
time.sleep(4)
g = Group(scale=1, x=(width - cam.width) // 2, y=(height - cam.height) // 2)
tg = TileGrid(
    bitmap, pixel_shader=ColorConverter(input_colorspace=Colorspace.BGR565_SWAPPED)
)
g.append(tg)
display.show(g)

#t0 = time.monotonic_ns()
display.auto_refresh = False

reds = np.zeros(cam.height,dtype=np.uint16)
greens = np.zeros(cam.height,dtype=np.uint16)
blues = np.zeros(cam.height,dtype=np.uint16)
bright = np.zeros(cam.height)

def _r(pixel):
    return ((pixel >> 5)&0x3F)/0x3F*100
def _g(pixel):
    return ((pixel)&0x1F)/0x1F*100
def _b(pixel):
    return (pixel >> 11)/0x1F*100
def _brightness(pixel):
    return _b(pixel) + _r(pixel) + _g(pixel)
def color_from_pixel(pixel):
    return np.array((
        _r(pixel),
        _g(pixel),
        _b(pixel),
        _brightness(pixel)
        ))
def rgb_to_grayscale(r,g,b):
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

class LineDetector:
    THRESHOLD = 50

    def __init__(self, row):
        self.row = row
        self.COM = 0

    def update(self, bitmap):
        # DEBUG - convert image to grayscale
        """
        for i in range(cam.width):
            for j in range(cam.height):
                r, g, b, bright = color_from_pixel(bitmap[i, j])
                gray = int(rgb_to_grayscale(r,g,b))

                if gray > self.THRESHOLD:
                    gray = 0xFF
                else:
                    gray = 0

                bitmap[i, j] = int(gray) & 0x1F
        """

        # Line detection at given row
        grayscale = []
        for i in range(cam.height):
            r, g, b, bright = color_from_pixel(bitmap[self.row, i])

            # Apply threshold
            gray = rgb_to_grayscale(r,g,b)
            if gray > self.THRESHOLD:
                gray = 0xFF
            else:
                gray = 0
            grayscale.append(gray)

        # Compute COM
        COM = 0
        for i, pixel in enumerate(grayscale):
            COM += i * pixel
        COM /= sum(grayscale)
        self.COM = COM

        # Draw red dot at COM
        bitmap[self.row, int(COM)] = 0x3F<<5

    def print_value(self):
        print((self.COM,))

detector = LineDetector(40)

while True:
    cam.capture(bitmap)

    # Process image
    detector.update(bitmap)
    detector.print_value()

    # Refresh
    bitmap.dirty()
    display.refresh(minimum_frames_per_second=0)
    #t1 = time.monotonic_ns()
    #print("fps", 1e9 / (t1 - t0))
    #t0 = t1
