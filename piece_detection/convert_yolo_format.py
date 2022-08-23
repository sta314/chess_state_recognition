import json
from os import listdir
from os.path import isfile, join, splitext, basename
from pathlib import Path

###                             ###
### ONLY USED FOR PREPROCESSING ###
###                             ###

image_width = 1200
image_height = 800

pieces_lookup = {
    'K': '0',  # white_king
    'Q': '1',  # white_queen
    'R': '2',  # white_rook
    'B': '3',  # white_bishop
    'N': '4',  # white_knight
    'P': '5',  # white_pawn

    'k': '6',  # black_king
    'q': '7',  # black_queen
    'r': '8',  # black_rook
    'b': '9',  # black_bishop
    'n': '10', # black_knight
    'p': '11', # black_pawn
}

directory_path = "datasets/train"
files = [f for f in listdir(directory_path) if isfile(join(directory_path, f)) and f.endswith(".json")]


for file_path in files:

    file = open(join(directory_path, file_path), mode='r')
    data_json = json.load(file)

    all_pieces = data_json["pieces"]

    with open(join(directory_path, splitext(file_path)[0] + ".txt"), "w") as file:
        for piece_information in all_pieces:
            x_min, y_min, x_shift, y_shift = piece_information["box"]
            x_center = (x_min + x_shift/2) / image_width
            y_center = (y_min + y_shift/2) / image_height
            width = x_shift / image_width
            height = y_shift / image_height
            
            file.write(pieces_lookup[piece_information["piece"]] + " " + str(x_center) + " " + str(y_center) + " " + str(width) + " " + str(height) + "\n")


for file_path in files:
    p = Path(join(directory_path, file_path)).absolute()
    parent_dir = p.parent.parent
    
    old_labels_path = parent_dir / (basename(directory_path) + "_oldlabels")
    old_labels_path.mkdir(parents=False, exist_ok=True)

    p.rename(old_labels_path / p.name)

