import numpy as np
import cv2

def denormalize_piece_info(piece_info, width, height):
    piece_info[:, (0, 2)] *= width
    piece_info[:, (1, 3)] *= height
    return piece_info

def get_squares_from_corners(corners):
    corners_reversed = corners[:, :, (1,0)].transpose((1, 0, 2))
    squares = np.zeros((8, 8, 2, 2, 2), dtype=np.int32)

    for i in range(8):
        for j in range(8):
            squares[i][j] = corners_reversed[i:i+2, j:j+2, :]
    return squares

def match_pieces_with_squares(square_info, piece_info):
    square_coords, confidences, labels = piece_info[:,:4].astype(np.int32), piece_info[:,4], piece_info[:,5].astype(np.int32)
    matchings = list()
    for piece_idx, piece in enumerate(square_coords):
        if confidences[piece_idx] < 0.6: # discard if confidence is lower than a threshold
            continue
        x_box = (piece[0] + (piece[2] - piece[0])/2)
        y_box = piece[3]
        isFound = False
        for i, square_row in enumerate(square_info):
            if isFound:
                break
            for j, square in enumerate(square_row):
                top_left_corner = square[0][0]
                top_right_corner = square[0][1]
                bottom_left_corner = square[1][0]
                bottom_right_corner = square[1][1]

                x_min = min(top_left_corner[0], bottom_left_corner[0])
                x_max = max(top_right_corner[0], bottom_right_corner[0])

                left_error_margin = abs(top_left_corner[1] - bottom_left_corner[1])//5
                right_error_margin = abs(top_right_corner[1] - bottom_right_corner[1])//5
                y_min = min(top_left_corner[1], top_right_corner[1]) + (left_error_margin + right_error_margin)//2
                y_max = max(bottom_left_corner[1], bottom_right_corner[1]) + (left_error_margin + right_error_margin)//2

                if x_max > x_box > x_min and y_max > y_box > y_min:
                    matchings.append(((i, j), labels[piece_idx]))
                    isFound = True
                    break
    return matchings

def create_chessboard_array_from_assignments(assignments_list):
    chessboard_array = np.full((8, 8), -1, dtype=np.int32)
    for assignment in assignments_list:
        chessboard_array[assignment[0][0], assignment[0][1]] = assignment[1]
    return chessboard_array

def is_top_left_white(img, square_info):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 2]
    square_variances = np.zeros((8, 8), dtype=np.int32)
    square_means = np.zeros((8, 8), dtype=np.int32)
    for i in range(8):
        for j in range(8):
            square_to_check = square_info[i][j]
            np_square = np.concatenate(square_to_check)
            mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.fillConvexPoly(mask, np_square[(1,0,2,3), :], (255))
            masked_image = cv2.bitwise_and(gray, mask)
            masked_image_flattened = masked_image.reshape(-1)
            
            square_variances[i][j] = np.var(masked_image_flattened[np.nonzero(masked_image_flattened)])
            square_means[i][j] = np.mean(masked_image_flattened[np.nonzero(masked_image_flattened)])


    cum_mean = np.mean(square_means)

    diff_arr = abs(square_means - cum_mean)

    lowest_variance_idx = np.unravel_index(np.argmax(diff_arr, axis=None), square_variances.shape)

    is_lowest_variance_square_white = square_means[lowest_variance_idx] > cum_mean
    return not(is_lowest_variance_square_white ^ (np.sum(lowest_variance_idx) % 2 == 0))
    
