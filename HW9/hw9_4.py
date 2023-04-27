import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

files = ["sigA.csv", "sigB.csv", "sigC.csv", "sigD.csv"]

for filename in files:
    # Read CSV
    t, v = pd.read_csv(filename).to_numpy().T
    
    # Generate FFT
    dt = t[1] - t[0]
    N = len(v)
    
    Y = (np.fft.fft(v)/N)[range(N//2)]
    freqs = np.fft.fftfreq(N, d=dt)[range(N//2)]

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle("Signal and FFT | " + filename)
    ax1.plot(t, v)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude')
    ax2.loglog(freqs, abs(Y))
    ax2.set_xlabel('Freq (Hz)')
    ax2.set_ylabel('|Y(freq)|')
    fig.tight_layout()
    plt.savefig(filename + ".sig_fft.png")
    plt.show()