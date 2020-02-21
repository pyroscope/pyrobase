# -*- coding: utf-8 -*-
""" PyroBase - General Python Helpers and Utilities.

    Copyright (c) 2011-2018 The PyroScope Project <pyroscope.project@gmail.com>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""
from __future__ import with_statement, print_function

import os
import re
import sys
import webbrowser

from setuptools import find_packages

from paver.easy import *
from paver.setuputils import setup

# Bootstrap our own tasks, projects using us don't need this!
if os.path.abspath("src") not in sys.path:
    sys.path.insert(0, os.path.abspath("src"))
from pyrobase.paver.easy import *


#
# Project Metadata
#

changelog = path("debian/changelog")

name, version = open(changelog).readline().split(" (", 1)
version, _ = version.split(")", 1)

project = dict(
    # egg
    name = "pyrobase",
    version = version,
    package_dir = {"": "src"},
    packages = find_packages("src", exclude = ["tests"]),
    include_package_data = True,
    zip_safe = True,
    data_files = [
        ("EGG-INFO", [
            "README.rst", "LICENSE", "debian/changelog",
        ]),
    ],

    # dependencies
    install_requires = [
        'six',
    ],
    setup_requires = [
    ],
    extras_require={
        'imgur': ['imgurpython', 'requests'],
        'imgur_ssl': ['imgurpython', 'requests[security]'],
    },

    # tests
    test_suite = "nose.collector",

    # cheeseshop
    author = "The PyroScope Project",
    author_email = "pyroscope.project@gmail.com",
    description = __doc__.split('.', 1)[0].strip(),
    long_description = __doc__.split('.', 1)[1].strip(),
    license = [line.strip() for line in __doc__.splitlines()
        if line.strip().startswith("Copyright")][0],
    url = "https://github.com/pyroscope/pyrobase",
    keywords = "python utility library paver unittests",
    classifiers = [
        # see http://pypi.python.org/pypi?:action=list_classifiers
        #"Development Status :: 3 - Alpha",
        #"Development Status :: 4 - Beta",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
)


#
# Build
#
@task
@needs(["setuptools.command.egg_info"])
def bootstrap():
    "initialize project"


@task
@needs("docs")
def dist_docs():
    "create a documentation bundle"
    dist_dir = path("dist")
    docs_package = path("%s/%s-%s-docs.zip" % (dist_dir.abspath(), options.setup.name, options.setup.version))

    dist_dir.exists() or dist_dir.makedirs()
    docs_package.exists() and docs_package.remove()

    sh(r'cd build/apidocs && zip -qr9 %s .' % (docs_package,))

    print('')
    print("Upload @ http://pypi.python.org/pypi?:action=pkg_edit&name=%s" % ( options.setup.name,))
    print(docs_package)


#
# Testing
#

PYTEST_CMD = 'pytest -c ./setup.cfg src/tests'

@task
def test():
    "run unit tests"
    sh(PYTEST_CMD)


@task
def cov():
    "generate coverage report and show in browser"
    coverage_index = path("build/coverage/index.html")
    coverage_index.remove()
    sh(PYTEST_CMD)
    coverage_index.exists() and webbrowser.open(
        'file://{}'.format(os.path.abspath(coverage_index)))

@task
@needs("setuptools.command.build")
def functest():
    "functional test of the command line tools"
    from pyrobase.paver.support import vsh

    venv = path("build/venv")
    venv.exists() and venv.rmtree()
    sh("git clone --local '%s' '%s'" % (os.getcwd(), venv))
    with pushd(venv) as basedir:
        sh("virtualenv", ".")
        vsh("pip", "install", "-q", "-U", "setuptools")
        vsh("pip", "install", "-q", "paver")
        vsh("paver", "bootstrap")


#
# Release Management
#
@task
@needs(["dist_clean", "minilib", "generate_setup", "sdist"])
def release():
    "check release before upload to PyPI"
    sh("paver bdist_wheel")
    wheels = path("dist").files("*.whl")
    if not wheels:
        error("\n*** ERROR: No release wheel was built!")
        sys.exit(1)
    if any(".dev" in i for i in wheels):
        error("\n*** ERROR: You're still using a 'dev' version!")
        sys.exit(1)

    # Check that source distribution can be built and is complete
    print('')
    print("~" * 78)
    print("TESTING SOURCE BUILD")
    sh( "{ command cd dist/ && unzip -q %s-%s.zip && command cd %s-%s/"
        "  && /usr/bin/python setup.py sdist >/dev/null"
        "  && if { unzip -ql ../%s-%s.zip; unzip -ql dist/%s-%s.zip; }"
        "        | cut -b26- | sort | uniq -c| egrep -v '^ +2 +' ; then"
        "       echo '^^^ Difference in file lists! ^^^'; false;"
        "    else true; fi; } 2>&1"
        % tuple([project["name"], version] * 4)
    )
    path("dist/%s-%s" % (project["name"], version)).rmtree()
    print("~" * 78)

    print('')
    print("Created", " ".join([str(i) for i in path("dist").listdir()]))
    print("Use 'paver sdist bdist_wheel' to build the release and")
    print("    'twine upload dist/*.{zip,whl}' to upload to PyPI")
    print("Use 'paver dist_docs' to prepare an API documentation upload")


#
# Main
#
setup(**project)
