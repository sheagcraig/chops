#!/usr/bin/python


import io
# TODO: Might not be needed.
# import json

# Using the pillow fork of PIL.
from PIL import Image, ImageFilter
import requests


class GoogleImageSearch(object):
    """Class for searching Google Images.

    The proper image search API has been deprecated.

    This method makes use of the Custom Search Engine feature at the
    free tier to make up to 100 searches per day.
    """
    base_url = "https://www.googleapis.com/customsearch/v1"

    def __init__(self, cx, key):
        self.cx = cx
        self.key = key

    def search(self, query, **kwargs):
        """Perform an image search with optional search arguments."""
        # Other known args: "imgSize": "medium", "fileType": "jpg"
        # I think "num" is number of results to get per request.
        # I think "start" is offset into paged results.
        response = requests.get(self.base_url,
                                {"cx": self.cx, "key": self.key, "q": query,
                                 "searchType": "image", "num": 10, "start": 1})
        self.json_content = response.json()
        return self.json_content["items"]


# Example after doing gis.search("Tacos")
# for link in [item["link"] for item in items]:
#     PIL.Image.open(io.BytesIO(requests.get(link).content)).show()

def main():
    pass


if __name__ == "__main__":
    main()
