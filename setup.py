#! /usr/bin/env python

# check setuptools source code 
# https://bitbucket.org/pypa/setuptools/src/312a67d000cb05d15b854957466c4751cf5e1c08/setuptools/command/install.py?at=default&fileviewer=file-view-default

from distutils.command.clean import clean as Clean # write custom class that inherits from Clean => write custom Clean command run after main part of setup.py build is run
from pkg_resources import parse_version # to compare versions correctly (e.g. '10.0.0' > '2.0.0')
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from setuptools.extension import Extension
import os
import platform # get python version and python inplementation
import shutil
import sys
import traceback

if sys.version_info < (3, 6):
    raise RuntimeError("Python 3.6 or later required. The current"
                       " Python version is %s installed in %s."
                       % (platform.python_version(), sys.executable))

DISTNAME = 'dispypkg'
DESCRIPTION = 'Description'
with open('README.rst') as f:
    LONG_DESCRIPTION = f.read()
MAINTAINER = 'TK'
MAINTAINER_EMAIL = 'tobiaskrabel@gmail.com'
URL = ''
DOWNLOAD_URL = 'https://pypi.org/project/dispypkg/#files'
LICENSE = 'new BSD'

# we can actually import a restricted version of sklearn that
# does not need the compiled code
# import sklearn

VERSION = '0.0.0'

if platform.python_implementation() == 'PyPy': # https://pypy.org/, returns 'Cpython' when running on my machine
    NUMPY_MIN_VERSION = '1.14.0'
else:
    NUMPY_MIN_VERSION = '1.11.0'


# Optional setuptools features
# We need to import setuptools early, if we want setuptools features,
# as it monkey-patches the 'setup' function
# For some commands, use setuptools
SETUPTOOLS_COMMANDS = {
    'develop', 'release', 'bdist_egg', 'bdist_rpm',
    'bdist_wininst', 'install_egg_info', 'build_sphinx',
    'egg_info', 'easy_install', 'upload', 'bdist_wheel',
    '--single-version-externally-managed', 'sdist'
}
if SETUPTOOLS_COMMANDS.intersection(sys.argv):
    import setuptools

    extra_setuptools_args = dict(
        zip_safe=False,  # the package can run out of an .egg file
        include_package_data=True,
        extras_require={
            'alldeps': (
                'numpy >= {}'.format(NUMPY_MIN_VERSION)
            ),
        },
        ext_modules=cythonize([
            Extension(
                "%s.*" % DISTNAME, 
                ["%s/*.py" % DISTNAME]
            )
        ])
    )
else:
    extra_setuptools_args = dict()


# Custom clean command to remove build artifacts

class CleanCommand(Clean): # every custom command needs to implement a run method
    description = "Remove build artifacts from the source tree"

    def run(self):
        Clean.run(self)
        # Remove c files if we are not within a sdist package
        cwd = os.path.abspath(os.path.dirname(__file__))
        remove_c_files = not os.path.exists(os.path.join(cwd, 'PKG-INFO'))
        if remove_c_files:
            print('Will remove generated .c files')
        if os.path.exists('build'):
            shutil.rmtree('build')
        for dirpath, dirnames, filenames in os.walk('dispypkg'):
            for filename in filenames:
                if any(filename.endswith(suffix) for suffix in
                    (".pyx", '.c')):
                    os.unlink(os.path.join(dirpath, filename))
                    continue
                extension = os.path.splitext(filename)[1]
                if remove_c_files and extension in ['.c', '.cpp']:
                    pyx_file = str.replace(filename, extension, '.pyx')
                    if os.path.exists(os.path.join(dirpath, pyx_file)):
                        os.unlink(os.path.join(dirpath, filename))
            for dirname in dirnames:
                if dirname == '__pycache__':
                    shutil.rmtree(os.path.join(dirpath, dirname))

cmdclass = {'clean': CleanCommand}


# Optional wheelhouse-uploader features
# To automate release of binary packages for dispypkg we need a tool
# to download the packages generated by travis and appveyor workers (with
# version number matching the current release) and upload them all at once
# to PyPI at release time.
# The URL of the artifact repositories are configured in the setup.cfg file.

WHEELHOUSE_UPLOADER_COMMANDS = {'fetch_artifacts', 'upload_all'}
if WHEELHOUSE_UPLOADER_COMMANDS.intersection(sys.argv):
    import wheelhouse_uploader.cmd

    cmdclass.update(vars(wheelhouse_uploader.cmd))


def configuration(parent_package='', top_path=None):
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

    from numpy.distutils.misc_util import Configuration

    config = Configuration(None, parent_package, top_path)

    # Avoid non-useful msg:
    # "Ignoring attempt to set 'name' (from ... "
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)

    config.add_subpackage('dispypkg')

    return config

# used to capture whether numpy is installed and up-to-date
def get_numpy_status():
    """
    Returns a dictionary containing a boolean specifying whether NumPy
    is up-to-date, along with the version string (empty string if
    not installed).
    """
    numpy_status = {}
    try:
        import numpy
        numpy_version = numpy.__version__
        numpy_status['up_to_date'] = parse_version(
            numpy_version) >= parse_version(NUMPY_MIN_VERSION)
        numpy_status['version'] = numpy_version
    except ImportError:
        traceback.print_exc()
        numpy_status['up_to_date'] = False
        numpy_status['version'] = ""
    return numpy_status


def setup_package():
    metadata = dict(name=DISTNAME,
                    maintainer=MAINTAINER,
                    maintainer_email=MAINTAINER_EMAIL,
                    description=DESCRIPTION,
                    license=LICENSE,
                    url=URL,
                    download_url=DOWNLOAD_URL,
                    version=VERSION,
                    long_description=LONG_DESCRIPTION,
                    classifiers=['Intended Audience :: Data Scientists',
                                 'Programming Language :: C',
                                 'Programming Language :: Python',
                                 'Operating System :: Microsoft :: Windows',
                                 'Operating System :: POSIX',
                                 'Operating System :: Unix',
                                 'Operating System :: MacOS',
                                 'Programming Language :: Python :: 3.6',
                                 'Programming Language :: Python :: 3.7'
                                 ],
                    cmdclass=cmdclass,
                    install_requires=[
                        'numpy>={}'.format(NUMPY_MIN_VERSION)
                    ],
                    **extra_setuptools_args)

    if len(sys.argv) == 1 or (
            len(sys.argv) >= 2 and ('--help' in sys.argv[1:] or
                                    sys.argv[1] in ('--help-commands',
                                                    'egg_info',
                                                    '--version',
                                                    'clean'))):
        # For these actions, NumPy is not required
        #
        # They are required to succeed without Numpy for example when
        # pip is used to install dispypkg when Numpy is not yet present in
        # the system.
        try:
            from setuptools import setup
        except ImportError:
            from distutils.core import setup

        metadata['version'] = VERSION
    else:
        numpy_status = get_numpy_status()
        numpy_req_str = "dispypkg requires NumPy >= {}.\n".format(
            NUMPY_MIN_VERSION)

        instructions = ("Installation instructions are available on our "
                        "website\n")

        if numpy_status['up_to_date'] is False:
            if numpy_status['version']:
                raise ImportError("Your installation of Numerical Python "
                                  "(NumPy) {} is out-of-date.\n{}{}"
                                  .format(numpy_status['version'],
                                          numpy_req_str, instructions))
            else:
                raise ImportError("Numerical Python (NumPy) is not "
                                  "installed.\n{}{}"
                                  .format(numpy_req_str, instructions))

        from numpy.distutils.core import setup

        metadata['configuration'] = configuration

    setup(**metadata)


if __name__ == "__main__":
    setup_package()
    # cleanup
    shutil.rmtree("%s.egg-info" % DISTNAME)
