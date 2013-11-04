import cProfile

from polymaze import polymaze_old


def main():
    cProfile.run('generate_maze_only()')


def generate_maze_and_image():
    maze = polymaze_old.PolyMaze(indexed_polygon_class=polymaze_old.IndexedTriangle)
    image = polymaze_old.image(1200, 1200)

def generate_maze_only():
    maze = polymaze_old.PolyMaze(indexed_polygon_class=polymaze_old.IndexedTriangle)


if __name__ == '__main__':
    main()