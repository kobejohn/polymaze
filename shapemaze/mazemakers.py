import random

import gridmakers as _gridmakers
import maze as _maze
import shapes as _shapes


_supershapes_dict = _shapes.supershapes_dict()


def rectangle_maze(vertical_shapes=None, horizontal_shapes=None,
                   supershape=None):
    rectangle_grid = _gridmakers.rectangle(vertical_shapes=vertical_shapes,
                                           horizontal_shapes=horizontal_shapes,
                                           supershape=supershape)
    return _maze.Maze(rectangle_grid)


def string_to_mazes(string, supershape=None,
                    max_vertical=None, max_horizontal=None):
    """Generate a the character and maze for each character in string."""
    # provide default values
    max_v, max_h = max_vertical, max_horizontal
    use_random = supershape is None
    for word in string.split():
        for c in word:
            if use_random:
                supershape = random.choice(_supershapes_dict.values())
            c_grid = _gridmakers.character(c, supershape=supershape,
                                           max_vertical_indexes=max_v,
                                           max_horizontal_indexes=max_h)
            maze = _maze.Maze(c_grid)
            yield c, maze


if __name__ == '__main__':
    pass
