# get a line of raw bitmap and plot the components
import matplotlib.pyplot as plt 
import numpy as np
plt.ion()

import serial
ser = serial.Serial('COM3',230400) # the name of your Pico port
print('Opening port: ')
print(ser.name)

def get_data():
    ser.write(b'gimme\r\n')
    data_read = ser.read_until(b'\n',50) # read the echo
    data = []
    while True:
        data_read = ser.read_until(b'\n',50) # read until newline
        data_text = str(data_read,'utf-8') # convert bytes to string

        if "END" in data_text:
            break

        data.append(float(data_text))
    print(len(data))
    return np.array(data)

while True:
    if input().strip() == "q":
        break

    reds_pico = get_data()
    #cumsum_pico = get_data()

    # 1) Average - maybe not necessary
    filter = np.array([1, 2, 1])
    filter = filter / np.sum(filter)
    reds = np.convolve(reds_pico, filter, "same")

    # 2) Normalize around average then cumsum
    reds = (reds - np.average(reds))/np.std(reds)

    reds = np.cumsum(reds)

    reds -= np.min(reds)
    blues = reds

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
    #plt.clf()
    #plt.plot(cumsum_pico, "r")
    #plt.plot(reds, "b")

    print("COMPUTER COM", COM)
    data_read = ser.read_until(b'\n',50)
    print("PICO COM", COM)
    
    """cumsum = np.cumsum(reds)

    filter = np.array([1, 0, -1])
    edges = np.convolve(cumsum, filter, "same")[:-1]

    plt.plot(edges)

    idxs = np.where(edges > (np.mean(edges)))[0]
    COM = idxs[int(np.average(np.arange(0, len(edges[idxs])), weights=edges[idxs]))]

    print("COMPUTER COM", COM)"""
    #plt.plot(bright, linewidth=3)
    #plt.axvline(COM)

# be sure to close the port
ser.close()