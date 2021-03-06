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

:GitHub:    https://github.com/pyroscope/pyrobase#readme
:PyPI:      http://pypi.python.org/pypi/pyrobase/
:API docs:  https://pyrobase.readthedocs.io/en/latest/api.html
:OpenHub:   https://www.openhub.net/p/pyrobase


Installation
------------

Install the package with ``python -m pip install --user pyrobase``,
or more commonly just add it as a dependency to your project
and call ``python -m pip install -r requirements.txt``.
Installing into a virtualenv is recommended.


Usage
-----

See the project's unit tests for examples,
and for a full API documentation visit the `API Reference`_.

The `Contributing Guidelines`_ tell you how to report problems and
request new features, and what to do as a developer or documentation author.

.. _`API Reference`: https://pyrobase.readthedocs.io/en/latest/api.html


Acknowledgements
----------------

* Repository hosting @ GitHub.
* Documentation hosting by https://readthedocs.io/.
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
