from collections import deque
import math
import random

import PIL.Image
import PIL.ImageDraw


def main():
    """Demonstrate how to use polymaze."""
    polymaze = PolyMaze()
    image = polymaze.image(600, 1100)
    image.save('polymaze demo.png', 'PNG', **image.info)
    image.show()


class PolyMaze(object):
    """Generate, manipulate and output mazes based on various polygons."""
    WALL = 'wall'
    PATH = 'path'

    def __init__(self):
        #todo: allow selection of type
        self._map = PolygonMap(IndexedTriangle)
        #todo: allow user-centric creation of the grid. this is debug
        for row in range(20):
            for col in range(30):
                index = (row, col)
                self._map.create_polygon(index)
        # create maze and make entrance / exit available
        self.entrance_space, self.exit_space = self._mazify_map(self._map)

    def image(self, max_height_px, max_width_px):
        """Return a PILLOW image representation of self.

        arguments: max_width/height_px bound the size of the returned image.
        """
        # calculate the size of the final image first in terms of polygon sides
        rows = [i[0] for i in self._map.all_indexes()]  # todo: better way to unzip?
        cols = [i[1] for i in self._map.all_indexes()]  # todo: better way to unzip?
        row_scale, col_scale = self._map._polygon_class.SIDES_PER_INDEX
        height_in_poly_edges = row_scale * (max(rows) - min(rows) + 1.1)
        width_in_poly_edges = col_scale * (max(cols) - min(cols) + 2.1)
        # then convert polygon sides to pixels based on limiting bound
        edge_ratio = float(height_in_poly_edges) / width_in_poly_edges
        bound_ratio = float(max_height_px) / max_width_px
        if edge_ratio > bound_ratio:
            # height is the limiting boundary
            scale = float(max_height_px) / height_in_poly_edges
        else:
            # width is the limiting boundary (or both are equally limiting)
            scale = float(max_width_px) / width_in_poly_edges
        size = (int(round(scale * width_in_poly_edges)),
                int(round(scale * height_in_poly_edges)))
        # create the base image
        white = (255, 255, 255)
        black = (0, 0, 0)
        light_red = (255, 128, 128)
        light_green = (128, 255, 128)
        image = PIL.Image.new('RGB', size, white)
        drawer = PIL.ImageDraw.Draw(image)
        # mark the entrance and exit before drawing walls
        entrance_polygon = list()
        for edge, _ in self.entrance_space.edges_and_neighbors():
            (row_a, col_a), (row_b, col_b) = edge.points()
            point_a = (int(round(col_a * scale)), int(round(row_a * scale)))
            point_b = (int(round(col_b * scale)), int(round(row_b * scale)))
            if point_a not in entrance_polygon:
                entrance_polygon.append(point_a)
            if point_b not in entrance_polygon:
                entrance_polygon.append(point_b)
        drawer.polygon(entrance_polygon, fill=light_red)
        exit_polygon = list()
        for edge, _ in self.exit_space.edges_and_neighbors():
            (row_a, col_a), (row_b, col_b) = edge.points()
            point_a = (int(round(col_a * scale)), int(round(row_a * scale)))
            point_b = (int(round(col_b * scale)), int(round(row_b * scale)))
            if point_a not in exit_polygon:
                exit_polygon.append(point_a)
            if point_b not in entrance_polygon:
                exit_polygon.append(point_b)
        drawer.polygon(exit_polygon, fill=light_green)
        # draw each wall edge and don't draw each path edge
        for edge in self._map.all_edges():
            if edge.status == self.WALL:
                (row_a, col_a), (row_b, col_b) = edge.points()
                drawer.line(((int(round(scale * col_a)),
                              int(round(scale * row_a))),
                             (int(round(scale * col_b)),
                              int(round(scale * row_b)))),
                            fill=black)
        return image

    def _mazify_map(self, _map):
        """Return entrance and exit spaces after mazifying the polygon map."""
        # create/set the edges of all spaces to wall status
        for edge in _map.all_edges():
            setattr(edge, 'status', self.WALL)
        # entrance and exit both use border spaces
        border_spaces = tuple(self._map.border_polygons())
        entrance = random.choice(border_spaces)
        # setup the path creation mechanism
        current_path = deque()
        current_path.append(entrance)
        potential_exit_and_length = (entrance, 1)  # longest path to a border
        # iteratively loop until the algorithm can find no more usable spaces
        # current_path will get longer as it stretches through the maze
        # eventually it will get shorter and come back to zero as the maze
        # fills up
        space = entrance
        while current_path:
            # consider all walls leading to new neighbors
            edges_with_neighbors = [(e, n) for e, n
                                    in space.edges_and_neighbors()
                                    if n and (e.status == self.WALL)]
            random.shuffle(edges_with_neighbors)
            for edge, new_space in edges_with_neighbors:
                if self._is_pathable(new_space, space):
                    # pathable neighbor ==> keep extending the path
                    edge.status = self.PATH  # break down that wall
                    current_path.append(new_space)  # extend the path stack
                    # track the best potential exit
                    new_len = len(current_path)
                    old_len = potential_exit_and_length[1]
                    if (new_len > old_len) and (new_space in border_spaces):
                        potential_exit_and_length = (new_space, new_len)
                    # setup for the next iteration
                    space = new_space
                    break  # don't need to check more neighbors
            else:
                # no usable neighbors ==> back up one step
                space = current_path.pop()  # normal case - back up one step
        # when maze complete mark longest path to edge as exit
        _exit = potential_exit_and_length[0]
        # break one wall to a border for the entrance and exit
        for edge, neighbor in entrance.edges_and_neighbors():
            if not neighbor:
                edge.status = self.PATH
                break
        for edge, neighbor in _exit.edges_and_neighbors():
            if not neighbor:
                edge.status = self.PATH
                break
        return entrance, _exit

    def _is_pathable(self, new_space, previous_space):
        """Return True if new_space can be used as a path. False otherwise."""
        # ignoring the previous_space, all edges must be walls to qualify
        for edge, neighbor in new_space.edges_and_neighbors():
            if neighbor is previous_space:
                continue  # ignore the previous_space we came from
            if edge.status == self.PATH:
                return False  # not a wall - disqualified
        # if it couldn't be disqualified, allow it
        return True


class PolygonMap(object):
    """A container map of IndexedPolygons."""
    def __init__(self, polygon_class):
        self._map = dict()  # polygons are indexed here
        self._polygon_class = polygon_class

    def create_polygon(self, index):
        """Create and store a polygon at the given index."""
        p = self._polygon_class(self, index)
        self._map[index] = p
        return p

    def get_polygon(self, index):
        """Return polygon at index or None if nothing there."""
        try:
            return self._map[index]
        except KeyError:
            return None

    def all_indexes(self):
        """Generate all indexes in the map exactly once."""
        for key in self._map:
            yield key

    def all_edges(self):
        """Generate all edges in the map exactly once."""
        for polygon in self._map.values():
            for edge in polygon._owned_edges.values():
                yield edge

    def border_polygons(self):
        """Generate all polygons on the map that have at least one open edge."""
        for polygon in self._map.values():
            for edge_name in polygon.EDGE_NAMES:
                neighbor, _ = polygon.neighbor(edge_name)
                if not neighbor:
                    yield polygon  # had an empty neighbor so qualifies
                    break  # only yield a polygon once


class IndexedPolygonBase(object):
    """Polygon that is located by index within a regular map of polygons."""
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Begin implementation requirements for specific polygons:
    #
    EDGE_NAMES = tuple()  # sequence of keys for identifying polygon edges
    SIDES_PER_INDEX = tuple()  # average sides/index (e.g. (1, 1) for a square)

    def _neighbor_index_by_edge(self, edge_name):
        """Return the index of the neighbor sharing the edge."""
        raise NotImplementedError

    def _shared_edge_lookup(self, edge_name):
        """Return the neighbors name for a shared edge."""
        raise NotImplementedError

    def _edge_end_points(self, edge_name):
        """Return a pair of realized coordinate tuples for edge end points."""
        raise NotImplementedError
    #
    # End parts to be implemented for specific polygons
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, _map, index):
        """Create a new polygon.

        index: Immutable that identifies this polygon relative to others.
               For example, (row, col)
        """
        # keep own identity in the map
        self._map = _map
        self._index = index
        self._owned_edges = dict()
        self._grab_edges(self._owned_edges)  # greedy ownership of edges

    def index(self):
        """Read-only index that locates this polygon in a map."""
        return self._index

    def map(self):
        """Read-only reference to the containing map."""
        return self._map

    def _grab_edges(self, ownership_dict_to_fill):
        """Check each edge of self, consequently creating edges as  need."""
        for edge_name in self.EDGE_NAMES:
            try:
                # if this succeeds, edge is already owned. ignore it.
                self.edge(edge_name)
            except KeyError:
                # it doesn't exist yet so create it and own it
                edge = Edge(self, edge_name)
                ownership_dict_to_fill[edge_name] = edge

    def edges_and_neighbors(self):
        """Generate each (edge, neighbor) for self.

        Edges that have no neighbors return (edge, None).
        """
        for edge_name in self.EDGE_NAMES:
            edge = self.edge(edge_name)
            neighbor, _ = self.neighbor(edge_name)  # neighbor may be None
            yield edge, neighbor

    def edge(self, edge_name):
        """Return one edge of this polygon by name.

        When an edge is shared, both shapes will return the same edge.
        """
        # try to get from self
        try:
            return self._owned_edges[edge_name]
        except KeyError:
            pass
        # get from neighbor
        neighbor, shared_edge_name = self.neighbor(edge_name)
        if neighbor:
            return neighbor._owned_edges[shared_edge_name]
        raise KeyError('{} edge was found in neither self ({}) nor neighbor'
                       ' (if any).'.format(edge_name, self.index()))

    def neighbor(self, edge_name):
        """Return the neighbor and shared name for a given edge.

        Returns: (neighbor, neighbor's name for the shared edge)
             or: (None, name) when there is no neighbor on that edge.
        """
        neighbor_index = self._neighbor_index_by_edge(edge_name)
        neighbor = self._map.get_polygon(neighbor_index)
        shared_edge_name = self._shared_edge_lookup(edge_name)
        return neighbor, shared_edge_name


#todo: urgh... doesn't look nice, but provides logical access to points
class Edge(object):
    """An edge with two end points."""
    def __init__(self, parent_polygon, parent_edge_name):
        self._parent_polygon = parent_polygon
        self._parent_edge_name = parent_edge_name

    def points(self):
        """Return a pair of realized coordinate tuples for edge end points."""
        return self._parent_polygon._edge_end_points(self._parent_edge_name)


class IndexedTriangle(IndexedPolygonBase):
    """Specific type of indexed polygon for use in a PolygonMap."""
    LEFT = 'left'
    RIGHT = 'right'
    MIDDLE = 'middle'

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Begin Implementation of base polygon requirements
    #
    EDGE_NAMES = (LEFT, RIGHT, MIDDLE)
    # for equilateral triangles in a row pointing up and down:
    # sides per row is exactly sin(60 deg)
    # sides per col is exactly 1/2
    SIDES_PER_INDEX = (math.sin(math.radians(60)), 0.5)

    def _neighbor_index_by_edge(self, edge_name):
        """Return the index of the neighbor sharing the edge."""
        row, col = self.index()
        # odd column --> triangle base is up (down for even)
        # therefore: left (no change), right (no change),
        #            middle odd column (-1/up)
        #            middle even column (+1/down)
        odd = True if (row + col) % 2 else False  # get a semantic boolean
        neighbor_row = {self.LEFT: row,
                        self.RIGHT: row,
                        self.MIDDLE: row - 1 if odd else row + 1}[edge_name]
        # column is simple: left (-1), middle (no change), right (+1)
        neighbor_col = {self.LEFT: col - 1,
                        self.RIGHT: col + 1,
                        self.MIDDLE: col}[edge_name]
        neighbor_index = (neighbor_row, neighbor_col)
        return neighbor_index

    def _shared_edge_lookup(self, edge_name):
        """Return the neighbors name for a shared edge."""
        return {self.LEFT: self.RIGHT,
                self.RIGHT: self.LEFT,
                self.MIDDLE: self.MIDDLE}[edge_name]

    def _edge_end_points(self, edge_name):
        """Return a pair of realized coordinate tuples for edge end points."""
        row, col = self.index()
        row_size, col_size = self.SIDES_PER_INDEX
        # tood: a lot of unnecessary calculation... fix it when it's an issue
        even_left_point = (row_size * (row + 1), col_size * col)
        odd_left_point = (row_size * row, col_size * col)
        even_middle_point = (row_size * row, col_size * (col + 1))
        odd_middle_point = (row_size * (row + 1), col_size * (col + 1))
        even_right_point = (row_size * (row + 1), col_size * (col + 2))
        odd_right_point = (row_size * row, col_size * (col + 2))
        even_index_lookup = {self.LEFT: (even_left_point, even_middle_point),
                             self.MIDDLE: (even_left_point, even_right_point),
                             self.RIGHT: (even_middle_point, even_right_point)}
        odd_index_lookup = {self.LEFT: (odd_left_point, odd_middle_point),
                            self.MIDDLE: (odd_left_point, odd_right_point),
                            self.RIGHT: (odd_middle_point, odd_right_point)}
        # lookup the right corners
        odd = True if (row + col) % 2 else False  # get a semantic boolean
        if odd:
            return odd_index_lookup[edge_name]
        else:
            return even_index_lookup[edge_name]
    #
    # End implementation of base polygon requirements
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


if __name__ == '__main__':
    main()