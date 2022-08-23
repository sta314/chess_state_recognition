import numpy as np
from chessboard_location.chessboard_finder import get_chessboard_intersections
from piece_detection.utils_chess import create_chessboard_from_board_array
from piece_detection.utils_corners import create_chessboard_array_from_assignments, denormalize_piece_info, get_squares_from_corners, is_top_left_white, match_pieces_with_squares
from piece_detection.utils_yolo import predict_image

def return_board_from_image(img, model, log = True, isRoboflow = False):

    if log:
        print("-----------------------")
        print("YOLOv5 detecting img...")
        print("-----------------------")
    prediction = predict_image(img, model)
    model_output_denormalized = denormalize_piece_info(prediction, img.shape[1], img.shape[0])

    if log:
        print("-----------------------")
        print("Getting chessboard intersections...")
        print("-----------------------")
    corners = get_chessboard_intersections(img)
    if corners is None:
        return None

    squares = get_squares_from_corners(corners)

    assigned_squares_list = match_pieces_with_squares(squares, model_output_denormalized)
    chessboard_array = create_chessboard_array_from_assignments(assigned_squares_list)

    fix_color = False # No need for current dataset
    if fix_color and not is_top_left_white(img, squares):
        chessboard_array = np.rot90(chessboard_array, 1, (0, 1))

    chessboard = create_chessboard_from_board_array(chessboard_array, isRoboflow)

    return chessboard
