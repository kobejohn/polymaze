# coding=utf-8
import math
import random

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFilter
import PIL.ImageFont
import PIL.ImageOps

import shapes as _shapes

_SS_DICT = _shapes.supershapes_dict()
_BASE_EDGES = 1000.0
_DEFAULT_COMPLEXITY = 1.0
_DEFAULT_FONT = 'impact.ttf'  # common font with a high surface area
_PIXEL_ON = 0  # PIL color value to indicate a shape should be used (black)
_PIXEL_OFF = 255  # PIL color value to indicate a shape is off (white)


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

    def create_rectangle(self, **kwargs):
        """Create a rectangle of shapes.

        kwargs:
        complexity - scale the difficulty of the maze to any positive number
        aspect - aspect of the grid's graph (not indexes) (height / width)
        """
        # make sure default has a value
        aspect = float(kwargs.pop('aspect', None)
                       or 2.0 / (1 + math.sqrt(5)))  # default golden rect
        # get an exact-aspect ratio and roughly-accurate size rectangle
        rough_ss_edgecount = float(self._supershape.avg_edge_count()) / 2.0
        rough_complexity = kwargs.get('complexity') or _DEFAULT_COMPLEXITY
        rough_edge_count = _BASE_EDGES * rough_complexity  # total edges
        rough_shape_count = float(rough_edge_count) * 2.0 / rough_ss_edgecount
        rough_h = int(round((rough_shape_count * aspect)**0.5))
        rough_w = int(round((float(rough_shape_count) / aspect)**0.5))
        rectangle_image = PIL.Image.new('L', (rough_w, rough_h),
                                        color=_PIXEL_ON)
        self.create_from_image(rectangle_image, **kwargs)

    def create_string(self, string, font_path=None, **kwargs):
        """Create shapes in the form of the provided string.

        kwargs:
        font_path - just file name of any font in resources or full path
        complexity - scale the difficulty of the maze to any positive number
        aspect - aspect of the grid's graph (not indexes) (height / width)
        """
        string_image = _string_image(string, font_path=font_path)
        # cheat. multiply complexity by length of string
        base_complexity = kwargs.get('complexity') or _DEFAULT_COMPLEXITY
        kwargs['complexity'] = len(string) * base_complexity
        # create with the standard image method
        self.create_from_image(string_image, **kwargs)

    def create_from_image(self, image, max_level=None, **kwargs):
        """Create shapes that reproduce the shape of black pixels in image."""
        # provide default
        max_level = max_level or 127  # middle of 8-bit range
        grid_im = self._source_image_to_grid_image(image, **kwargs)
        grid_pixels = grid_im.load()
        width, height = grid_im.size
        for y in range(height):
            for x in range(width):
                if grid_pixels[x, y] <= max_level:
                    self.create((y, x))

    def _source_image_to_grid_image(self, source, complexity=None, aspect=None):
        """Produce shapes to recreate the appearance of dark parts of source."""
        # determine defaults, basic values and shortcuts
        ss = self._supershape  # for brevity
        complexity = complexity or _DEFAULT_COMPLEXITY
        target_aspect = aspect or (float(source.size[1]) / source.size[0])
        ss_h_per_row, ss_w_per_row = ss.graph_offset_per_row()
        ss_h_per_col, ss_w_per_col = ss.graph_offset_per_col()
        # determine the size of the target graph
        edge_count = _BASE_EDGES * complexity  # total edges
        shape_count = float(edge_count) * 2.0 / ss.avg_edge_count()
        target_h = (ss.avg_area() * shape_count * target_aspect)**0.5
        target_w = (float(ss.avg_area() * shape_count) / target_aspect)**0.5
        # determine the approximate size of the grid needed to make the target
        # note: does not include skew - just average w/h
        grid_base_rows = int(round(float(target_h) / ss_h_per_row))
        grid_base_cols = int(round(float(target_w) * ss_w_per_col))
        # resize the source image to the target grid
        # note: done separately from transform to get better quality resize
        grid_base = source.resize((grid_base_cols, grid_base_rows),
                                  PIL.Image.ANTIALIAS)
        # account for skew in the supershape arrangement
        grid_skew_rows_per_col = float(ss_h_per_col) / ss_h_per_row
        grid_skew_cols_per_row = float(ss_w_per_row) / ss_w_per_col
        grid_rows = int(round(grid_base_rows + abs(grid_skew_rows_per_col) * grid_base_cols))
        grid_cols = int(round(grid_base_cols + abs(grid_skew_cols_per_row) * grid_base_rows))
        skew_only_coeffs = (1.0, grid_skew_cols_per_row, 0.0,
                            grid_skew_rows_per_col, 1.0, 0.0)
        # must invert before/after skewing since it fills with black
        grid = PIL.ImageOps.invert(grid_base)
        grid = grid.transform((grid_cols, grid_rows), PIL.Image.AFFINE,
                              skew_only_coeffs, PIL.Image.BICUBIC)
        grid = PIL.ImageOps.invert(grid)
        return grid


def _string_image(string, font_path=None):
    """Return a grayscale image with black characters on a white background."""
    grayscale = 'L'
    large = 1000
    height = 1400  # presumably large enough for any font @ large size
    width = int(round(height * 0.8 * len(string)))
    # make the background
    image = PIL.Image.new(grayscale, (width, height), color=_PIXEL_OFF)
    # draw the text
    draw = PIL.ImageDraw.Draw(image)
    # choose a font
    font_priority = list()
    if font_path:
        # if font path was provided, it might work in three ways
        # 1) path completely defines location of a font
        # 2) just a file name works for a font in the current working directory
        # 3) just a file name works for a font somewhere in the system path
        font_priority.append(font_path)
    #todo: how to list this font for linux? windows automatically looks in fonts
    # always try the default font last
    font_priority.append(_DEFAULT_FONT)
    for font_path in font_priority:
        try:
            font = PIL.ImageFont.truetype(font_path, size=large)
            break  # break when a font works
        except IOError:
            pass
    else:
        # nothing worked. give up and use whatever PIL decides
        font = None
        print 'Unable to find custom or standard font. Using default.'
    draw.text((10, 10), string, fill=_PIXEL_ON, font=font)
    # isolate the text
    c_box = PIL.ImageOps.invert(image).getbbox()
    image = image.crop(c_box)
    return image


if __name__ == '__main__':
    pass
