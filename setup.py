"""
The matplotlib build options can be modified with a setup.cfg file. See
setup.cfg.template for more information.
"""

from __future__ import print_function, absolute_import
from collections import OrderedDict, namedtuple

# This needs to be the very first thing to use distribute
from distribute_setup import use_setuptools
use_setuptools()

import sys

# distutils is breaking our sdists for files in symlinked dirs.
# distutils will copy if os.link is not available, so this is a hack
# to force copying
import os
try:
    del os.link
except AttributeError:
    pass

# This 'if' statement is needed to prevent spawning infinite processes
# on Windows
if __name__ == '__main__':
    # BEFORE importing distutils, remove MANIFEST. distutils doesn't properly
    # update it when the contents of directories change.
    if os.path.exists('MANIFEST'):
        os.remove('MANIFEST')

try:
    from setuptools import setup
except ImportError:
    try:
        from setuptools.core import setup
    except ImportError:
        from distutils.core import setup

# The setuptools version of sdist adds a setup.cfg file to the tree.
# We don't want that, so we simply remove it, and it will fall back to
# vanilla distutils.
try:
    from setuptools.command import sdist
except ImportError:
    pass
else:
    del sdist.sdist.make_release_tree

import setupext
from setupext import print_line, print_raw, print_message, print_status

# Get the version from the source code
__version__ = setupext.Matplotlib().check()


# These are the packages in the order we want to display them.  This
# list may contain strings to create section headers for the display.

Spacer = namedtuple('Spacer', ['text'])

mpl_packages = OrderedDict()

mpl_packages['building'] = Spacer('Building Matplotlib')
mpl_packages['matplotlib'] = setupext.Matplotlib()
mpl_packages['python'] = setupext.Python()
mpl_packages['platform'] = setupext.Platform()

mpl_packages['required'] = Spacer('Required dependencies and extensions')
mpl_packages['numpy'] = setupext.Numpy()
mpl_packages['six'] = setupext.Six()
mpl_packages['dateutil'] = setupext.Dateutil()
mpl_packages['tornado'] = setupext.Tornado()
mpl_packages['pyparsing'] = setupext.Pyparsing()
mpl_packages['cxx'] = setupext.CXX()
mpl_packages['libagg'] = setupext.LibAgg()
mpl_packages['freetype'] = setupext.FreeType()
mpl_packages['ft2font'] = setupext.FT2Font(mpl_packages['freetype'],
                                           mpl_packages['numpy'],
                                           mpl_packages['cxx'])
mpl_packages['png'] = setupext.Png(mpl_packages['numpy'],
                                   mpl_packages['cxx'])
mpl_packages['image'] = setupext.Image(mpl_packages['numpy'],
                                       mpl_packages['libagg'],
                                       mpl_packages['cxx'])
mpl_packages['ttconv'] = setupext.TTConv(mpl_packages['numpy'],
                                         mpl_packages['cxx'])
mpl_packages['path'] = setupext.Path(mpl_packages['numpy'],
                                     mpl_packages['libAgg'],
                                     mpl_packages['cxx'])
mpl_packages['contour'] = setupext.Contour(mpl_packages['numpy'])
mpl_packages['delaunay'] = setupext.Delaunay(mpl_packages['numpy'])
mpl_packages['tri'] = setupext.Tri(mpl_packages['numpy'])

mpl_packages['optional'] = Spacer('Optional subpackages')
mpl_packages['sample_data'] = setupext.SampleData()
mpl_packages['toolkits'] = setupext.Toolkits()
mpl_packages['tests'] = setupext.Tests()

mpl_packages['optional backends'] = Spacer('Optional backend extensions')

# These backends are listed in order of preference, the first
# being the most preferred.  The first one that looks like it will
# work will be selected as the default backend.
mpl_packages['macosx'] = setupext.BackendMacOSX(mpl_packages['numpy'],
                                                mpl_packages['libagg'],
                                                mpl_packages['cxx'])
mpl_packages['qt4'] = setupext.BackendQt4()
mpl_packages['gtk3agg'] = setupext.BackendGtk3Agg()
mpl_packages['gtkcairo'] = setupext.BackendGtk3Cairo()
mpl_packages['gtkagg'] = setupext.BackendGtkAgg(mpl_packages['libagg'],
                                                mpl_packages['cxx'],
                                                mpl_packages['numpy'])
mpl_packages['tkagg'] = setupext.BackendTkAgg(mpl_packages['numpy'],
                                              mpl_packages['libagg'],
                                              mpl_packages['cxx'])
mpl_packages['wxagg'] = setupext.BackendWxAgg()
mpl_packages['gtkagg'] = setupext.BackendGtk(mpl_packages['numpy'])
mpl_packages['agg'] = setupext.BackendAgg(mpl_packages['numpy'],
                                          mpl_packages['libagg'],
                                          mpl_packages['freetype'],
                                          mpl_packages['cxx'])
mpl_packages['cairo'] = setupext.BackendCairo()
mpl_packages['windowing'] = setupext.Windowing()

mpl_packages['latex'] = Spacer('Optional LaTeX dependencies')
mpl_packages['dvipng'] = setupext.DviPng()
mpl_packages['ghostscript'] = setupext.Ghostscript()
mpl_packages['latex'] = setupext.LaTeX()
mpl_packages['pdftops'] = setupext.PdfToPs()


classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: Python Software Foundation License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 3',
    'Topic :: Scientific/Engineering :: Visualization',
    ]

# One doesn't normally see `if __name__ == '__main__'` blocks in a setup.py,
# however, this is needed on Windows to avoid creating infinite subprocesses
# when using multiprocessing.
if __name__ == '__main__':
    # These are distutils.setup parameters that the various packages add
    # things to.
    packages = []
    namespace_packages = []
    py_modules = []
    ext_modules = []
    package_data = {}
    package_dir = {'': 'lib'}
    install_requires = []
    default_backend = None


    # Go through all of the packages and figure out which ones we are
    # going to build/install.
    print_line()
    print_raw("Edit setup.cfg to change the build options")

    required_failed = []
    good_packages = []
    for package in mpl_packages.items():
        if isinstance(package, Spacer):
            print_raw('')
            print_raw(package.text.upper())
            continue

        try:
            result = package.check()
            if result is not None:
                message = 'yes [%s]' % result
                print_status(package.name, message)
        except setupext.CheckFailed as e:
            msg = str(e).strip()
            if len(msg):
                print_status(package.name, 'no  [%s]' % msg)
            else:
                print_status(package.name, 'no')
            if not package.optional:
                required_failed.append(package)
        else:
            good_packages.append(package)
            if isinstance(package, setupext.OptionalBackendPackage):
                if default_backend is None:
                    default_backend = package.name
    print_raw('')


    # Abort if any of the required packages can not be built.
    if required_failed:
        print_line()
        print_message(
            "The following required packages can not "
            "be built: %s" %
            ', '.join(x.name for x in required_failed))
        sys.exit(1)


    # Now collect all of the information we need to build all of the
    # packages.
    for package in good_packages:
        if isinstance(package, str):
            continue
        packages.extend(package.get_packages())
        namespace_packages.extend(package.get_namespace_packages())
        py_modules.extend(package.get_py_modules())
        ext = package.get_extension()
        if ext is not None:
            ext_modules.append(ext)
        data = package.get_package_data()
        for key, val in data.items():
            package_data.setdefault(key, [])
            package_data[key] = list(set(val + package_data[key]))
        install_requires.extend(package.get_install_requires())

    # Write the default matplotlibrc file
    if default_backend is None:
        default_backend = 'svg'
    if setupext.options['backend']:
        default_backend = setupext.options['backend']
    with open('matplotlibrc.template') as fd:
        template = fd.read()
    with open('lib/matplotlib/mpl-data/matplotlibrc', 'w') as fd:
        fd.write(template % {'backend': default_backend})


    # Build in verbose mode if requested
    if setupext.options['verbose']:
        for mod in ext_modules:
            mod.extra_compile_args.append('-DVERBOSE')


    # Finally, pass this all along to distutils to do the heavy lifting.
    distrib = setup(
        name="matplotlib",
        version=__version__,
        description="Python plotting package",
        author="John D. Hunter, Michael Droettboom",
        author_email="mdroe@stsci.edu",
        url="http://matplotlib.org",
        long_description="""
        matplotlib strives to produce publication quality 2D graphics
        for interactive graphing, scientific publishing, user interface
        development and web application servers targeting multiple user
        interfaces and hardcopy output formats.  There is a 'pylab' mode
        which emulates matlab graphics.
        """,
        license="BSD",
        packages=packages,
        namespace_packages = namespace_packages,
        platforms='any',
        py_modules=py_modules,
        ext_modules=ext_modules,
        package_dir=package_dir,
        package_data=package_data,
        classifiers=classifiers,
        download_url="https://downloads.sourceforge.net/project/matplotlib/matplotlib/matplotlib-{0}/matplotlib-{0}.tar.gz".format(__version__),

        # List third-party Python packages that we require
        install_requires=install_requires,

        # matplotlib has C/C++ extensions, so it's not zip safe.
        # Telling setuptools this prevents it from doing an automatic
        # check for zip safety.
        zip_safe=False,
    )
