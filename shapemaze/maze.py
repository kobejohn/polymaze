from collections import deque
import random

import PIL.Image
import PIL.ImageDraw

import shapegrid
import shapes


def demo():
    """Demonstrate how to use polymaze."""
    polymaze = Maze(shapes.up_down_triangle_creator)
    image = polymaze.image(700, 1200)
    image.save('Maze Demo.png', 'PNG', **image.info)
    image.show()


class Maze(object):
    """Generate, manipulate and output a maze based on regular shapes."""
    WALL = 'wall'
    PATH = 'path'

    def __init__(self, shape_creator):
        """Create a maze from a grid of shapes.

        args:
        shape_creator: callable that returns an IndexedShape
        """
        self._grid = shapegrid.ShapeGrid(shape_creator)
        #todo: allow user-centric creation of the grid. this is debug
        # create a debug grid
        rows = 10
        cols = 15
        for row in range(rows):
            for col in range(cols):
                index = (row, col)
                self._grid.create(index)
        # debug create random gaps in the grid
        for i in range(int(round(0.05 * rows * cols))):
            # delete some spaces to see if it still works well
            index = random.randrange(rows), random.randrange(cols)
            self._grid.remove(index)
        # debug remove a corner from the grid
        for row in range(int(round(0.2 * rows))):
            for col in range(int(round(0.2 * cols))):
                self._grid.remove((row, col))
        # create maze and make entrance / exit available
        self._entrance_space, self._exit_space = self._mazify_grid()

    def entrance_space(self):
        return self._entrance_space

    def exit_space(self):
        return self._exit_space

    def _mazify_grid(self):
        """Return entrance and exit spaces after mazifying the internal grid."""
        # Set the edges of all spaces to wall status
        for edge in self._grid.edges():
            setattr(edge, 'status', self.WALL)
        # make an entrance on a border (exit also looks for a border space)
        border_spaces = tuple(self._grid.border_shapes())
        entrance_space = random.choice(border_spaces)
        # break down one border wall to make the entrance
        for n_index, neighbor in entrance_space.neighbors():
            if neighbor is None:
                edge = entrance_space.edge(n_index)
                edge.status = self.PATH
                break  # done after making the exit path
        # setup the path creation mechanism
        current_path = deque()
        current_path.append(entrance_space)
        potential_exit_and_length = (entrance_space, 1)  # long path to border
        # iteratively loop until the algorithm can find no more usable spaces
        # current_path will get longer as it stretches through the maze
        # eventually it will get shorter and come back to zero as the maze
        # fills up
        space = entrance_space
        while current_path:
            # consider all walls leading to new neighbors in random order
            indexed_walls = [(n_index, edge) for n_index, edge in space.edges()
                             if edge.status == self.WALL]
            random.shuffle(indexed_walls)
            for n_index, edge in indexed_walls:
                new_space = self._grid.get(n_index)
                if new_space is None:
                    # no neighbor there
                    continue
                if self._is_pathable(new_space):
                    # pathable new_space ==> keep extending the path
                    edge.status = self.PATH  # break down that wall
                    current_path.append(new_space)  # extend the path stack
                    # track the best potential exit
                    new_len = len(current_path)
                    old_len = potential_exit_and_length[1]
                    if (new_len > old_len) and (new_space in border_spaces):
                        potential_exit_and_length = new_space, new_len
                    # setup for the next iteration
                    space = new_space
                    break  # don't need to check more neighbors
            else:  # after testing and failing all walls for pathability
                # no usable neighbors ==> back up one step
                space = current_path.pop()  # normal case - back up one step
        # when maze complete mark longest path to edge as exit
        exit_space = potential_exit_and_length[0]
        # break down one border wall to make the exit
        for n_index, neighbor in exit_space.neighbors():
            if neighbor is None:
                edge = exit_space.edge(n_index)
                edge.status = self.PATH
                break  # done after making the exit path
        return entrance_space, exit_space

    def _is_pathable(self, new_space):
        """Return True if new_space can be used as a path. False otherwise."""
        for n_index, edge in new_space.edges():
            if edge.status == self.PATH:
                return False  # not a wall - disqualified
        # if it couldn't be disqualified, allow it
        return True

    def image(self, max_height_px, max_width_px):
        """Return a PILLOW image representation of self.

        arguments: max_width/height_px bound the size of the returned image.
        """
        # calculate the size of the final image first in terms of shape points
        all_xy = list()
        for edge in self._grid.edges():
            xy_1, xy_2 = edge.endpoints()
            all_xy.append(xy_1)
            all_xy.append(xy_2)
        x_values, y_values = zip(*all_xy)
        pad_edges = 1
        height_in_shape_edges = max(x_values) - min(x_values) + 2 * pad_edges
        width_in_shape_edges = max(y_values) - min(y_values) + 2 * pad_edges
        # then convert shape sides to pixels based on limiting bound
        edge_ratio = float(height_in_shape_edges) / width_in_shape_edges
        bound_ratio = float(max_height_px) / max_width_px
        if edge_ratio > bound_ratio:
            # height is the limiting boundary
            scale = float(max_height_px) / height_in_shape_edges
        else:
            # width is the limiting boundary (or both are equally limiting)
            scale = float(max_width_px) / width_in_shape_edges
        padding_px = int(round(scale * pad_edges))
        size = (int(round(scale * width_in_shape_edges)),
                int(round(scale * height_in_shape_edges)))
        # create the base image
        white = (255, 255, 255)
        black = (0, 0, 0)
        gray = (128, 128, 128)
        light_red = (255, 128, 128)
        light_green = (128, 255, 128)
        image = PIL.Image.new('RGB', size, gray)
        drawer = PIL.ImageDraw.Draw(image)
        # calculate total offset including padding and centering
        vert_offset_in_edges = -1 * min(x_values)
        horz_offset_in_edges = -1 * min(y_values)
        vert_offset = padding_px + int(round(vert_offset_in_edges * scale))
        horz_offset = padding_px + int(round(horz_offset_in_edges * scale))
        # mark all spaces white before drawing anything else
        for space in self._grid.shapes():
            space_polygon_points = list()
            for _, edge in space.edges():
                (row_a, col_a), _ = edge.endpoints(space.index())
                point_a = (int(round(col_a * scale)) + horz_offset,
                           int(round(row_a * scale)) + vert_offset)
                space_polygon_points.append(point_a)
            drawer.polygon(space_polygon_points, fill=white)
        # mark the entrance and exit before drawing walls
        entrance_polygon_points = list()
        for _, edge in self.entrance_space().edges():
            (row_a, col_a), _ = edge.endpoints(self.entrance_space().index())
            point_a = (int(round(col_a * scale)) + horz_offset,
                       int(round(row_a * scale)) + vert_offset)
            entrance_polygon_points.append(point_a)
        drawer.polygon(entrance_polygon_points, fill=light_red)
        exit_polygon_points = list()
        for _, edge in self.exit_space().edges():
            (row_a, col_a), _ = edge.endpoints(self.exit_space().index())
            point_a = (int(round(col_a * scale)) + horz_offset,
                       int(round(row_a * scale)) + vert_offset)
            exit_polygon_points.append(point_a)
        drawer.polygon(exit_polygon_points, fill=light_green)
        # draw each wall edge and don't draw each path edge
        for edge in self._grid.edges():
            if edge.status == self.WALL:
                (row_a, col_a), (row_b, col_b) = edge.endpoints()
                drawer.line(((int(round(scale * col_a)) + horz_offset,
                              int(round(scale * row_a)) + vert_offset),
                             (int(round(scale * col_b)) + horz_offset,
                              int(round(scale * row_b)) + vert_offset)),
                            fill=black, width=2)
        return image


if __name__ == '__main__':
    demo()
