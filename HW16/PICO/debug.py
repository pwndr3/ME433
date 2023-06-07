# get a line of raw bitmap and plot the components
import matplotlib.pyplot as plt 
import numpy as np
plt.ion()

import serial
ser = serial.Serial('COM4',230400) # the name of your Pico port
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

    reds = get_data()

    # plot the colors 
    plt.clf()
    
    cumsum = np.cumsum(reds)

    filter = np.array([1, 0, -1])
    edges = np.convolve(cumsum, filter, "same")[:-1]

    plt.plot(edges)

    idxs = np.where(edges > (np.mean(edges)))[0]
    COM = idxs[int(np.average(np.arange(0, len(edges[idxs])), weights=edges[idxs]))]

    print("COMPUTER COM", COM)
    #plt.plot(bright, linewidth=3)
    #plt.axvline(COM)

# be sure to close the port
ser.close()