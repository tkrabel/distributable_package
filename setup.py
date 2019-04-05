#! /usr/bin/env python

# check setuptools source code 
# https://bitbucket.org/pypa/setuptools/src/312a67d000cb05d15b854957466c4751cf5e1c08/setuptools/command/install.py?at=default&fileviewer=file-view-default

import os
import platform # get python version and python inplementation
import shutil
import sys
import traceback
from pkg_resources import parse_version # to compare versions correctly (e.g. '10.0.0' > '2.0.0')
from distutils.command.clean import clean as Clean
from setuptools.extension import Extension
from setuptools import setup
from Cython.Build import cythonize
from Cython.Distutils import build_ext


if sys.version_info < (3, 6):
    raise RuntimeError("Python 3.6 or later required. The current"
                       " Python version is %s installed in %s."
                       % (platform.python_version(), sys.executable))

DISTNAME = 'dispypkg'
DESCRIPTION = 'Test package for multi-platform distribution'
with open('README.md') as f:
    LONG_DESCRIPTION = f.read()
MAINTAINER = 'Tobias Krabel, Florian Wetschoreck'
MAINTAINER_EMAIL = 'tobiaskrabel@gmail.com, florian.wetschoreck@gmail.com'
URL = ''
DOWNLOAD_URL = 'https://pypi.org/project/dispypkg/#files'
LICENSE = ''
VERSION = '0.0.7'


# custom commands in setup pipeline
class CustomBuildExt(build_ext):
    def run(self):
        build_ext.run(self)
        build_dir = os.path.realpath(self.build_lib)
        root_dir = os.path.dirname(os.path.realpath(__file__))
        target_dir = build_dir if not self.inplace else root_dir
        self.copy_file(f'{DISTNAME}/__init__.py', root_dir, target_dir)

    def copy_file(self, path, source_dir, destination_dir):
        if os.path.exists(os.path.join(source_dir, path)):
            shutil.copyfile(os.path.join(source_dir, path), 
                            os.path.join(destination_dir, path))

class CleanCommand(Clean):
    description = "Remove build artifacts from the source tree"

    def run(self):
        Clean.run(self)
        if os.path.exists('build'):
            shutil.rmtree('build')
        for dirpath, dirnames, filenames in os.walk(DISTNAME):
            print(dirpath, dirnames, filenames)
            for filename in filenames:
                if any(filename.endswith(suffix) for suffix in
                       (".pyc", ".c")):
                    os.unlink(os.path.join(dirpath, filename))
                    continue
            for dirname in dirnames:
                if dirname == '__pycache__':
                    shutil.rmtree(os.path.join(dirpath, dirname))

cmdclass = {'build_ext': CustomBuildExt, 'clean': CleanCommand}


setup(
  name=DISTNAME,
  ext_modules=cythonize([
    Extension(f"{DISTNAME}.*", [f"{DISTNAME}/[!__init]*.py"])
  ]),
  cmdclass=cmdclass,
  version=VERSION,
  description=DESCRIPTION,
  long_description=LONG_DESCRIPTION,
  author=MAINTAINER,                   
  author_email=MAINTAINER_EMAIL,
  url=URL,
  download_url=DOWNLOAD_URL,
  packages=[],
  include_package_data=True,
  classifiers=[
    'Intended Audience :: Data Scientists'
  ],
)
