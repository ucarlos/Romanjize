try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {"description": "A small program to convert Japanese tags into English.",
          "author": "Ulysses Carlos",
          "url": "N/A",
          "download_url": "https://github.com/ucarlos/Romanjize",
          "author_email": "ucarlos1@student.gsu.edu",
          "version": "0.15",
          "install_requires": ['nose', 'mutagen', 'google_trans_new'],
          "packages": ['Romanjize'],
          "scripts": [],
          "name": "romanjize"}


setup(**config)
