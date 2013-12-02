import argparse
from datetime import datetime

import polymaze as pmz


def commandline():
    parser = _parser()
    kwargs = vars(parser.parse_args())
    # if a string was provided, make that the primary definition of the mazes
    string = kwargs.pop('string', None)
    if string is not None:
        mazes = list(_make_string_mazes(string, **kwargs))
    else:
        mazes = [_make_rectangle_maze(**kwargs)]
    # whatever was produced, save it
    _save_mazes(mazes)


def _make_string_mazes(string, **kwargs):
    """Generate a maze for each non-whitespace character in string."""
    print 'Making character mazes: ',  # print results on one line
    for c in string:
        c_image = pmz.character_image(c)
        grid = pmz.PolyGrid(image=c_image, **kwargs)
        print c,  # continue results on the same line
        yield pmz.Maze(grid)


def _make_rectangle_maze(**kwargs):
    """Return a rectangular maze."""
    if all(v is None for v in kwargs.values()):
        # if no args provided, set at least one. otherwise just get empty grid
        kwargs['complexity'] = 1
    return pmz.Maze(pmz.PolyGrid(**kwargs))


def _save_mazes(mazes):
    now_str = str(datetime.now().time())
    clean_now_string = now_str.replace(':', '.').rsplit('.', 1)[0]
    base_name = 'maze ({})'.format(clean_now_string)
    print 'Saving {} maze image(s)...'.format(len(mazes))
    for i, maze in enumerate(mazes):
        try:
            character, maze = maze  # try to split maze in case of characters
        except TypeError:
            pass
        ss_name = maze.shape_name()
        full_name = '{} ({:03} of {:03}) with {}.png' \
                    ''.format(base_name, i+1, len(mazes), ss_name)
        image = maze.image()
        if image:
            # if there is actually an image, produce it
            image.save(full_name, 'PNG', **image.info)
            print '    Saved {}'.format(full_name)
        else:
            print '    This maze appears to be empty. Not saving.'


def _parser():
    parser = argparse.ArgumentParser(description='Make and save mazes.')
    # optional top level type of maze to make (default rectangle)
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--string',
                       help='Make a maze for each character in STRING.')
    # optional complexity
    parser.add_argument('-c', '--complexity', type=_positive,
                        help='Numeric scale for complexity.'
                             ' 0.5 is easy. 100 is WTFImpossible.')
     # optional shape to use
    ss_names = pmz.supershapes_dict.keys()
    parser.add_argument('--shape', dest='supershape', choices=ss_names,
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
