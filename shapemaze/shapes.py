def composite_x_factory(index):
    """Return the appropriate shape for the given index."""
    # probably reduce index with % composite_row_size % composite col size?
    # then simple dict that describes the composite shape?
    pass


class IndexedShapeBase(object):
    """A shape that fits by index into a grid of other shapes."""

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Begin Implementation requirements

    def _identify_and_sort_neighbors(self):
        """Return a dict identifying each neighbor with a semantic edge name
        and a tuple indicating the clockwise order of the edges.

        return: ({neighbor_index: semantic_name, ...},
                 ('semantic_name1', 'semantic_name2', ...))
        """
        raise NotImplementedError

    def _calc_edge_endpoints(self):
        """Return a dict identifying the end points for the edge between
        self and each neighbor.

        return: {neighbor_index: (float_yx, float_yx), ...}

        Note regarding units:
            All shapes in grid must agree on the units of the point values.
            If all shapes have the same edge length, that's a good unit value.
        """
        raise NotImplementedError

    # End implementation requirements
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, grid, index):
        self._grid = grid
        self._index = index
        edge_names, clockwise_indexes = self._identify_and_sort_neighbors()
        self._edge_names = edge_names
        self._neighbor_indexes = clockwise_indexes
        self._edge_endpoints = self._calc_edge_endpoints()
        self._owned_edges = dict()
        self._grab_edges()

    def index(self):
        return self._index

    def neighbors(self):
        """Generate each index-neighbor pair for this shape.

        Neighbor is None for nonexistent neighbors.
        """
        for n_index in self._neighbor_indexes:
            yield n_index, self._grid.get(n_index)

    def edges(self):
        """Generate each index-edge pair for this shape."""
        for n_index in self._neighbor_indexes:
            edge = self.edge(n_index)
            yield n_index, edge

    def edge(self, neighbor_index):
        """Return one edge of this shape by the index of the sharing neighbor.

        Note:
        When an edge is shared, both shapes will return the same edge.
        """
        # try to get from self
        try:
            return self._owned_edges[neighbor_index]
        except KeyError:
            pass
        # get from neighbor
        neighbor = self._grid.get(neighbor_index)
        if neighbor:
            # neighbor stores the shared edge under this shape's index
            return neighbor._owned_edges[self.index()]

    def _grab_edges(self):
        """Return a dict of new edges for ONLY those that don't exist yet.

        return: {neighbor_index: edge, ...}
        """
        grabbed_edges = dict()
        for n_index, neighbor in self.neighbors():
            # not strictly necessary so removed
            ## ignore self owned edges
            #if n_index in self._owned_edges:
            #    continue
            # ignore neighbor owned edges
            if neighbor:
                if self.index() in neighbor._owned_edges:
                    continue
            # create edges that didn't exist in self or neighbor
            grabbed_edges[n_index] = Edge(self._grid, self.index(), n_index)
        self._owned_edges.update(grabbed_edges)

    def _give_away_edges(self):
        """Give edges away to neighbors or keep them if no neighbor."""
        for n_index, edge in self._owned_edges.items():
            neighbor = self._grid.get(n_index)
            if neighbor:
                # transfer the edge only when there is a neighbor
                neighbor._owned_edges[self.index()] = edge
                del self._owned_edges[n_index]


class Square(IndexedShapeBase):
    """A square that fits by index into a regular grid of squares."""

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Begin Implementation requirements
    def _identify_and_sort_neighbors(self):
        """Implements base class requirements."""
        row, col = self.index()
        top, bottom, left, right = ((row - 1, col),
                                    (row + 1, col),
                                    (row, col - 1),
                                    (row, col + 1))
        return ({top: 'top', right: 'right', bottom: 'bottom', left: 'left'},
                (top, right, bottom, left))

    def _calc_edge_endpoints(self):
        """Implements base class requirements."""
        row, col = self.index()
        # shared side coordinates
        top = float(row)
        bottom = float(row + 1)
        left = float(col)
        right = float(col + 1)
        # point coordinates
        top_left = (top, left)
        top_right = (top, right)
        bottom_left = (bottom, left)
        bottom_right = (bottom, right)
        # paired points per edge
        named_lookup = {'top': (top_left, top_right),
                        'right': (top_right, bottom_right),
                        'bottom': (bottom_right, bottom_left),
                        'left': (bottom_left, top_left)}
        edge_endpoints = {n_index: named_lookup[n_name] for n_index, n_name
                          in self._edge_names.items()}
        return edge_endpoints

    # End implementation requirements
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Edge(object):
    def __init__(self, grid, neighbor_1_index, neighbor_2_index):
        self._grid = grid
        self._neighbor_1_index = neighbor_1_index
        self._neighbor_2_index = neighbor_2_index

    def endpoints(self, requesting_shape_index=None):
        """Return the xy, xy end points of this edge.

        kwargs: requesting_shape_index - if the clockwise order of vertices is
                    desired, provide this so the edge knows which way to sort
        """
        # default if the sorting doesn't matter
        if requesting_shape_index is None:
            # use neighbor_1 UNLESS it doesn't exist in the grid
            requesting_shape_index = self._neighbor_1_index
            requesting_shape = self._grid.get(requesting_shape_index)
            if requesting_shape is None:
                requesting_shape_index = self._neighbor_2_index
        if requesting_shape_index == self._neighbor_1_index:
            n_index = self._neighbor_2_index
        elif requesting_shape_index == self._neighbor_2_index:
            n_index = self._neighbor_1_index
        else:
            raise ValueError('The requesting shape is not one of the sharing'
                             ' neighbors of this edge.')
        return self._grid.get(requesting_shape_index)._edge_endpoints[n_index]
