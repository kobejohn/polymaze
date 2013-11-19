import random as _random

import gridmakers as _gridmakers
import maze as _maze
import shapes as _shapes


_supershapes_dict = _shapes.supershapes_dict()


def rectangle(supershape=None, grid_v_bound=None, grid_h_bound=None):
    rectangle_grid = _gridmakers.rectangle(vertical_shapes=grid_v_bound,
                                           horizontal_shapes=grid_h_bound,
                                           supershape=supershape)
    return _maze.Maze(rectangle_grid)


def string(s, supershape=None, grid_v_bound=None, grid_h_bound=None):
    """Generate a the character and maze for each character in s."""
    # provide default values
    use_random = supershape is None
    for word in s.split():
        for c in word:
            if use_random:
                supershape = _random.choice(_supershapes_dict.values())
            c_grid = _gridmakers.character(c, supershape=supershape,
                                           max_vertical_indexes=grid_v_bound,
                                           max_horizontal_indexes=grid_h_bound)
            maze = _maze.Maze(c_grid)
            yield c, maze


if __name__ == '__main__':
    pass
