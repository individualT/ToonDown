import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

VERSION = '0.1.0'
PACKAGE_NAME = 'ToonDown'
AUTHOR = 'skuukzky1'
AUTHOR_EMAIL = 'jikbakgury@gmail.com'
URL = 'https://github.com/skuukzky1/tkor_downloader'

LICENSE = 'The MIT License'
DESCRIPTION = 'Toon Downloader'
LONG_DESCRIPTION = open('README.md', 'r', encoding='UTF8').read()
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
      'requests==2.22.0',
      'tqdm==4.61.2',
      'beautifulsoup4==4.9.3',
      'Pillow==8.3.1',
]

setup(name=PACKAGE_NAME,
      version=VERSION,
      description=DESCRIPTION,
      long_description=LONG_DESCRIPTION,
      long_description_content_type=LONG_DESC_TYPE,
      author=AUTHOR,
      license=LICENSE,
      author_email=AUTHOR_EMAIL,
      url=URL,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages()
      )