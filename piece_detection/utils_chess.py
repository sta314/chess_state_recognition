import chess
import chess.svg


def output_chess_board(board, file_name = "", lichess = False):
    board_svg = chess.svg.board(board, size=600)
    if file_name != "":
        with open(file_name, 'w') as f:
            f.write(board_svg)
    if lichess:
        print("Click & enjoy...")
        print("-----------------------")
        print("https://lichess.org/editor/" + board.board_fen())


def create_chessboard_from_board_array(board_array, isRoboflow = False):

    fen = board_array_to_fen(board_array, isRoboflow)

    board = chess.Board(fen)

    return board

def board_array_to_fen(board_array, isRoboflow = False):
    if not isRoboflow:
        pieces_lookup = {
            0  : 'K',  # white_king
            1  : 'Q',  # white_queen
            2  : 'R',  # white_rook
            3  : 'B',  # white_bishop
            4  : 'N',  # white_knight
            5  : 'P',  # white_pawn
            6  : 'k',  # black_king
            7  : 'q',  # black_queen
            8  : 'r',  # black_rook
            9  : 'b',  # black_bishop
            10 : 'n',  # black_knight
            11 : 'p'   # black_pawn
        }
    else:
        pieces_lookup = {
            1  : 'b',  # black_bishop
            2  : 'k',  # black_king
            3  : 'n',  # black_knight
            4  : 'p',  # black_pawn
            5  : 'q',  # black_queen
            6  : 'r',  # black_rook
            7  : 'B',  # white_bishop
            8  : 'K',  # white_king
            9  : 'N',  # white_knight
            10  : 'P',  # white_pawn
            11 : 'Q',  # white_queen
            12 : 'R'   # white_rook
        }

    fen_str = ""
    for row in board_array:
        empty = 0
        for cell in row:
            if cell == -1:
                empty += 1
            else:
                if empty != 0:
                    fen_str += str(empty)
                    empty = 0
                fen_str += pieces_lookup[cell] # TODO lookup
        if empty != 0:
            fen_str += str(empty)
        fen_str += "/"
    return fen_str[:-1]