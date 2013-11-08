"""Demonstrate how to use polymaze."""
from shapemaze import Maze, shapes

# these are the various shapes that can be used to create a maze
creators = {'Squares': shapes.Square,
            'Up-Down Triangles': shapes.UpDownTriangle_factory,
            'Hexagons': shapes.Hexagon,
            'OctaDiamonds': shapes.OctaDiamond_factory}

for name, creator in creators.items():
    maze = Maze(creator, vertical_shapes=20, horizontal_shapes=30)
    image = maze.image(1200, 1200)
    image.save('Demo - {}.png'.format(name), 'PNG', **image.info)
    print 'Created a demo maze for {}.'.format(name)
