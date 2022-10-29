from connect import Comms
import time

from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels
from brainflow.data_filter import DataFilter
from brainflow.ml_model import MLModel, BrainFlowMetrics, BrainFlowClassifiers, BrainFlowModelParams
import numpy as np

import os

import csv
def get_feature_vector(data, board_id:int, sample_rate):
    eeg_channels = BoardShim.get_eeg_channels(board_id)
    bands = DataFilter.get_avg_band_powers(data, eeg_channels, sample_rate, True)
    feature_vector = bands[0]
    return feature_vector

WINDOWSIZE = 3

c = Comms(board_id=-1)
c.start(inf=True)

time.sleep(3)

current_data = c.get_current_data(WINDOWSIZE)

print(current_data)



start = time.time()

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, "outputs\\feature_vectors.csv")
print(filename)


count =0 

f = get_feature_vector(current_data, c.board_id, c.sampling_rate)

with open(filename, 'w') as csvfile: 
        csvwriter = csv.writer(csvfile)         
        csvwriter.writerow(f) 

print(f"wrote a line : {count}")
count+=1

time.sleep(3)

while time.time() < start+21:
    
    f = get_feature_vector(current_data, c.board_id, c.sampling_rate)

    with open(filename, 'a') as csvfile: 
        csvwriter = csv.writer(csvfile)         
        csvwriter.writerow(f) 

    print(f"wrote a line : {count}")
    count+=1
    time.sleep(3)


c.stop()
print("````````````````````````````````````````````````````\n")
with open(filename, 'r') as file:
    for line in file:
        print(str(line))
