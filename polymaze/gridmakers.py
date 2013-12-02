import os

import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

import polygrid as _polygrid


_BASE_DIR = os.path.dirname(__file__)
_RESOURCE_DIR = os.path.join(_BASE_DIR, 'resources')


def character(c,
              supershape=None, complexity=None, aspect_h=None, aspect_w=None):
    grid = _polygrid.PolyGrid(supershape=supershape)
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


if __name__ == '__main__':
    pass
