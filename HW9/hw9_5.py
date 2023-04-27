import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

files = ["sigA.csv", "sigB.csv", "sigC.csv", "sigD.csv"]
X = [500, 250, 10, 10]

def maf(v, Xval):
    res = []
    
    for i in range(len(v) - Xval):
        res.append(np.average(v[i:i+Xval]))
        
    return np.array(res)

def fft(t, v):
    # Generate FFT
    dt = t[1] - t[0]
    N = len(v)
    
    Y = (np.fft.fft(v)/N)[range(N//2)]
    freqs = np.fft.fftfreq(N, d=dt)[range(N//2)]
    
    return freqs, Y

for i, filename in enumerate(files):
    # Read CSV
    t, v = pd.read_csv(filename).to_numpy().T

    # Filter data
    v_filt = maf(v, X[i])
    freqs_filt, Y_filt = fft(t, v_filt)
    
    # Get FFT
    freqs, Y = fft(t, v)

    # Plot
    fig, (ax1, ax2) = plt.subplots(2, 1)
    fig.suptitle(r"Signal and FFT | $X = " + str(X[i]) + r"$ | " + filename)
    ax1.plot(t, v, "k", label="Unfiltered")
    ax1.plot(t[:-X[i]], v_filt, "tab:red", label="Filtered")
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude')
    ax1.legend()
    ax2.loglog(freqs, abs(Y), "k", label="Unfiltered")
    ax2.loglog(freqs_filt, abs(Y_filt), "tab:red", label="Filtered")
    ax2.set_xlabel('Freq (Hz)')
    ax2.set_ylabel('|Y(freq)|')
    ax2.legend()
    fig.tight_layout()
    plt.savefig(filename + ".maf.png")
    plt.show()