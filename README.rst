pyrobase
========

|Travis CI|  |RTD|  |Issues|  |PyPI|

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

Install the package with ``python -m pip install --user pyrobase``,
or more commonly just add it as a dependency to your project
and call ``python -m pip install -r requirements.txt``.
Installing into a virtualenv is recommended.


Usage
-----

See the project's ``pavement.py`` and unit tests, and for a full API
documentation go to http://packages.python.org/pyrobase/.

The `Contributing Guidelines`_ tell you how to report probelems and
request new features, and what to do as a developer or documentation author.


Acknowledgements
----------------

* Repository hosting @ GitHub.
* Paver @ http://paver.github.com/paver/.
* https://github.com/Quantique for the inspiration on the scgi+ssh transport.


.. _`Contributing Guidelines`: https://github.com/pyroscope/pyrobase/blob/master/CONTRIBUTING.rst

.. |RTD| image:: https://readthedocs.org/projects/pyrobase/badge/?version=latest
   :target: https://pyrobase.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status
.. |Travis CI| image:: https://travis-ci.org/pyroscope/pyrobase.svg?branch=master
   :target: https://travis-ci.org/pyroscope/pyrobase
.. |Issues| image:: https://img.shields.io/github/issues/pyroscope/pyrobase.svg
   :target: https://github.com/pyroscope/pyrobase/issues
.. |PyPI| image:: https://img.shields.io/pypi/v/pyrobase.svg
   :target: https://pypi.python.org/pypi/pyrobase/
