pyrobase
========

*General Python Helpers and Utilities.*  |Issues|  |PyPI|

.. contents:: **Contents**


What is it?
-----------

``pyrobase`` assembles general Python helper functions and classes that
can be applied to any project. That includes some additional tasks
for the Paver build tool, an improved xmlrpc2scgi module, unit test
helpers, and generic base modules for various domains.

All modules have unit tests (currently pyrobase.paver is an exception),
and the goal is to reach >80% coverage.

See https://github.com/pyroscope/pyrobase/wiki for more.


Installation
------------

Install it with ``pip install pyrobase``, or more commonly just add
it as a dependency to your project and call ``python setup.py develop -U``.


Usage
-----

See the project's ``pavement.py`` and unit tests, and for a full API
documentation go to http://packages.python.org/pyrobase/.


Build Instructions
------------------

First, check out the source::

    git clone git://github.com/pyroscope/pyrobase.git ~/src/pyrobase
    cd ~/src/pyrobase

You are strongly encouraged to build within a virtualenv, if your
host has the "python-virtualenv" package installed this is simply done by…

::

    virtualenv --no-site-packages $(pwd)

If you don't have that package, use these commands instead::

    venv='https://github.com/pypa/virtualenv/raw/master/virtualenv.py'
    python -c "import urllib2; open('venv.py','w').write(urllib2.urlopen('$venv').read())"
    deactivate 2>/dev/null
    python venv.py --no-site-packages $(pwd)

Next, install necessary tools and build the project::

    . bin/activate
    easy_install -U setuptools paver
    paver develop -U
    paver docs
    paver lint -m
    paver coverage


Acknowledgements
----------------

* Repository hosting @ GitHub.
* Paver @ http://paver.github.com/paver/.
* https://github.com/Quantique for the inspiration on the scgi+ssh transport.


.. |Issues| image:: https://img.shields.io/github/issues/pyroscope/pyrobase.svg
   :target: https://github.com/pyroscope/pyrobase/issues
.. |PyPI| image:: https://img.shields.io/pypi/v/pyrobase.svg
   :target: https://pypi.python.org/pypi/pyrobase/