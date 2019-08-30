=======================
pytest-markers-presence
=======================

.. image:: https://img.shields.io/pypi/v/pytest-markers-presence.svg
    :target: https://pypi.org/project/pytest-markers-presence
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-markers-presence.svg
    :target: https://pypi.org/project/pytest-markers-presence
    :alt: Python versions

.. image:: https://travis-ci.org/livestreamx/pytest-markers-presence.svg?branch=master
    :target: https://travis-ci.org/livestreamx/pytest-markers-presence
    :alt: See Build Status on Travis CI

.. image:: https://ci.appveyor.com/api/projects/status/github/livestreamx/pytest-markers-presence?branch=master
    :target: https://ci.appveyor.com/project/livestreamx/pytest-markers-presence/branch/master
    :alt: See Build Status on AppVeyor

A simple plugin to detect missed pytest tags and markers

----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.


Features
--------

* List not staged test classes
* List missed Allure BDD tags for test classes and functions (exclude fixtures)


Installation
------------

You can install "pytest-markers-presence" via `pip`_ from `PyPI`_::

    $ pip install pytest-markers-presence


Usage
-----

The `--stage-markers` and other provided options will not run your tests and it's also sensible for errors in the pytest
collection step. If you are using as part of you CI process the recommended way is to run it after the default test run.
For example:

    script:
      - pytest
      - pytest --stage-markers
      - pytest --bdd-markers
      - pytest --stage-markers --bdd-markers


Example of 'pytest' run with provided options:

    $ pytest --stage-markers

    =================== test session starts ===================

    (hidden for brevity)

    You should set stage marker with '@pytest.mark' ('unit', 'integration' or 'system') for your test class(es):
    Test class name: 'TestClass', location: /path/to/file.py

    ============== no tests ran in 0.00 seconds ===============

    $ pytest --bdd-markers

    =================== test session starts ===================

    (hidden for brevity)

    You should set BDD marker '@allure.feature' for your test class(es):
    Test class name: 'TestClass', location: /path/to/file.py

    You should set BDD marker '@allure.story' for your test function(s):
    Test case name: 'test_case', location: /path/to/file.py

    ============== no tests ran in 0.00 seconds ===============


Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-markers-presence" is free and open source software


Issues
------

If you encounter any problems, please `pytest-markers-presence`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`pytest-markers-presence`: https://github.com/livestreamx/pytest-markers-presence/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
