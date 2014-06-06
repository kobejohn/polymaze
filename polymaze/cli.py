#! /usr/bin/python
import argparse
from datetime import datetime

import PIL.Image

from .shapes import supershapes_dict
from .maze import Maze
from .polygrid import PolyGrid


ss_dict = supershapes_dict()


def commandline():
    parser = _parser()
    kwargs = vars(parser.parse_args())
    # setup the base grid with a supershape if provided
    grid = PolyGrid(supershape=ss_dict.get(kwargs.pop('shape'), None))

    # pull off non-common parameters
    string = kwargs.pop('string')
    image_path = kwargs.pop('image')
    font_path = kwargs.pop('font')
    filename = kwargs.pop('output')

    # fill the grid and create maze based on the remaining arguments provided
    if string:
        grid.create_string(string, font_path=font_path, **kwargs)
        maze_type = 'String'
    elif image_path:
        image = PIL.Image.open(image_path).convert('L')
        if not image:
            print('Unable to open the provided image path: {}'
                  ''.format(image_path))
        grid.create_from_image(image, **kwargs)
        maze_type = 'Image'
    else:
        grid.create_rectangle(**kwargs)
        maze_type = 'Rectangle'

    maze = Maze(grid)
    save_maze(maze, maze_type, filename)


def save_maze(maze, maze_type, filename=None):
    image = maze.image()
    if image is None:
        print('This maze appears to be empty. Not saving.')
    else:
        now_str = str(datetime.now().time())
        clean_now_string = now_str.replace(':', '.').rsplit('.', 1)[0]
        if filename is None:
            filename = '{} - {} made with {}.png'.format(clean_now_string,
                                                         maze_type,
                                                         maze.shape_name())
        image.save(filename)
        print(filename)


def _parser():
    parser = argparse.ArgumentParser(description='Make and save mazes.')
    # optional top level type of maze to make (default rectangle)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-s', '--string',
                       help='Make a maze for each character in STRING.')
    group.add_argument('-i', '--image',
                       help='Make a maze from IMAGE (path).')
    # optional complexity
    parser.add_argument('-c', '--complexity', type=_positive,
                        help='Numeric scale for complexity.'
                             ' 0.5 is easy. 100 is WTFImpossible (tm).')
     # optional shape to use
    ss_names = ss_dict.keys()
    parser.add_argument('-S', '--shape', choices=ss_names,
                        help='Make the maze with this shape. Random otherwise.')
    # optional aspect (relative height)
    parser.add_argument('-a', '--aspect', type=_positive,
                        help='Set the height/width aspect of the maze.')
    parser.add_argument('-f', '--font', type=str,
                        help='Provide a font name/path for string mazes.')
    parser.add_argument('-o', '--output', type=str, help='Output filename.')
    return parser


def _positive(v):
    try:
        number = float(v)
    except Exception:
        raise argparse.ArgumentTypeError('{} is not a valid number'.format(v))
    if number <= 0:
        raise argparse.ArgumentTypeError('{} must be positive'.format(number))
    return number


if __name__ == '__main__':
    commandline()
