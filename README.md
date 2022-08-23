# **Recognizing Chess Game State from an Image**
This project digitizes the game state for a given photo that contains chessboard, with pieces on it.

![Example Photo 1](https://cdn.hashnode.com/res/hashnode/image/upload/v1661265010510/GAFytnjZi.jpg "Example Photo 1")

![Example Photo 2](https://cdn.hashnode.com/res/hashnode/image/upload/v1661266153519/grmjTR7dB.jpg "Example Photo 2")

## Blog post

Detailed explanation of the project is available in [my blog post](https://mshcs.hashnode.dev/recognizing-chess-game-state-from-an-image).

## How to use?

#### For a single image
```sh
python main.py input_image output_folder [--local] [--roboflow]
```
Result will get written to the output folder.

Example:
```sh
python main.py examples/small_test/0046.png . [--local] [--roboflow]
```
#### For image batch in a folder
```sh
python main.py input_folder output_folder [--local] [--roboflow]
```
Results will get written to the output folder.