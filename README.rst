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

A simple plugin for easy staging your Python3 project's structure of `PyTest`_ tests.
Make the repository with your tests structured with `Allure`_ ideology.

--------
Features
--------

* Dynamical tests marking based on 'tests' subfolders
* List not classified functions
* List missed Allure BDD tags for test classes and functions (exclude fixtures and other incompatible objects)
* Assertions rewriting with Allure steps including attachments for complex objects:
    - Pydantic BaseModels
    - dictionaries
    - lists
    - long strings.
* Setting Allure titles for BDD tests based on 'Scenario' information
* Collecting of task tracker tickets with specified keyword
* Enable setting of fail exitcode when all session tests were skipped


Installation
------------

You can install "pytest-markers-presence" via `pip`_ from `PyPI`_::

    $ pip install pytest-markers-presence


Usage
-----

The `--staging` option is compatible with simple pytest run loop and could be used for dynamical tests marking.
The `--staging-warnings` option just enables warnings for `--staging` option.

The `--assert-steps` option is compatible with simple pytest run loop and could be used for assertions rewriting with
Allure steps.

The `--bdd-titles` option is compatible with simple pytest run loop and could be used for setting Allure titles for BDD
tests based on 'Scenario' information.

The `--bdd-format` option will not run your tests and it's also sensible for errors in the pytest
collection step. If you are using as part of you CI process the recommended way is to run it after the default test run.

The `--all-skipped-fail` option is compatible is simple pytest run loop
and could be used for enabling of fail exitcode setting when all session
tests were skipped.

For example:

    script:
      - pytest

      - pytest --staging --bdd-titles --all-skipped-fail

      - pytest --assert-steps

      - pytest --bdd-format


Examples of 'pytest' run with provided options:

    $ pytest tests --staging --assert-steps --bdd-titles

    ======================= test session starts =======================

    (hidden for brevity)

    ==================== 1 passed in 0.51 seconds =====================



    $ pytest --bdd-format

    ======================= test session starts =======================

    (hidden for brevity)

    You should create test class(es) for your test function(s):
    Test function: 'test_function', location: /path/to/test.py

    You should set BDD tag '@allure.feature' for your test class(es):
    Test class: 'TestClass', location: /path/to/file.py

    You should set BDD tag '@allure.story' for your test function(s):
    Test function: 'test_case', location: /path/to/file.py

    ================== no tests ran in 0.00 seconds ===================

    $ pytest --all-skipped-fail

    ======================= test session starts =======================

    (hidden for brevity)

    test_fail_on_all_skipped_when_skip.py::test_case SKIPPED                 [100%]

    Changed exitcode to FAILED because all tests were skipped.

    ======================== 1 skipped in 0.01s =======================


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

.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`pytest-markers-presence`: https://github.com/livestreamx/pytest-markers-presence/issues
.. _`PyTest`: https://github.com/pytest-dev/pytest
.. _`Allure`: https://github.com/allure-framework/allure-python
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
