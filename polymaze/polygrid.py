import math
import random

import shapes as _shapes

_SS_DICT = _shapes.supershapes_dict()
_BASE_EDGES = 7000.0
_DEFAULT_COMPLEXITY = 1.0


class PolyGrid(object):
    """Sparse grid of shapes."""
    def __init__(self, supershape=None):
        """Create an empty grid.

        kwargs:
        supershape - a supershape class that defines how the maze will look
                     (random if not provided)
        """
        self._shapes = dict()
        self._supershape = supershape or random.choice(_SS_DICT.values())

    def create(self, index):
        """Create (or replace) a shape at index."""
        ss = self._supershape
        self._shapes[index] = new_shape = ss.create_component(self, index)
        return new_shape

    def create_rectangle(self, **kwargs):
        """Create a rectangle of shapes.

        kwargs:
        complexity - scale the difficulty of the maze to any positive number
        aspect - aspect of the grid's graph (not indexes) (height / width)
        """
        rows, cols = _normalize_bounds_to_complexity(self._supershape, **kwargs)
        for row in range(rows):
            for col in range(cols):
                self.create((row, col))

    def create_string(self, string, **kwargs):
        """Create shapes in the form of the provided string.

        kwargs:
        complexity - scale the difficulty of the maze to any positive number
        aspect - aspect of the grid's graph (not indexes) (height / width)
        """
        pass

    def supershape_name(self):
        return self._supershape.name()

    def remove(self, index):
        """Remove the shape at index and remove its link to the grid."""
        # get a reference to the shape or finish if it doesn't exist
        try:
            removed_shape = self._shapes[index]
        except KeyError:
            return  # no shape there, done
        # distribute any owned edges to neighbors
        removed_shape._give_away_edges()
        # remove the shape from the grid
        del(self._shapes[index])
        # remove the grid from the shape
        removed_shape._grid = None

    def get(self, index):
        """Return the shape at index or None if no shape there."""
        try:
            return self._shapes[index]
        except KeyError:
            return None

    def shapes(self):
        """Generate each edge in the map exactly once."""
        for shape in self._shapes.itervalues():
            yield shape

    def edges(self):
        """Generate each edge in the map exactly once."""
        for shape in self._shapes.itervalues():
            for edge in shape._owned_edges.itervalues():
                yield edge

    def border_shapes(self):
        """Generate all shapes on the grid that have at least one open edge."""
        for shape in self._shapes.itervalues():
            for n_index, neighbor in shape.neighbors():
                if neighbor is None:
                    yield shape
                    break  # only yield a shape once


def _normalize_bounds_to_complexity(supershape, complexity=None, aspect=None):
    """Normalize the difficulty of mazes based on number of edges per shape.

    This approach allows the complexity/difficulty of a maze using any shape
    to be similar by having more simple shapes and fewer complex shapes. If
    the number of shapes is standardized instead, the complexity varies greatly
    between shapes with few and many edges.
    """
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # outline:
    #   a) edges
    #       --> adjust base edges for general complexity
    #       --> adjust edges for shape complexity (down for more edges)
    #       --> convert edges to shape count
    #           (tesselation internal shape --> 1 shape per (shape edges)/2
    #   b) y/x ratio --> row/col ratio
    #       --> convert the desired h/w ratio to a row/col ratio
    #           such that the row/col ratio for this supershape will yield
    #           the desired h/w ratio when graphed
    #           start: Ah/Aw = rows*row_offset[0] + cols*col_offset[0]
    #                          -----------------------------------------
    #                          rows*row_offset[1] + cols*col_offset[1]
    #           assume A = Ah/Aw
    #           end: rows/cols = A*col_offset[1] - col_offset[0]
    #                            -------------------------------
    #                            row_offset[0] - A*row_offset[1]
    #   c) combine
    #       --> calculate out how many rows/cols it takes to fill the given
    #           supershape ratio with shape count
    #           start: r * c = shape_count
    #           end: r = sqrt(shape_count * rows_per_col)
    #                c = shapes / r
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # provide defaults
    ss = supershape  # for brevity
    complexity = complexity if complexity is not None else _DEFAULT_COMPLEXITY
    # a) edges
    edge_count = _BASE_EDGES * complexity
    edge_count = float(edge_count) / ss.avg_edge_count()
    shape_count = float(edge_count) * 2.0 / ss.avg_edge_count()
    # b) aspect ratio --> grid ratio
    aspect = aspect or 2.0 / (1 + math.sqrt(5))  # default golden rect
    aspect = float(aspect)
    y_offset_per_col = ss.graph_offset_per_col()[0]
    x_offset_per_col = ss.graph_offset_per_col()[1]
    y_offset_per_row = ss.graph_offset_per_row()[0]
    x_offset_per_row = ss.graph_offset_per_row()[1]
    rows_per_col = ((aspect * x_offset_per_col - y_offset_per_col)
                    / (y_offset_per_row - aspect * x_offset_per_row))
    # c) combine everything
    rows = (shape_count * rows_per_col) ** 0.5
    cols = float(shape_count) / rows
    rows = int(round(rows))
    cols = int(round(cols))
    return rows, cols


if __name__ == '__main__':
    pass
