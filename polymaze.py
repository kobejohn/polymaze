import argparse
from datetime import datetime

import polymaze as _pmz


def commandline():
    parser = _parser()
    args = parser.parse_args()
    # parse all the args
    maker, content = _parse_maker(args)
    shape = _pmz.supershapes_dict.get(args.shape)  # None if no shape
    aspect_w, aspect_h = args.aspect_width, args.aspect_height
    complexity = args.complexity
    mazes = _make_mazes(maker, content, shape, complexity, aspect_w, aspect_h)
    _save_mazes(mazes)


def _make_mazes(maker, content, shape, complexity, aspect_w, aspect_h):
    maker_args = (content,) if content else tuple()
    maze_or_mazes = maker(*maker_args,
                          supershape=shape, complexity=complexity,
                          aspect_w=aspect_w, aspect_h=aspect_h)
    try:
        mazes = tuple(maze_or_mazes)  # if generator --> (maze, maze, ...)
    except TypeError:
        mazes = (maze_or_mazes,)  # if just one maze --> (maze,)
    return mazes


def _save_mazes(mazes):
    clean_now_string = str(datetime.now()).replace(':', '-').split('.')[0]
    base_name = 'maze {}'.format(clean_now_string)
    for i, maze in enumerate(mazes):
        try:
            character, maze = maze  # try to split maze in the case of string
        except TypeError:
            pass
        full_name = '{} ({:03} of {:03}).png'.format(base_name, i+1, len(mazes))
        image = maze.image()
        image.save(full_name, 'PNG', **image.info)


def _parse_maker(args):
    """Return the requested mazemaker function and content."""
    if args.string:
        maker = _pmz.mazemakers.string
        content = args.string
    elif args.rectangle:
        maker = _pmz.mazemakers.rectangle
        content = None
    else:
        # no maker was specified
        maker = _pmz.mazemakers.rectangle
        content = None
    return maker, content


def _parser():
    parser = argparse.ArgumentParser(description='Make and save some mazes.')
    # optional top level type of maze to make
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--string',
                       help='Make a maze for each character in STRING.')
    group.add_argument('--rectangle', action='store_true')
    # optional shape to use
    ss_names = _pmz.supershapes_dict.keys()
    parser.add_argument('--shape', choices=ss_names,
                        help='Make the maze with this shape. Random otherwise.')
    # optional image bounds
    parser.add_argument('-aw', '--aspect_width', type=_positive,
                        help='Relative width of the maze.')
    parser.add_argument('-ah', '--aspect_height', type=_positive,
                        help='Relative height of the maze.')
    parser.add_argument('-c', '--complexity', type=_positive,
                        help='Positive scale for complexity. 1 is easy.')
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
