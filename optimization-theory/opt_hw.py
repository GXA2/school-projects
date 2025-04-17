import numpy as np
import matplotlib.pyplot as plt
from skimage.restoration import denoise_tv_chambolle  # TV denoising function

# ----------------------------
# Generate the original and noisy signal
# ----------------------------
fs = 100000         # Sampling frequency (Hz)
T = 1               # Duration (seconds)
t = np.linspace(0, T, fs * T, endpoint=False)

# Define sine wave components
frequencies = [50, 150, 300, 600]   # Hz
amplitudes = [1.0, 0.8, 0.5, 0.3]
phases = [0, np.pi/4, np.pi/2, np.pi]

# Generate multi-sine wave
multi_sine_wave = sum(A * np.sin(2 * np.pi * f * t + p) 
                      for A, f, p in zip(amplitudes, frequencies, phases))

# Add Gaussian noise (stronger noise ~15% of max amplitude)
noise_std = 0.15  
noise = np.random.normal(0, noise_std, size=t.shape)
noisy_signal = multi_sine_wave + noise

# ----------------------------
# Quadratic smoothing function using Tikhonov regularization
# ----------------------------
def quadratic_smoothing(signal, lam):
    """
    Solves:
        min_x ||x - y||^2 + lam * sum((x[i+1]-x[i])^2)
    by solving the linear system: (I + lam*D^T D)x = y,
    where D is the first-difference operator.
    """
    n = len(signal)
    # Set up the tridiagonal matrix diagonals
    main = np.empty(n)
    main[0] = 1 + lam
    main[-1] = 1 + lam
    main[1:-1] = 1 + 2 * lam
    lower = -lam * np.ones(n - 1)
    upper = -lam * np.ones(n - 1)
    
    # Solve using the Thomas algorithm
    x = signal.copy().astype(float)
    # Forward elimination
    for i in range(1, n):
        m = lower[i - 1] / main[i - 1]
        main[i] = main[i] - m * upper[i - 1]
        x[i] = x[i] - m * x[i - 1]
    # Back substitution
    x[-1] = x[-1] / main[-1]
    for i in range(n - 2, -1, -1):
        x[i] = (x[i] - upper[i] * x[i + 1]) / main[i]
    return x

# Apply quadratic smoothing for several lambda values
quad_lam_values = [0.01, 0.1, 1.0]  # You can experiment with these
quad_smoothed_signals = {lam: quadratic_smoothing(noisy_signal, lam) 
                         for lam in quad_lam_values}

# ----------------------------
# Total Variation (TV) smoothing using skimage
# ----------------------------
# The 'weight' parameter here corresponds to the λ factor.
tv_lam_values = [0.01, 0.1, 1.0]  # Example lambda values for TV smoothing
tv_smoothed_signals = {}
for lam in tv_lam_values:
    # Note: denoise_tv_chambolle works with 1D arrays when multichannel=False.
    tv_smoothed = denoise_tv_chambolle(noisy_signal, weight=lam)
    tv_smoothed_signals[lam] = tv_smoothed

# ----------------------------
# Plotting the results (zoomed in to first 5000 samples for clarity)
# ----------------------------
plt.figure(figsize=(12, 10))

# Plot original and noisy signals
plt.subplot(3, 1, 1)
plt.plot(t[:5000], noisy_signal[:5000], label="Noisy Signal", color='r', alpha=0.7)
plt.plot(t[:5000], multi_sine_wave[:5000], label="Original Signal", color='b', linestyle='dashed', alpha=0.5)
plt.title("Original and Noisy Signal")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.legend()
plt.grid()

# Plot Quadratic Smoothing results
plt.subplot(3, 1, 2)
for lam, smoothed in quad_smoothed_signals.items():
    plt.plot(t[:5000], smoothed[:5000], label=f"Quadratic (λ={lam})")
plt.title("Quadratic Smoothing Results")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.legend()
plt.grid()

# Plot TV Smoothing results
plt.subplot(3, 1, 3)
for lam, smoothed in tv_smoothed_signals.items():
    plt.plot(t[:5000], smoothed[:5000], label=f"TV (λ={lam})")
plt.title("Total Variation Smoothing Results")
plt.xlabel("Time [s]")
plt.ylabel("Amplitude")
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()

