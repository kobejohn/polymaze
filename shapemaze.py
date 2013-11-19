import argparse
from datetime import datetime

import shapemaze as _smz


def commandline():
    parser = _make_parser()
    args = parser.parse_args()
    # parse all the args
    maker, content = _parse_maker(args)
    shape = _smz.supershapes_dict.get(args.shape)  # None if no shape
    image_max_w, image_max_h = args.image_max_width, args.image_max_height
    grid_max_w, grid_max_h = args.grid_max_width, args.grid_max_height
    # make the maze
    maker_args = (content,) if content else tuple()
    maker_kwargs = {'supershape': shape,
                    'grid_v_bound': grid_max_h, 'grid_h_bound': grid_max_w}
    maze_or_mazes = maker(*maker_args, **maker_kwargs)
    try:
        mazes = list(maze_or_mazes)  # generator --> [mazes]
    except TypeError:
        mazes = [maze_or_mazes]  # one maze --> [maze]
    # save the maze(s)
    clean_now_string = str(datetime.now()).replace(':', '-').split('.')[0]
    base_name = 'maze {}'.format(clean_now_string)
    for i, maze in enumerate(mazes):
        try:
            character, maze = maze  # try to split maze in the case of string
        except TypeError:
            pass
        full_name = '{} ({:03} of {:03}).png'.format(base_name, i+1, len(mazes))
        image = maze.image(max_height_px=image_max_h, max_width_px=image_max_w)
        image.save(full_name, 'PNG', **image.info)


def _parse_maker(args):
    """Return the requested mazemaker function and content."""
    if args.string:
        maker = _smz.mazemakers.string
        content = args.string
    elif args.rectangle:
        maker = _smz.mazemakers.rectangle
        content = None
    else:
        # no maker was specified
        maker = _smz.mazemakers.rectangle
        content = None
    return maker, content


def _make_parser():
    parser = argparse.ArgumentParser(description='Make and save some mazes.')
    # optional top level type of maze to make
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--string',
                       help='Make a maze for each character in STRING.')
    group.add_argument('--rectangle', action='store_true')
    # optional shape to use
    ss_names = _smz.supershapes_dict.keys()
    parser.add_argument('--shape', choices=ss_names,
                        help='Make the maze with this shape.')
    # optional image bounds
    parser.add_argument('-iw', '--image_max_width', type=_positive_int)
    parser.add_argument('-ih', '--image_max_height', type=_positive_int)
    parser.add_argument('-gw', '--grid_max_width', type=_positive_int)
    parser.add_argument('-gh', '--grid_max_height', type=_positive_int)
    return parser


def _positive_int(v):
    try:
        integer = int(v)
    except Exception:
        raise argparse.ArgumentTypeError('{} is not a valid integer'.format(v))
    if integer <= 0:
        raise argparse.ArgumentTypeError('{} must be positive'.format(v))
    return integer


if __name__ == '__main__':
    commandline()
