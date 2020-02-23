Contributing Guidelines
=======================

See `contribution-guide.org`_ for the basics on contributing
to an open source project.

.. _issue-reporting:

Reporting an Issue, or Requesting a Feature
-------------------------------------------

Any defects and feature requests are managed using GitHub's
*issue tracker*.
If you never opened an issue on GitHub before, consult the
`Mastering Issues`_ guide.

Before creating a bug report, please read `contribution-guide.org`'s `Submitting Bugs`_.


Creating a Work Directory
-------------------------

First, check out the source::

    mkdir -p ~/src
    git clone https://github.com/pyroscope/pyrobase.git ~/src/pyrobase
    cd $_

You are strongly encouraged to build within a virtualenv, call the provided
script ``bootstrap.sh`` to create one in your working directory::

    PYTHON=python3 ./bootstrap.sh
    . .env


Common Development Tasks
------------------------

Here are some common project tasks::

    pytest  # Run unittests
    invoke docs -o  # Build documentation and show in browser
    paver lint -m  # Check code quality
    paver cov  # Run unittests & show coverage report
    tox  # Run unittests in various test environments (multiple Python versions)


.. _`Mastering Issues`: https://guides.github.com/features/issues/
.. _`contribution-guide.org`: http://www.contribution-guide.org/
.. _`Submitting Bugs`: http://www.contribution-guide.org/#submitting-bugs
