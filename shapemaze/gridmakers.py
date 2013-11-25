import math
import os

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

import shapegrid as _shapegrid


_BASE_DIR = os.path.dirname(__file__)
_RESOURCE_DIR = os.path.join(_BASE_DIR, 'resources')
_EDGES_PER_COMPLEXITY = 7000.0  # arbitrary tweakable number


def rectangle(supershape=None, complexity=None, aspect_h=None, aspect_w=None):
    grid = _shapegrid.ShapeGrid(supershape=supershape)
    # convert complexity and aspect to index bounds
    rows, cols = _calc_index_bounds(supershape=grid.supershape(),
                                    complexity=complexity,
                                    aspect_h=aspect_h, aspect_w=aspect_w)
    for row in range(rows):
        for col in range(cols):
            grid.create((row, col))
    return grid


def character(c,
              supershape=None, complexity=None, aspect_h=None, aspect_w=None):
    grid = _shapegrid.ShapeGrid(supershape=supershape)
    # get an image of the character
    c_image = _character_image(c)
    # convert complexity and aspect to index bounds
    # extra step: for characters, default aspect is the original image aspect
    if not (aspect_h or aspect_w):
        aspect_w, aspect_h = c_image.size
    rows, cols = _calc_index_bounds(supershape=grid.supershape(),
                                    complexity=complexity,
                                    aspect_h=aspect_h, aspect_w=aspect_w)
    # convert the image to a grid
    return _image_white_to_shapes(c_image, grid, rows, cols)


def _character_image(c):
    """Draw a white character on a black background."""
    black = 0
    white = 255
    # make the background
    image = PIL.Image.new('L', (300, 300), color=black)
    # draw the text
    draw = PIL.ImageDraw.Draw(image)
    # choose a font
    override_font = os.path.join(_RESOURCE_DIR, 'font')  # custom font
    base_font = 'impact.ttf'  # common font with a high surface area
    font_priority = (override_font, base_font)
    for font_path in font_priority:
        try:
            font = PIL.ImageFont.truetype(font_path, 200)
            break  # break when a font works
        except IOError:
            pass
    else:
        font = None
        print 'Unable to find standard or custom font. Using default.'
    draw.text((10, 10), c, fill=white, font=font)
    # isolate the text and return it
    c_box = image.getbbox()
    return image.crop(c_box)


def _image_white_to_shapes(image, grid, rows, cols):
    """Place the image onto the grid at the given size and return the grid."""
    # make sure it is monochrome
    if len(image.getbands()) != 1:
        image = image.convert('L')
    # shrink the image with the required grid aspect (NOT image aspect)
    image = image.resize((cols, rows), resample=PIL.Image.ANTIALIAS)
    # convert to black/white
    threshold = 128
    image = image.point(lambda i: 255 * (i > threshold))
    # get the pixels and build the grid based on each pixel's position and value
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            if pixels[x, y]:
                grid.create((y, x))
    return grid


def _calc_index_bounds(supershape=None, complexity=None,
                       aspect_h=None, aspect_w=None):
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
    complexity = complexity or 1.0
    # a) edges
    edge_count = complexity * _EDGES_PER_COMPLEXITY
    edge_count = float(edge_count) / supershape.avg_edge_count()
    shape_count = float(edge_count) * 2.0 / supershape.avg_edge_count()
    # b) aspect ratio --> grid ratio
    if not (aspect_h or aspect_w):
        # default to golden rectangle if no aspect provided
        aspect_w = (1 + math.sqrt(5))/2
        aspect_h = 1.0
    elif not (aspect_h and aspect_w):
        # square if only one aspect component provided
        aspect_h = aspect_h or aspect_w  # h if available. otherwise same as w
        aspect_w = aspect_w or aspect_h  # w if available. otherwise 1
    else:
        pass  # just use provided aspects if both provided
    aspect_h = float(aspect_h)
    aspect_w = float(aspect_w)
    ss_spec = supershape.specification()
    y_offset_per_col = ss_spec['graph_offset_per_col'][0]
    x_offset_per_col = ss_spec['graph_offset_per_col'][1]
    y_offset_per_row = ss_spec['graph_offset_per_row'][0]
    x_offset_per_row = ss_spec['graph_offset_per_row'][1]
    a = float(aspect_h) / aspect_w
    rows_per_col = ((a * x_offset_per_col - y_offset_per_col)
                    / (y_offset_per_row - a * x_offset_per_row))
    # c) combine everything
    rows = (shape_count * rows_per_col) ** 0.5
    cols = float(shape_count) / rows
    rows = int(round(rows))
    cols = int(round(cols))
    return rows, cols


if __name__ == '__main__':
    pass
