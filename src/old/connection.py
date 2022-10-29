import time
import argparse
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets

# ------------------------------------------------------
SYNTH = -1
CYTON = 0
MUSE2016 = 42

def connect_and_read_data(board_id, serial_port:str=None):
    params = BrainFlowInputParams()

    if board_id != -1: 
        assert serial_port != None
        params.serial_port = serial_port

    board = BoardShim(board_id, params)
    board.prepare_session()
    board.start_stream()
    time.sleep(10)
    # data = board.get_current_board_data (256) # get latest 256 packages or less, doesnt remove them from internal buffer
    data = board.get_board_data()  # get all data and remove it from internal buffer
    board.stop_stream()
    board.release_session()

    print(data)


if __name__ == "__main__":
    connect_and_read_data(board_id=SYNTH)
    connect_and_read_data(board_id=MUSE2016, serial_port="COM4")