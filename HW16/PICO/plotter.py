# get a line of raw bitmap and plot the components
import matplotlib.pyplot as plt 
plt.ion()

import serial
ser = serial.Serial('COM3',230400) # the name of your Pico port
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

    # 1) Average - maybe not necessary
    filter = np.array([1, 2, 1])
    filter = filter / np.sum(filter)
    reds = np.convolve(reds, filter, "same")
    blues = np.convolve(blues, filter, "same")

    # 2) Normalize around average then cumsum
    reds = (reds - np.average(reds))/np.std(reds)
    blues = (blues - np.average(blues))/np.std(blues)

    reds = np.cumsum(reds)
    blues = np.cumsum(blues)

    reds -= np.min(reds)
    blues -= np.min(blues)

    # 3) Get COM for higher and lower than average, for blue and red channels
    def value(arr, percentile):
        ptp = np.ptp(arr)
        return np.min(arr) + percentile * ptp

    def COM(arr, idxs):
        COM = 0
        s = 0
        for i, idx in enumerate(idxs):
            COM += i * arr[idx]
            s += arr[idx]
        COM /= s
        return idxs[int(COM)]

    def COM_high(arr):
        idxs = np.where(arr > value(arr, 0.75))[0]
        return COM(arr, idxs)
    def COM_low(arr):
        idxs = np.where(arr < value(arr, 0.25))[0]
        print(idxs)
        print(arr)
        return COM(arr, idxs)

    COM_high_r = COM_high(reds)
    COM_high_b = COM_high(blues)
    #print(COM_high_r, COM_high_b)

    COM_low_r = COM_low(reds)
    COM_low_b = COM_low(blues)
    #print(COM_low_r, COM_low_b)

    COM = 0
    error = len(reds)
    r_b_ratio = 2.0
    for COM_r in [COM_high_r, COM_low_r]:
        for COM_b in [COM_high_b, COM_low_b]:
            err = abs(COM_r - COM_b)

            if err < error:
                error = err
                COM = (r_b_ratio * COM_r + COM_b)/(1 + r_b_ratio)

    # plot the colors 
    plt.clf()
    x = range(len(reds)) # time array
    plt.plot(x,reds,'r*-',x,blues,'b*-')
    #plt.plot(x,combined,linewidth=3)
    plt.ylabel('color')
    plt.xlabel('position')
    plt.axvline(COM)
    plt.axhline(value(blues, 0.8),c="b")
    plt.axhline(value(reds, 0.8),c="r")
    plt.axhline(value(blues, 0.2),c="b")
    plt.axhline(value(reds, 0.2),c="r")
    plt.show()

    """bright = np.cumsum(reds)
    filter = np.array([1, 0, -1])
    bright = np.convolve(bright, filter, "same")[:-1]
    x = x[:-1]

    idxs = np.where(bright > (np.mean(bright)))[0]
    COM = idxs[int(np.average(np.arange(0, len(bright[idxs])), weights=bright[idxs]))]

    plt.plot(x, bright, linewidth=3)
    plt.axvline(COM)"""

# be sure to close the port
ser.close()