import gridmakers as _gridmakers
import maze as _maze


def rectangle(**kwargs):
    """Generate a rectangular maze.

    kwargs are defined in the gridmakers module.
    """
    rectangle_grid = _gridmakers.rectangle(**kwargs)
    return _maze.Maze(rectangle_grid)


def string(s, **kwargs):
    """Generate a the character and maze for each character in s.

    kwargs are defined in the gridmakers module.
    """
    # get each non white-space character and convert to a maze
    for word in s.split():
        # remove all the whitespace
        for c in word:
            # make a maze for each character
            c_grid = _gridmakers.character(c, **kwargs)
            maze = _maze.Maze(c_grid)
            yield c, maze


if __name__ == '__main__':
    pass
