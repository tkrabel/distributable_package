import os

from dispypkg._build_utils import maybe_cythonize_extensions


def configuration(parent_package='', top_path=None):
    from numpy.distutils.misc_util import Configuration
    from numpy.distutils.system_info import get_info
    import numpy

    # needs to be called during build otherwise show_version may fail sometimes
    get_info('blas_opt', 0)

    libraries = []
    if os.name == 'posix':
        libraries.append('m')

    config = Configuration('dispypkg', parent_package, top_path)

    # submodules with build utilities
    config.add_subpackage('_build_utils')

    # submodules which do not have their own setup.py
    # we must manually add sub-submodules & tests
    # config.add_subpackage('compose')

    # submodules which have their own setup.py
    # config.add_subpackage('cluster')

    # add the test directory
    #config.add_subpackage('tests')

    maybe_cythonize_extensions(top_path, config)

    return config


if __name__ == '__main__':
    from numpy.distutils.core import setup
    setup(**configuration(top_path='').todict())
