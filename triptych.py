#!/usr/bin/python


import argparse
import copy
import io
import os
import plistlib
import random
import sys

# Using the pillow fork of PIL.
from PIL import Image, ImageFilter
import requests

from google_image import GoogleImageSearch, ImageType, ImageSize


class Words(object):
    """All words in the system dict, with method for random selection."""

    def __init__(self):
        with open("/usr/share/dict/words") as word_doc:
            self.words = word_doc.read().splitlines()

    def get_random_word(self):
        return random.choice(self.words)

    def get_random_words(self, number):
        return [random.choice(words) for _ in xrange(number)]


# TODO: Pyiint, docs, license.
def main():
    parser = get_argparser()
    args = parser.parse_args()

    config_file = os.path.expanduser("~/.google_image_search")
    if os.path.exists(config_file):
        prefs = plistlib.readPlist(config_file)
        cx = prefs.get("CX")
        key = prefs.get("KEY")
    else:
        sys.exit("Please create a '%s' plist file with keys CX and KEY." %
                 config_file)

    google_image_search = GoogleImageSearch(cx, key)

    queries = []
    if args.search:
        queries = args.search[0:3]

    words = Words()
    images = []
    while len(images) < 3:
        if queries:
            query = queries.pop(0)
        else:
            query = words.get_random_word()
            print "Using random search term '%s'." % query

        google_image_search.search(query, imgType=ImageType.photo,
                                   imgSize=ImageSize.large)
        links = google_image_search.links()
        if not links:
            print "No results for search term '%s'." % query
            continue

        image = None
        while image is None:
            image_url = random.choice(links)
            try:
                image = Image.open(io.BytesIO(requests.get(image_url).content))
            except IOError:
                print ("Unable to download '%s'. Trying a different result." %
                       image_url)
                if len(links) > 1:
                    links.pop(links.index(image_url))
                else:
                    continue

        images.append(image)

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
        composite.save(os.path.expanduser(args.ofile) + ".jpg")
    else:
        composite.show()


def get_argparser():
    """Return an ArgumentParser configured for this app."""
    desc = "Generate a triptych from random Google image search results."
    parser = argparse.ArgumentParser(description=desc)
    arg_help = ("Search using this search term. May be specified up to three "
                "times.")
    parser.add_argument("-s", "--search", help=arg_help, nargs="*")
    parser.add_argument("-p", "--padding", help="Amount of padding, as a "
                        "percentage (float between 0 and 1), to all images in "
                        "the final composite. Default is ().", default=0.2)
    parser.add_argument("-o", "--ofile", help="Path to save image.")
    return parser


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
