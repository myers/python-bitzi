#!/usr/bin/env python

__revision__ = "$Id: setup.py,v 1.3 2004/08/10 14:44:40 myers_carpenter Exp $"

from distutils.core import setup, Extension, Command
import distutils

import sys, os, re, unittest

try:
    import ctypes
except ImportError:
    print """\
The "ctypes" module is required for python-bitzi to work.  If you are on debian you 
can get it by doing

    apt-get install python-ctypes
  
For everyone else (including Windows users) you can download it here:

    http://sourceforge.net/project/showfiles.php?group_id=71702
"""
    sys.exit(1)

import bitzi

cmdclass = {}

setup_args = {
    "name": "python-bitzi",
    "version": bitzi.__version__,
    "description": "Metadata extraction using the Bitzi libraries",
    "long_description": """\
python-bitzi is a wrapper around the Bitcollider library from Bitzi.  It
allows you to extract metadata from different types of files.  Using this
library you can get the bitprint (tiger tree + sha1), md5, song length, song
bit rate, image dimensions.

You can think of Bitzi as the "card catalog" for the heavenly jukebox,
holding information about any and every media file that is ever reported to
them, not just the files available on the web, or through any particular
service, or through any particular sharing/distribution network.

Developers of file sharing networks should find this extension useful.
""",

    "license": "Public Domain",
    "author": "Myers W. Carpenter",
    "author_email": "icepick@icepick.info",
    "url": "http://icepick.info/projects/python-bitzi/",
    "download_url": "http://icepick.info/projects/python-bitzi/",
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Programming Language :: Python",
        "Topic :: Utilities",
        "Topic :: Communications :: File Sharing",
    ],
    'py_modules': ['bitzi',],
    'cmdclass': cmdclass,
}

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None

if hasattr(distutils.dist.DistributionMetadata, 'get_platforms'):
    setup_args['platforms'] = "win32 posix"


class test(Command):
    """
    Based off of http://mail.python.org/pipermail/distutils-sig/2002-January/002714.html
    """
    description  = "test the distribution prior to install"
    
    user_options = [
        ('verbosity=', 'l',
         "Set the verbosity on TestRunner",),
        ('test-dir=', None,
         "directory that contains the test definitions"),]
                 
    def initialize_options(self):
        self.test_dir = 'test'    
        self.verbosity = 1
        
    def finalize_options(self):
        build = self.get_finalized_command('build')
        self.build_purelib = build.build_purelib
        self.build_platlib = build.build_platlib
                                                                                           
    def run(self):
        import unittest
        self.run_command('build')
        self.run_command('build_ext')

        old_path = sys.path[:]
        sys.path.insert(0, self.build_purelib)
        sys.path.insert(0, self.build_platlib)
        sys.path.insert(0, os.path.join(os.getcwd(), self.test_dir))
        
        runner = unittest.TextTestRunner(verbosity=self.verbosity)
        suite = self.build_suite()
        runner.run(suite)
        
        sys.path = old_path[:]
                
    def build_suite(self):
        files = os.listdir(self.test_dir)
        test = re.compile("^test_.*.py$", re.IGNORECASE)
        files = filter(test.search, files)
        filenameToModuleName = lambda f: os.path.splitext(f)[0]
        moduleNames = map(filenameToModuleName, files)
        modules = map(__import__, moduleNames)
        load = unittest.defaultTestLoader.loadTestsFromModule
        return unittest.TestSuite(map(load, modules))                    
cmdclass['test'] = test            


if __name__ == '__main__':
    distutils.core.setup(**setup_args)
