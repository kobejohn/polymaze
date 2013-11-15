import os
import random

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

import shapes as _shapes
import shapegrid as _shapegrid


_base_dir = os.path.dirname(__file__)
_content_dir = os.path.join(_base_dir, 'resources')
_supershapes_dict = _shapes.supershapes_dict()


def rectangle(vertical_shapes=40, horizontal_shapes=80, supershape=None):
    # provide defaults
    supershape = supershape or random.choice(_supershapes_dict.values())
    # create a grid
    grid = _shapegrid.ShapeGrid(supershape)
    for row in range(vertical_shapes):
        for col in range(horizontal_shapes):
            index = (row, col)
            grid.create(index)
    return grid


def character(c, max_vertical_indexes=None, max_horizontal_indexes=None,
              supershape=None,):
    # provide defaults
    supershape = supershape or random.choice(_supershapes_dict.values())
    max_vertical_indexes = max_vertical_indexes or 50
    max_horizontal_indexes = max_horizontal_indexes or 30
    # get an image of the character
    c_image = _character_image(c)
    # convert the image to a grid
    return _image_white_to_grid(c_image, supershape,
                                max_vertical_indexes, max_horizontal_indexes)


def _character_image(c):
    """Draw a white character on a black background."""
    black = 0
    white = 255
    # font by WLM Fonts
    # http://www.fontspace.com/wlm-fonts/wlm-carton
    font_path = os.path.join(os.path.dirname(__file__),
                             'resources', 'wlm_carton.ttf')
    # make the background
    image = PIL.Image.new('L', (300, 300), color=black)
    # draw the text
    draw = PIL.ImageDraw.Draw(image)
    try:
        font = PIL.ImageFont.truetype('impact.ttf', 200)  # has upper/lower case
    except IOError:
        font = PIL.ImageFont.truetype(font_path, 400)  # has only upper case
    draw.text((10, 10), c, fill=white, font=font)
    # isolate the text and return it
    c_box = image.getbbox()
    return image.crop(c_box)


def _image_white_to_grid(image, supershape,
                         max_vertical_indexes, max_horizontal_indexes):
    """Convert the image to a grid."""
    # make sure it is monochrom
    if len(image.getbands()) != 1:
        image = image.convert('L')
    # shrink the image with aspect
    image.thumbnail((max_horizontal_indexes, max_vertical_indexes),
                    PIL.Image.ANTIALIAS)
    # convert to black/white
    threshold = 128
    image = image.point(lambda i: 255 * (i > threshold))
    # get the pixels and build the grid based on each pixel's position and value
    pixels = image.load()
    grid = _shapegrid.ShapeGrid(supershape)
    width, height = image.size
    for y in range(height):
        for x in range(width):
            if pixels[x, y]:
                grid.create((y, x))
    return grid


if __name__ == '__main__':
    pass
