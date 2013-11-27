import cProfile

import polymaze as pmz


preloaded_shape = pmz.supershapes_dict['Hexagon']


def main():
    complex_ = 'make_maze(100)'
    simple = 'make_maze(0.5)'
    cProfile.run(complex_)


def make_maze(complexity):
    # low complexity --> find fixed costs
    # high complexity --> find high-n costs
    pmz.mazemakers.rectangle(complexity=complexity, supershape=preloaded_shape)


if __name__ == '__main__':
    main()