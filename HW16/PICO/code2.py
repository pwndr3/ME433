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

def send_arr(arr):
    for x in arr:
        print(x)
    print("END")

class LineDetector:
    PERC_HIGH = 0.75
    PERC_LOW = 0.25
    RB_RATIO = 2.0

    def __init__(self, row):
        self.row = row
        self.COM = 0

    def _get_COM(self, bitmap, row):
        # 1) Acquire red and blue line
        reds = []
        blues = []
        for i in range(cam.height):
            r, g, b, bright = color_from_pixel(bitmap[row, i])
            reds.append(r)
            blues.append(b)
        reds = np.array(reds)
        blues = np.array(blues)

        """for i in reds:
            print(i)
        print("END")"""

        # 2) Average
        filter = np.array([1, 2, 1]) / 4.0
        reds = np.convolve(reds, filter)
        blues = np.convolve(blues, filter)

        # 3) Normalize around average then cumsum
        reds = (reds - np.mean(reds))/np.std(reds)
        blues = (blues - np.mean(blues))/np.std(blues)

        def cumsum(arr):
            res = []
            s = 0
            for el in arr:
                s += el
                res.append(s)
            return np.array(res)

        reds = cumsum(reds)
        blues = cumsum(blues)

        reds -= np.min(reds)
        blues -= np.min(blues)

        #input()
        #for i in reds:
        #    print(i)
        #print("END")

        # 4) Find COM
        def value(arr, perc):
            ptp = np.max(arr) - np.min(arr)
            return np.min(arr) + perc * ptp

        def COM(arr, idxs):
            COM = 0
            s = 0
            for i, idx in enumerate(idxs):
                COM += i * arr[idx]
                s += arr[idx]

            if s == 0:
                return cam.height//2

            COM /= s
            return idxs[int(COM)]

        def COM_high(arr):
            idxs = []
            for i, r in enumerate(arr):
                if r > self.PERC_HIGH:
                    idxs.append(i)

            return COM(arr, idxs)
        def COM_low(arr):
            idxs = []
            for i, r in enumerate(arr):
                if r < self.PERC_LOW:
                    idxs.append(i)

            return COM(arr, idxs)

        COM_high_r = COM_high(reds)
        COM_high_b = COM_high(blues)

        COM_low_r = COM_low(reds)
        COM_low_b = COM_low(blues)

        COM = 0
        error = len(reds)

        for COM_r in [COM_high_r, COM_low_r]:
            for COM_b in [COM_high_b, COM_low_b]:
                err = abs(COM_r - COM_b)

                if err < error:
                    error = err
                    COM = (self.RB_RATIO * COM_r + COM_b)/(1 + self.RB_RATIO)

        print(COM)
        self.COM = COM
        return COM
        #return 0

    def update(self, bitmap):
        COM = self._get_COM(bitmap, self.row)

        # Draw red dot at COM
        bitmap[self.row, int(COM)] = 0x3F<<5

    def print_value(self):
        print((self.COM,))

row = 20
detector = LineDetector(row)

while True:
    #input()
    cam.capture(bitmap)

    # Process image
    detector.update(bitmap)
    #detector.print_value()
    #for i in range(0,60):
    #    print(str(i)+" "+str(bitmap[row,i]))
    # Draw red dot at COM
    #bitmap[row, 30] = 0x3F<<5

    # Refresh
    bitmap.dirty()
    display.refresh(minimum_frames_per_second=0)
    #t1 = time.monotonic_ns()
    #print("fps", 1e9 / (t1 - t0))
    #t0 = t1
