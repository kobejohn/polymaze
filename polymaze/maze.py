from collections import deque
import random

import PIL.Image
import PIL.ImageDraw


class Maze(object):
    """A maze based on a shape pattern."""
    WALL = 'wall'
    PATH = 'path'
    PX_PER_GRAPH_UNIT = 40.0  # tweakable. higher makes higher resolution images

    def __init__(self, grid):
        """Create a maze from a grid of shapes."""
        self._grid = grid
        self._entrance_exit_pairs = tuple(self._mazify_grid())

    def entrance_exit_pairs(self):
        return self._entrance_exit_pairs

    def _mazify_grid(self):
        """Mazify and generate in/out pairs for each connected set of shapes."""
        # Set the edges of all spaces to wall status
        for edge in self._grid.edges():
            setattr(edge, 'status', self.WALL)
        # get a list of all border shapes which is useful in several places
        border_spaces = deque(self._grid.border_shapes())
        random.shuffle(border_spaces)  # randomize to remove patterns
        # Loop to ensure that a maze is created for each area of
        # connected shapes (except single shapes which occur on borders often).
        while border_spaces:
            border_space = border_spaces.pop()
            if all(neighbor is None for n_index, neighbor
                   in border_space.neighbors()):
                # eliminate isolated single shapes
                self._grid.remove(border_space.index())
                continue
            elif self._has_paths(border_space):
                # this space has already been pathed as part of a maze so ignore
                continue
            else:
                pass  # couldn't eliminate this border so need to make a maze
            entrance_exit = self._mazify_connected_shapes(border_space,
                                                          border_spaces)
            yield entrance_exit

    def _mazify_connected_shapes(self, entrance_space, border_spaces):
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
                if not self._has_paths(new_space):
                    # space that hasn't been pathed yet ==> continue the path
                    edge.status = self.PATH  # break down that wall
                    # track the best potential exit
                    new_len = len(current_path)
                    old_len = potential_exit_and_length[1]
                    if (new_len > old_len) and (new_space in border_spaces):
                        potential_exit_and_length = new_space, new_len
                    # put self back on the stack to be considered on the
                    # return trip (may have remaining edges
                    current_path.append(space)
                    # setup for the next iteration
                    current_path.append(new_space)  # extend the path stack
                    space = new_space
                    break  # don't need to check more neighbors for now
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

    def image(self, w_limit=None, h_limit=None):
        """Return a PIL(LOW) image representation of self.

        arguments: max_width/height_px bound the size of the returned image.
        """
        # first calculate the graph size of the final image
        x_values, y_values = list(), list()
        for edge in self._grid.edges():
            (y1, x1), (y2, x2) = edge.endpoints()
            x_values.extend((x1, x2))
            y_values.extend((y1, y2))
        image_padding_in_edges = 1.0
        graph_height = max(y_values) - min(y_values) + 2*image_padding_in_edges
        graph_width = max(x_values) - min(x_values) + 2*image_padding_in_edges
        # handle graph --> image scaling reasonably
        scale = float(self.PX_PER_GRAPH_UNIT)  # default scale for no limits
        if h_limit and w_limit:
            # scaling: both limits provided --> scale to the more limiting one
            graph_relative_height = float(graph_height) / graph_width
            relative_height_limit = float(h_limit) / w_limit
            if graph_relative_height > relative_height_limit:
                scale = float(h_limit) / graph_height  # height bound
            else:
                scale = float(w_limit) / graph_width  # width bound
        elif h_limit or w_limit:
            # scaling: one limit provided --> scale to the provided limit
            if h_limit:
                scale = float(h_limit) / graph_height  # height bound
            else:
                scale = float(w_limit) / graph_width  # width bound
        # pad the image
        size = (int(round(scale * graph_width)),
                int(round(scale * graph_height)))
        # create the base image
        white = (255, 255, 255)
        black = (0, 0, 0)
        light_red = (255, 128, 128)
        light_green = (128, 255, 128)
        image = PIL.Image.new('RGBA', size)
        drawer = PIL.ImageDraw.Draw(image)
        # calculate total offset including padding and centering
        vert_offset_in_edges = min(y_values)
        horz_offset_in_edges = min(x_values)
        vert_offset_px = int(round((image_padding_in_edges
                                    - vert_offset_in_edges) * scale))
        horz_offset_px = int(round((image_padding_in_edges
                                    - horz_offset_in_edges) * scale))
        # mark all spaces white before drawing anything else
        for space in self._grid.shapes():
            space_polygon_points = list()
            for _, edge in space.edges():
                (row_a, col_a), _ = edge.endpoints(space.index())
                point_a = (int(round(col_a * scale)) + horz_offset_px,
                           int(round(row_a * scale)) + vert_offset_px)
                space_polygon_points.append(point_a)
            drawer.polygon(space_polygon_points, fill=white)
        # mark entrances and exits before drawing walls
        for entrance, exit in self.entrance_exit_pairs():
            entrance_polygon_points = list()
            for _, edge in entrance.edges():
                (row_a, col_a), _ = edge.endpoints(entrance.index())
                point_a = (int(round(col_a * scale)) + horz_offset_px,
                           int(round(row_a * scale)) + vert_offset_px)
                entrance_polygon_points.append(point_a)
            drawer.polygon(entrance_polygon_points, fill=light_red)
            exit_polygon_points = list()
            for _, edge in exit.edges():
                (row_a, col_a), _ = edge.endpoints(exit.index())
                point_a = (int(round(col_a * scale)) + horz_offset_px,
                           int(round(row_a * scale)) + vert_offset_px)
                exit_polygon_points.append(point_a)
            drawer.polygon(exit_polygon_points, fill=light_green)
        # draw each wall edge and don't draw each path edge
        for edge in self._grid.edges():
            if edge.status == self.WALL:
                (row_a, col_a), (row_b, col_b) = edge.endpoints()
                drawer.line(((int(round(scale * col_a)) + horz_offset_px,
                              int(round(scale * row_a)) + vert_offset_px),
                             (int(round(scale * col_b)) + horz_offset_px,
                              int(round(scale * row_b)) + vert_offset_px)),
                            fill=black, width=4)
        return image

    def _has_paths(self, new_space):
        """Return True if new_space has any edges as paths. False otherwise."""
        for n_index, edge in new_space.edges():
            if edge.status == self.PATH:
                return True  # found at least one wall
        # if it couldn't be disqualified, allow it
        return False


if __name__ == '__main__':
    pass
