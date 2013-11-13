"""Demonstrate how to use polymaze."""
from shapemaze import Maze, shapes

# these are the various shapes that can be used to create a maze
for name, supershape in shapes.supershapes():
    maze = Maze(supershape, vertical_shapes=30, horizontal_shapes=60)
    image = maze.image(1200, 1200)
    image.save('Demo - {}.png'.format(name), 'PNG', **image.info)
    print 'Created a demo maze for {}.'.format(name)
