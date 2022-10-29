import numpy as np
from brainflow.data_filter import DataFilter, NoiseTypes, DetrendOperations, FilterTypes

num_classes = 6

# Load raw data (replace np.zeros with your own data)

data_recorder = []



data = np.zeros(shape=(1000, 150, 4))  # REPLACE WITH YOUR OWN DATA


labels = np.zeros(shape=(1000, num_classes))  # REPLACE WITH YOUR OWN DATA (Labels in vector form)


data_filtered = np.copy(data)
sampling_rate = 250

for i in range(0, data.shape[0]):
    for ch in range(0, data.shape[2]):
        sample = np.copy(data[i, :, ch], order='C')
        DataFilter.detrend(sample, DetrendOperations.CONSTANT)
        DataFilter.remove_environmental_noise(sample, sampling_rate, NoiseTypes.FIFTY_AND_SIXTY)
        DataFilter.perform_highpass(sample, sampling_rate, 8.0, 3, FilterTypes.BUTTERWORTH, ripple=0.0)
        sample = sample * 1e-3
        data_filtered[i, :, ch] = sample
