#! /usr/bin/python
import argparse
from datetime import datetime
import sys

import PIL.Image

from .polygrid import PolyGrid
from .shapes import supershapes_dict
from .maze import Maze


ss_dict = supershapes_dict()


def commandline():
    parser = _parser()
    kwargs = vars(parser.parse_args())
    # setup the base grid with a supershape if provided
    grid = PolyGrid(supershape=ss_dict.get(kwargs.pop('shape'), None))

    # pull off non-common parameters
    text = kwargs.pop('text')
    if text is not None:
        text = text.decode(sys.stdin.encoding)
    image_path = kwargs.pop('image')
    if image_path is not None:
        image_path = image_path.decode(sys.stdin.encoding)
    font_path = kwargs.pop('font')
    if font_path is not None:
        font_path = font_path.decode(sys.stdin.encoding)
    filename = kwargs.pop('output')
    if filename is not None:
        filename = filename.decode(sys.stdin.encoding)

    # fill the grid and create maze based on the remaining arguments provided
    if text:
        grid.create_string(text, font_path=font_path, **kwargs)
        maze_type = 'Text'
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
            filename = '{} - {} made with {}'.format(clean_now_string,
                                                     maze_type,
                                                     maze.shape_name())
        # force png... for your own good! png works well with this type
        # of image, lossless AND smaller file size than jpg.
        # If this is ever updated to work with original images remaining
        # in the background of the maze, then jpg might make sense.
        filename += '.png'
        image.save(filename)
        print(u'Saved {}'.format(filename))


def _parser():
    parser = argparse.ArgumentParser(description='Make and save mazes.')
    # optional top level type of maze to make (default rectangle)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-t', '--text',
                       help='Make a maze inside the characters of TEXT.'
                            ' Note: interprets "\\n" as a new line.')
    group.add_argument('-i', '--image',
                       help='Make a maze from IMAGE (path).')
    # optional complexity
    parser.add_argument('-c', '--complexity', type=_positive,
                        help='Positive number that controls maze complexity.'
                             ' For example: 0.5 is very easy. 110 is very hard.')
     # optional shape to use
    ss_names = ss_dict.keys()
    parser.add_argument('-s', '--shape', choices=ss_names,
                        help='Make the maze with this shape. Random otherwise.')
    # optional aspect (relative height)
    parser.add_argument('-a', '--aspect', type=_positive,
                        help='Set the height/width aspect of the maze.')
    parser.add_argument('-f', '--font', type=str,
                        help='Provide a font path for text mazes.')
    parser.add_argument('-o', '--output', type=str,
                        help='Output filename. The format will always be PNG.')
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
