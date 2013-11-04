class ShapeGrid(object):
    """Sparse grid of shapes."""
    def __init__(self, shape_creator):
        self._shape_creator = shape_creator
        self._shapes = dict()

    def create(self, index):
        """Create (or replace) a shape at index."""
        self._shapes[index] = new_shape = self._shape_creator(self, index)
        return new_shape

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
