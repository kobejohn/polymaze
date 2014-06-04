import argparse
from datetime import datetime

import PIL.Image

import polymaze as pmz


def commandline():
    parser = _parser()
    kwargs = vars(parser.parse_args())
    # setup the base grid with a supershape if provided
    ss_name = kwargs.pop('shape')
    if ss_name:
        supershape = pmz.SUPERSHAPES_DICT[ss_name]
    else:
        supershape = None
    grid = pmz.PolyGrid(supershape=supershape)
    # pull off non-common parameters
    string = kwargs.pop('string')
    image_path = kwargs.pop('image')
    font_path = kwargs.pop('font')

    # fill the grid and create maze based on the remaining arguments provided
    if string:
        grid.create_string(string, font_path=font_path, **kwargs)
        maze = pmz.Maze(grid)
        save_maze(maze, 'String')
    elif image_path:
        image = PIL.Image.open(image_path).convert('L')
        if not image:
            print('Unable to open the provided image path: {}'
                  ''.format(image_path))
        grid.create_from_image(image, **kwargs)
        maze = pmz.Maze(grid)
        save_maze(maze, 'Image')
    else:
        grid.create_rectangle(**kwargs)
        maze = pmz.Maze(grid)
        save_maze(maze, 'Rectangle')


def save_maze(maze, maze_type):
    image = maze.image()
    if image is None:
        print 'This maze appears to be empty. Not saving.'
    else:
        now_str = str(datetime.now().time())
        clean_now_string = now_str.replace(':', '.').rsplit('.', 1)[0]
        filename = '{} - {} made with {}.png'.format(clean_now_string,
                                                     maze_type,
                                                     maze.shape_name())
        image.save(filename, format='PNG')
        print filename


def _parser():
    parser = argparse.ArgumentParser(description='Make and save mazes.')
    # optional top level type of maze to make (default rectangle)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--string',
                       help='Make a maze for each character in STRING.')
    group.add_argument('--image',
                       help='Make a maze from IMAGE (path).')
    # optional complexity
    parser.add_argument('--complexity', type=_positive,
                        help='Numeric scale for complexity.'
                             ' 0.5 is easy. 100 is WTFImpossible.')
     # optional shape to use
    ss_names = pmz.SUPERSHAPES_DICT.keys()
    parser.add_argument('--shape', choices=ss_names,
                        help='Make the maze with this shape. Random otherwise.')
    # optional aspect (relative height)
    parser.add_argument('--aspect', type=_positive,
                        help='Set the height/width aspect of the maze.')
    parser.add_argument('--font', type=str,
                        help='Provide a font name/path for string mazes.')
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
