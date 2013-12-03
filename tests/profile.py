import cProfile

import polymaze as pmz


preloaded_shape = pmz.SUPERSHAPES_DICT['Hexagon']


def main():
    complex_ = 'make_maze(100)'  # high complexity --> find high-n costs
    simple = 'make_maze(0.5)'  # low complexity --> find fixed costs
    cProfile.run(complex_)


def make_maze(complexity):
    grid = pmz.PolyGrid(complexity=complexity, supershape=preloaded_shape)
    pmz.Maze(grid)

if __name__ == '__main__':
    main()