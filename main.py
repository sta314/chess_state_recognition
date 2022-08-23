from chessboard_location.utils_chessboard import *
from chessboard_location.utils_visual import *
from chessboard_location.chessboard_finder import get_chessboard_intersections
from piece_detection.chessboard_detector import return_board_from_image
from piece_detection.utils_chess import create_chessboard_from_board_array, output_chess_board
from piece_detection.utils_yolo import load_yolo_model

import os
import argparse
from tqdm import tqdm
import time

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument('path', type=str, nargs=1)
    parser.add_argument('out', type=str, nargs=1)
    parser.add_argument(
            "-r",
            "--roboflow",
            action="store_true")
    parser.add_argument(
            "-l",
            "--local",
            action="store_true")
    
    args = parser.parse_args()

    path = args.path[0]
    out_dir = args.out[0]
    isRoboflow = args.roboflow
    isLocal = args.local

    if not isRoboflow:
        imported_model = load_yolo_model("weights/best.pt", isLocal)
    else:
        imported_model = load_yolo_model("weights/best_roboflow.pt", isLocal)
    
    if os.path.isfile(path):

        img = cv2.imread(path, cv2.IMREAD_COLOR)

        chessboard = return_board_from_image(img, imported_model, True, isRoboflow)
        if chessboard is None:
            print("Failed")
            exit(0)

        output_chess_board(chessboard, file_name = os.path.join(out_dir, os.path.basename(path).split('.')[0] + ".svg"), lichess = True)
        
    else:
        output_folder = out_dir + "/" + str(time.time())
        os.makedirs(output_folder, exist_ok=True)
        for filename in tqdm(os.listdir(path)):
            print("Processing file : ", filename)
            f = os.path.join(path, filename)
            img = cv2.imread(f)
            
            chessboard = return_board_from_image(img, imported_model, False, isRoboflow)
            if chessboard is None:
                print("Failed for ", filename)
                continue
            
            cv2.imwrite(os.path.join(output_folder, os.path.basename(filename)), img)
            output_chess_board(chessboard, file_name = os.path.join(output_folder, os.path.basename(filename).split('.')[0] + ".svg"), lichess = True)

if __name__ == "__main__":
    main()
