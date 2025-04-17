import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, filtfilt, savgol_filter, find_peaks

# === Constants ===
SAMPLE_RATE = 100
WINDOW_DURATION = 10
N_SAMPLES = 1000

# === Filtering Functions ===
def bandpass_filter(signal, low, high, fs=SAMPLE_RATE, order=4):
    nyq = 0.5 * fs
    b, a = butter(order, [low / nyq, high / nyq], btype='band')
    return filtfilt(b, a, signal)

# === HR Peak Estimation ===
def estimate_hr(signal):
    smoothed = savgol_filter(signal, window_length=41, polyorder=3)
    distance = int(0.45 * SAMPLE_RATE)
    peaks, _ = find_peaks(smoothed, distance=distance, prominence=1.2)
    return round(len(peaks) * (60 / WINDOW_DURATION), 2)

# === RR Peak Estimation (improved) ===
def estimate_rr(signal):
    smoothed = savgol_filter(signal, window_length=81, polyorder=3)
    distance = int(2.5 * SAMPLE_RATE)  # Allow 24 RPM max
    peaks, _ = find_peaks(smoothed, distance=distance, prominence=0)
    return round(len(peaks) * (60 / WINDOW_DURATION), 2)

# === Load Dataset ===
data = np.load("dataset_non_sensorweb.npy")
n_frames = data.shape[0]

gt_hr, gt_rr = [], []
est_hr, est_rr = [], []

# === Frame-by-Frame Processing ===
for i in range(n_frames):
    signal = data[i, :N_SAMPLES]
    hr_true = data[i, -5]
    rr_true = data[i, -4]

    # Filtered signals
    filtered_hr = bandpass_filter(signal, low=0.7, high=3.5)
    filtered_rr = bandpass_filter(signal, low=0.1, high=0.6)

    hr_est = estimate_hr(filtered_hr)
    rr_est = estimate_rr(filtered_rr)

    gt_hr.append(hr_true)
    gt_rr.append(rr_true)
    est_hr.append(hr_est)
    est_rr.append(rr_est)

# === Error Metrics ===
hr_errors = np.abs(np.array(gt_hr) - np.array(est_hr))
rr_errors = np.abs(np.array(gt_rr) - np.array(est_rr))

print(f"✅ HR mean error: {np.mean(hr_errors):.2f} bpm")
print(f"✅ RR mean error: {np.mean(rr_errors):.2f} rpm")

# === Visualization ===
sample_limit = 500
plt.figure(figsize=(12, 6))

plt.subplot(1, 2, 1)
plt.plot(gt_hr[:sample_limit], label="True HR", linewidth=1)
plt.plot(est_hr[:sample_limit], label="Predicted HR", linestyle="--", linewidth=1)
plt.title("Heart Rate (BPM)")
plt.xlabel("Frame")
plt.ylabel("BPM")
plt.grid(True)
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(gt_rr[:sample_limit], label="True RR", linewidth=1)
plt.plot(est_rr[:sample_limit], label="Predicted RR", linestyle="--", linewidth=1)
plt.title("Respiration Rate (RPM)")
plt.xlabel("Frame")
plt.ylabel("RPM")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
