# get a line of raw bitmap and plot the components
import matplotlib.pyplot as plt 
plt.ion()

import serial
ser = serial.Serial('COM4',230400) # the name of your Pico port
print('Opening port: ')
print(ser.name)

while True:
    if input().strip() == "q":
        break

    ser.write(b'hi\r\n') # send a newline to request data
    data_read = ser.read_until(b'\n',50) # read the echo

    sampnum = 0
    index = 0
    raw = []
    reds = []
    greens = []
    blues = []
    bright = []

    # Pico sends back index and raw pixel value
    while sampnum < 60: # width of bitmap
        data_read = ser.read_until(b'\n',50) # read until newline
        data_text = str(data_read,'utf-8') # convert bytes to string
        data = list(map(int,data_text.split())) # convert string to values

        if(len(data)==2):
            index = data[0]
            raw.append(data[1])
            reds.append(((data[1]>>5)&0x3F)/0x3F*100) # red value is middle 6 bits
            greens.append((data[1]&0x1F)/0x1F*100) # green value is rightmost 5 bits
            blues.append(((data[1]>>11)&0x1F)/0x1F*100) # blue vale is leftmost 5 bits
            bright.append((data[1]&0x1F)+((data[1]>>5)&0x3F)+((data[1]>>11)&0x1F)) # sum of colors
            sampnum = sampnum + 1

    import numpy as np
    reds = np.array(reds)
    greens = np.array(greens)
    blues = np.array(blues)

    # plot the colors 
    plt.clf()
    x = range(len(reds)) # time array
    #plt.plot(x,reds,'r*-',x,greens,'g*-',x,blues,'b*-')
    #plt.ylabel('color')
    #plt.xlabel('position')
    #plt.show()

    bright = np.cumsum(reds)
    filter = np.array([1, 0, -1])
    bright = np.convolve(bright, filter, "same")[:-1]
    x = x[:-1]

    idxs = np.where(bright > (np.mean(bright)))[0]
    COM = idxs[int(np.average(np.arange(0, len(bright[idxs])), weights=bright[idxs]))]

    plt.plot(x, bright, linewidth=3)
    plt.axvline(COM)

# be sure to close the port
ser.close()