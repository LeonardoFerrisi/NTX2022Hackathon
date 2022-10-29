import glob
import argparse
import os
import pickle
import logging
from re import L

import numpy as np
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import StackingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import cross_val_score

from brainflow.board_shim import BoardShim
from brainflow.data_filter import DataFilter

from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType


def write_model(intercept, coefs, model_type):
    coefficients_string = '%s' % (','.join([str(x) for x in coefs[0]]))
    file_content = '''
#include "%s"
// clang-format off
const double %s_coefficients[%d] = {%s};
double %s_intercept = %lf;
// clang-format on
''' % (f'{model_type}_model.h', model_type, len(coefs[0]), coefficients_string, model_type, intercept)
    file_name = f'{model_type}_model.cpp'
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..', 'generated', file_name)
    with open(file_path, 'w') as f:
        f.write(file_content)
# [  ['unfocused', data[2:14, 2:30]], ['focused', data[]]  ]
def prep_data(data:list ,labels: list, datasets: list, board_id:int, blacklisted_channels = None):
    """
    Prepares data from provided labels and file names and pickles them

    Currently only supports binary classification

    Params:
        classes (list (str)): a list of labels of what the dataset at the same index in the datasets parameter
        datasets (list (str): a list of filenames
        blacklisted_channels (str): a list of the channels to ignore. Can be None
    """
    # use different windows, its kinda data augmentation
    window_sizes = [4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    overlaps = [0.5, 0.475, 0.45, 0.425, 0.4, 0.375, 0.35] # percentage of window_size

    # create empty lists to hold the datasets
    feature_vectors = list() # [[fladgj] ]
    vector_labels   = list()

    ls =  enumerate(labels) 
    labelset = list()
    for l in ls: labelset.append(l)

    for label, datafilename in zip(labelset, datasets): # example [[relaxed, dataset], [focused, dataset], [focused, dataset]]
        
        logging.info(f"Loading: {datafilename}")
        board_id = board_id

        try:
            board_id = int(board_id)
            data = DataFilter.read_file(datafilename)

            sampling_rate = BoardShim.get_sampling_rate(board_id)
            eeg_channels = get_eeg_channels(board_id, blacklisted_channels)
            for num, window_size in enumerate(window_sizes):
                cur_pos = sampling_rate * 10
                while cur_pos + int(window_size * sampling_rate) < data.shape[1]:
                    data_in_window = data[:, cur_pos:cur_pos + int(window_size * sampling_rate)]
                    data_in_window = np.ascontiguousarray(data_in_window)
                    bands = DataFilter.get_avg_band_powers(data_in_window, eeg_channels, sampling_rate, True)
                    feature_vector = bands[0]
                    feature_vector = feature_vector.astype(float)

                    feature_vectors.append(feature_vector)

                    vector_labels.append( label[0] )

                    cur_pos = cur_pos + int(window_size * overlaps[num] * sampling_rate)
        except Exception as e:
            logging.error(str(e), exc_info=True)

        logging.info('1st Class: %d 2nd Class: %d' % (len([x for x in vector_labels if x == 0]), len([x for x in vector_labels if x == 1])))

    with open('dataset_x.pickle', 'wb') as f:
        pickle.dump(feature_vectors, f, protocol=3)
    with open('dataset_y.pickle', 'wb') as f:
        pickle.dump(vector_labels, f, protocol=3)

    return feature_vectors, vector_labels


# [  [A; i8530, B: 550]  ], [  ['unfocuesd;]  ] 

def get_eeg_channels(board_id, blacklisted_channels):
    eeg_channels = BoardShim.get_eeg_channels(board_id)
    try:
        eeg_names = BoardShim.get_eeg_names(board_id)
        selected_channels = list()
        if blacklisted_channels is None:
            blacklisted_channels = set()
        for i, channel in enumerate(eeg_names):
            if not channel in blacklisted_channels:
                selected_channels.append(eeg_channels[i])
        eeg_channels = selected_channels
    except Exception as e:
        logging.warn(str(e))
    logging.info('channels to use: %s' % str(eeg_channels))
    return eeg_channels

def print_dataset_info(data):
    x, y = data
    first_class_ids = [idx[0] for idx in enumerate(y) if idx[1] == 0]
    second_class_ids = [idx[0] for idx in enumerate(y) if idx[1] == 1]
    x_first_class = list()
    x_second_class = list()
    
    for i, x_data in enumerate(x):
        if i in first_class_ids:
            x_first_class.append(x_data.tolist())
        elif i in second_class_ids:
            x_second_class.append(x_data.tolist())
    second_class_np = np.array(x_second_class)
    first_class_np = np.array(x_first_class)

    logging.info('1st Class Dataset Info:')
    logging.info('Mean:')
    logging.info(np.mean(first_class_np, axis=0))
    logging.info('2nd Class Dataset Info:')
    logging.info('Mean:')
    logging.info(np.mean(second_class_np, axis=0))

def train_regression(data, metric_name = None):
    if metric_name == None: raise Exception("metric name cannot be None")
    model = LogisticRegression(solver='liblinear', max_iter=4000,
                                penalty='l2', random_state=2, fit_intercept=True, intercept_scaling=0.2)
    logging.info('#### Logistic Regression ####')
    scores = cross_val_score(model, data[0], data[1], cv=5, scoring='f1_macro', n_jobs=8)
    logging.info('f1 macro %s' % str(scores))
    model.fit(data[0], data[1])
    logging.info(model.intercept_)
    logging.info(model.coef_)
    
    initial_type = [(f'{metric_name}_input', FloatTensorType([1, 5]))]
    onx = convert_sklearn(model, initial_types=initial_type, target_opset=11, options={type(model): {'zipmap': False}})
    with open(f'logreg_{metric_name}.onnx', 'wb') as f:
        f.write(onx.SerializeToString())
    write_model(model.intercept_, model.coef_, f'{metric_name}')

def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument('--reuse-dataset', action='store_true')
    args = parser.parse_args()

    # if args.reuse_dataset:
    #     with open('dataset_x.pickle', 'rb') as f:
    #         dataset_x = pickle.load(f)
    #     with open('dataset_y.pickle', 'rb') as f:
    #         dataset_y = pickle.load(f)
    #     data = dataset_x, dataset_y
    # else:

    datasets = [
        ('not_focused', data),
        ('focused', data),
        ()
    
    
    ]
    data = prep_data(['not_focused', 'focused'], datasets=[], board_id=0)
    data = prep_data('relaxed', 'focused', blacklisted_channels={'T3', 'T4'})

    print_dataset_info(data)

    train_regression(data, metric_name="concentration")



if __name__ == '__main__':
    main()