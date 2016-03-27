#!/usr/bin/python


# Copyright (C) 2016 Shea G Craig <shea.craig@sas.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""3x: Composite abitrary images into a horizontal image."""


import argparse
import copy
import os
from random import shuffle

# Using the pillow fork of PIL.
from PIL import Image, ImageFilter


def main():
    parser = get_argparser()
    args = parser.parse_args()
    dirpath, _, filenames = os.walk(
        os.path.expanduser(args.image_folder)).next()
    image_paths = [os.path.join(dirpath, image) for image in filenames]
    images = get_images(image_paths)

    smallest_height = min(image.height for image in images)

    resized_images = resize_images(images, smallest_height)

    padding = int(args.padding * smallest_height)

    # Composite width = width of all images, plus padding on either side.
    width = sum(image.width for image in resized_images) + (
        padding * (len(resized_images) + 1))

    composite = Image.new("RGB", (width, smallest_height + 2 * padding),
                          color=(255, 255, 255))

    paste_images(resized_images, composite, padding)

    composite.filter(ImageFilter.UnsharpMask(0.4, 150))

    if args.ofile:
        composite.save(os.path.expanduser(args.ofile))
    else:
        composite.show()


def get_argparser():
    """Return an ArgumentParser configured for this app."""
    desc = ("Given a folder of images, generate a single image with all "
            "images horizontally arrayed.")
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument("image_folder", help="Path to folder of images.")
    parser.add_argument("-p", "--padding", help="Amount of padding, as a "
                        "percentage (float between 0 and 1), to all images in "
                        "the final composite. Default is ().", default=0.2)
    parser.add_argument("-o", "--ofile", help="Path to save image.")
    return parser


def get_images(image_paths):
    images = []
    for image in image_paths:
        try:
            images.append(Image.open(image))
        except IOError:
            print "%s is not an image file." % image
    return images


def resize_images(images, smallest_height):
    """Scale a list of images to the smallest height."""
    result = []
    for image in images:
        scale_factor = smallest_height / float(image.height)
        new_x = int(image.width * scale_factor)
        scaled_image = image.resize((new_x, smallest_height), Image.LANCZOS)
        result.append(scaled_image)
    return result


def paste_images(images, composite, padding):
    """Paste a list of images into a composite, with padding."""
    x = padding
    for image in images:
        composite.paste(image, (x, padding))
        x += image.width + padding


if __name__ == "__main__":
    main()
