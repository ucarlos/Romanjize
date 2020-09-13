try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {"description": "A bunch of small tools that I made using Python.",
          "author": "Ulysses Carlos",
          "url": "N/A",
          "download_url": "Where to download it.",
          "author_email": "ucarlos1@student.gsu.edu",
          "version": "0.1",
          "install_requires": ['nose', 'mutagen', 'googletrans'],
          "packages": ['Romanjize'],
          "scripts": [],
          "name": "uly-romanjize-0.11"}


setup(**config)
