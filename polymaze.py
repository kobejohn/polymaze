import argparse
from datetime import datetime

import polymaze as pmz


def commandline():
    parser = _parser()
    kwargs = vars(parser.parse_args())
    # if provided, replace the supershape name with the object
    ss_name = kwargs.pop('supershape', None)
    if ss_name:
        kwargs['supershape'] = pmz.SUPERSHAPES_DICT[ss_name]
    # if a string was provided, make that the primary definition of the mazes
    string = kwargs.pop('string', None)
    if string is not None:
        mazes = list(_make_string_mazes(string, **kwargs))
    else:
        # rectangle if other grid type not specified
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
    # set complexity or aspect to make sure a grid is produced (not empty)
    default_complexity = 1.0
    kwargs.setdefault('complexity', default_complexity)
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
    parser.add_argument('--complexity', type=_positive,
                        help='Numeric scale for complexity.'
                             ' 0.5 is easy. 100 is WTFImpossible.')
     # optional shape to use
    ss_names = pmz.SUPERSHAPES_DICT.keys()
    parser.add_argument('--shape', dest='supershape', choices=ss_names,
                        help='Make the maze with this shape. Random otherwise.')
    # optional aspect (relative height)
    parser.add_argument('--aspect', type=_positive,
                        help='Set the height/width aspect of the maze.')
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
