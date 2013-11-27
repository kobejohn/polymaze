import argparse
from datetime import datetime

import polymaze as pmz


def commandline():
    parser = _parser()
    args = parser.parse_args()
    # parse all the args
    maker, content = _parse_maker(args)
    shape = pmz.supershapes_dict.get(args.shape)  # None if not provided
    aspect_w, aspect_h = args.aspect_w, args.aspect_h
    complexity = args.complexity
    mazes = _make_mazes(maker, content, shape, complexity, aspect_w, aspect_h)
    _save_mazes(mazes)


def _make_mazes(maker, content, shape, complexity, aspect_w, aspect_h):
    maker_args = (content,) if content else tuple()  # allow nonexistent args
    maze_or_mazes = maker(*maker_args,
                          supershape=shape, complexity=complexity,
                          aspect_w=aspect_w, aspect_h=aspect_h)
    try:
        mazes = tuple(maze_or_mazes)  # if generator --> (maze, maze, ...)
    except TypeError:
        mazes = (maze_or_mazes,)  # if just one maze --> (maze,)
    return mazes


def _save_mazes(mazes):
    clean_now_string = str(datetime.now().time()).replace(':', '.').rsplit('.', 1)[0]
    base_name = 'maze ({})'.format(clean_now_string)
    for i, maze in enumerate(mazes):
        try:
            character, maze = maze  # try to split maze in the case of string
        except TypeError:
            pass
        ss_name = maze._grid.supershape().specification()['name']
        full_name = '{} ({:03} of {:03}) with {}.png' \
                    ''.format(base_name, i+1, len(mazes), ss_name)
        image = maze.image()
        image.save(full_name, 'PNG', **image.info)
        print 'Saved: ' + full_name


def _parse_maker(args):
    """Return the requested mazemaker function and content."""
    if args.string:
        maker = pmz.mazemakers.string
        content = args.string
    else:
        # no maker was specified
        maker = pmz.mazemakers.rectangle
        content = None
    return maker, content


def _parser():
    parser = argparse.ArgumentParser(description='Make and save mazes.')
    # optional top level type of maze to make (default rectangle)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--string',
                       help='Make a maze for each character in STRING.')
    # optional complexity
    parser.add_argument('-c', '--complexity', type=_positive,
                        help='Positive scale for complexity. 1 is easy.')
    # optional shape to use
    ss_names = pmz.supershapes_dict.keys()
    parser.add_argument('--shape', choices=ss_names,
                        help='Make the maze with this shape. Random otherwise.')
    # optional image bounds
    parser.add_argument('-aw', '--aspect_w', type=_positive,
                        help='Relative width of the maze.')
    parser.add_argument('-ah', '--aspect_h', type=_positive,
                        help='Relative height of the maze.')
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
