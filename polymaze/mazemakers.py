import gridmakers as _gridmakers
import maze as _maze


def rectangle(**kwargs):
    """Generate a rectangular maze.

    kwargs:
    supershape - a supershape class that defines how the maze will look
    complexity - scale the difficulty of the maze to any positive number
                 e.g. 0.5 is very simple, 1000 is very difficult
    aspect_h - relative height of the result image (square if only one provided)
    aspect_w - relative width of the result image (square if only one provided)
    """
    rectangle_grid = _gridmakers.rectangle(**kwargs)
    return _maze.Maze(rectangle_grid)


def string(s, **kwargs):
    """Generate a the character and maze for each character in s.

    kwargs:
    supershape - a supershape class that defines how the maze will look
    complexity - scale the difficulty of the maze to any positive number
                 e.g. 0.5 is very simple, 1000 is very difficult
    aspect_h - relative height of the result image (square if only one provided)
    aspect_w - relative width of the result image (square if only one provided)
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
