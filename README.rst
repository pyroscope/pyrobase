pyrobase
========

|Travis CI|  |Issues|  |PyPI|

*General Python Helpers and Utilities.*

.. contents:: **Contents**


What is it?
-----------

``pyrobase`` assembles general Python helper functions and classes that
can be applied to any project. That includes some additional tasks
for the Paver build tool, an improved xmlrpc2scgi module, unit test
helpers, and generic base modules for various domains.

All modules have unit tests (currently pyrobase.paver is an exception),
and the goal is to reach >80% coverage.

Links:

-  `PyPI <http://pypi.python.org/pypi/pyrobase/>`_
-  `API docs <http://packages.python.org/pyrobase/>`_
-  `OpenHub <https://www.openhub.net/p/pyrobase>`_


Installation
------------

Install it with ``pip install --user pyrobase``, or more commonly just add
it as a dependency to your project and call ``python setup.py develop -U``.
Installing into a virtualenv is recommended.


Usage
-----

See the project's ``pavement.py`` and unit tests, and for a full API
documentation go to http://packages.python.org/pyrobase/.


Build Instructions
------------------

First, check out the source::

    mkdir -p ~/src
    git clone https://github.com/pyroscope/pyrobase.git ~/src/pyrobase
    cd ~/src/pyrobase

You are strongly encouraged to build within a virtualenv, call the provided
script ``bootstrap.sh`` to create one in your working directory::

    ./bootstrap.sh
    . bin/activate

Use ``paver`` to run common project tasks::

    paver test
    paver docs
    paver lint -m
    paver coverage


Performing a Release
--------------------

#. Check Travis CI status at https://travis-ci.org/pyroscope/pyrobase

#. Check for and fix ``pylint`` violations::

    paver lint -m

#. Verify ``debian/changelog`` for completeness and the correct version, and bump the release date::

    dch -r

#. Remove ‘dev’ version tagging from ``setup.cfg``, and perform a release check::

    sed -i -re 's/^(tag_[a-z ]+=)/##\1/' setup.cfg
    paver release

#. Commit and tag the release::

    git status  # check all is committed
    tag="v$(dpkg-parsechangelog | grep '^Version:' | awk '{print $2}')"
    git tag -a "$tag" -m "Release $tag"

#. Build the final release and upload it to PyPI::

    paver dist_clean sdist bdist_wheel
    twine upload dist/*.{zip,whl}

#. Create the ZIP file with the API documentation::

    paver dist_docs

#. Upload the docs from the ``dist`` directory to ``pythonhosted.org``::

    xdg-open "https://pypi.python.org/pypi?%3Aaction=pkg_edit&name=pyrobase" &


Acknowledgements
----------------

* Repository hosting @ GitHub.
* Paver @ http://paver.github.com/paver/.
* https://github.com/Quantique for the inspiration on the scgi+ssh transport.


.. |Travis CI| image:: https://travis-ci.org/pyroscope/pyrobase.svg?branch=master
    :target: https://travis-ci.org/pyroscope/pyrobase
.. |Issues| image:: https://img.shields.io/github/issues/pyroscope/pyrobase.svg
   :target: https://github.com/pyroscope/pyrobase/issues
.. |PyPI| image:: https://img.shields.io/pypi/v/pyrobase.svg
   :target: https://pypi.python.org/pypi/pyrobase/
