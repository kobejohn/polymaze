from collections import deque
import random

from .polygrid import PolyViz


class Maze(object):
    """A maze based on a shape pattern."""
    def __init__(self, grid):
        """Create a maze from a grid of shapes."""
        self._grid = grid
        self._viz = PolyViz(self._grid)
        # create styles for the shapes
        self._FLOOR_STYLE = '<< floor >>'
        self._ENTRANCE_STYLE = '<< entrance >>'
        self._EXIT_STYLE = '<< exit >>'
        white = (255, 255, 255, 255)
        light_red = (255, 128, 128, 255)
        light_green = (128, 255, 128, 255)
        self._viz.new_shape_style(self._FLOOR_STYLE, color=white)
        self._viz.new_shape_style(self._ENTRANCE_STYLE, color=light_green)
        self._viz.new_shape_style(self._EXIT_STYLE, color=light_red)
        # create styles for the edges
        self._WALL_STYLE = '<< wall >>'
        self._PATH_STYLE = '<< path >>'
        black = (0, 0, 0, 255)
        transparent = (255, 255, 255, 0)
        self._viz.new_edge_style(self._WALL_STYLE, color=black)
        self._viz.new_edge_style(self._PATH_STYLE, color=transparent)
        self._entrance_exit_pairs = tuple(self._mazify_grid())

    def shape_name(self):
        return self._grid.supershape_name()

    def entrance_exit_pairs(self):
        return self._entrance_exit_pairs

    def _mazify_grid(self):
        """Mazify and generate in/out pairs for each connected set of shapes."""
        # Set the edges of all spaces to wall status
        for edge in self._grid.edges():
            edge.viz_style = self._WALL_STYLE
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
                edge.viz_style = self._PATH_STYLE
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
            # mark the path with the floor style
            space.viz_style = self._FLOOR_STYLE
            # consider all walls leading to new neighbors in random order
            for n_index, edge in space.edges(randomize=True):
                if edge.viz_style != self._WALL_STYLE:
                    continue  # ignore pathed edges. just looking for walls
                new_space = self._grid.get(n_index)
                if new_space is None:
                    # no neighbor there
                    continue
                if not self._has_paths(new_space):
                    # space that hasn't been pathed yet ==> continue the path
                    edge.viz_style = self._PATH_STYLE  # break down that wall
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
                edge.viz_style = self._PATH_STYLE
                break  # done after making the exit path
        # set the special case entrance and exit space styles
        entrance_space.viz_style = self._ENTRANCE_STYLE
        exit_space.viz_style = self._EXIT_STYLE
        return entrance_space, exit_space

    def image(self):
        return self._viz.image()

    def _has_paths(self, new_space):
        """Return True if new_space has any edges as paths. False otherwise."""
        for n_index, edge in new_space.edges():
            if edge.viz_style == self._PATH_STYLE:
                return True  # found at least one wall
        # if it couldn't be disqualified, allow it
        return False


if __name__ == '__main__':
    pass
