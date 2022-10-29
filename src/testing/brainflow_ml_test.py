import argparse
import time

from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels
from brainflow.data_filter import DataFilter
from brainflow.ml_model import MLModel, BrainFlowMetrics, BrainFlowClassifiers, BrainFlowModelParams


def main():
    BoardShim.enable_board_logger()
    DataFilter.enable_data_logger()
    MLModel.enable_ml_logger()
    
    params = BrainFlowInputParams()

    board = BoardShim(-1, params)
    master_board_id = board.get_board_id()
    sampling_rate = BoardShim.get_sampling_rate(master_board_id)
    board.prepare_session()
    board.start_stream(45000, '')
    BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'start sleeping in the main thread')
    time.sleep(5)  # recommended window size for eeg metric calculation is at least 4 seconds, bigger is better
    data = board.get_board_data()
    # board.stop_stream()
    # board.release_session()

    eeg_channels = BoardShim.get_eeg_channels(int(master_board_id))

    sampling_rate = BoardShim.get_sampling_rate(int(master_board_id))

    mindfulness_params = BrainFlowModelParams(BrainFlowMetrics.MINDFULNESS.value,
                                                BrainFlowClassifiers.DEFAULT_CLASSIFIER.value)
    mindfulness = MLModel(mindfulness_params)
    mindfulness.prepare()

    restfulness_params = BrainFlowModelParams(BrainFlowMetrics.RESTFULNESS.value,
                                                BrainFlowClassifiers.DEFAULT_CLASSIFIER.value)
    restfulness = MLModel(restfulness_params)
    restfulness.prepare()

    new_classifer = BrainFlowModelParams(BrainFlowMetrics.USER_DEFINED.value, 
                                                BrainFlowClassifiers.DEFAULT_CLASSIFIER.value)


    print(str(mindfulness_params.to_json()))
    print("\n")
    print(str(restfulness_params.to_json()))

    WINDOWSIZE = 3

    time.sleep(3)
    while True:
        
        data = board.get_current_board_data(sampling_rate*WINDOWSIZE)

        bands = DataFilter.get_avg_band_powers(data, eeg_channels, sampling_rate, True) 
        feature_vector = bands[0]

        print(f"Feature Vector: {feature_vector}" + \
            f", Mindfulness: {str(mindfulness.predict(feature_vector))}" + \
                f", Restfulness: {str(restfulness.predict(feature_vector))}" )


        time.sleep(3)


if __name__ == "__main__":
    main()