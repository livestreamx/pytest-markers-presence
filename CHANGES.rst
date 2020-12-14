Changelog
---------

0.11.0
~~~~~~

* Removed options `--browse-url` and `--links-keyword` (transferred to Overhave framework)
* Updated tests
* Updated library dependencies

0.10.0
~~~~~~

* Updated libraries versions

0.9.2
~~~~~

* Updated directory supported patterns for dynamic pytest mark: excluded directories with names like ".*".

0.9.1
~~~~~

* Hotfix for plugin

0.9.0
~~~~~

* Added enabling of fail exitcode setting when all session tests were skipped

0.8.0
~~~~~

* Added task tracker URL specification for ticket links compiling
* Added specification of keyword for task tracker tickets collecting

0.7.6
~~~~~

* Fix for dataclasses objects extraction

0.7.5
~~~~~

* Added support for not traditional pytest items (for example, YamlItem)
* Updated tests

0.7.4
~~~~~

* Add option '--staging-warnings' to external enabling of warnings
* Updated tests

0.7.3
~~~~~

* No assertions rewriting for built-in types
* Updated tests

0.7.2
~~~~~

* Hotfix for assertions rewriting

0.7.1
~~~~~

* Tagged again (pypi package broken)

0.7.0
~~~~~

* Implemented Allure titles setting for BDD tests
* Updated tests
* Minor changes

0.6.3
~~~~~

* Hotfix for Allure step compilation

0.6.2
~~~~~

* Updated assertions rewriting: implemented smart Allure step compilation with attachments
* Updated tests

0.6.1
~~~~~

* Hotfix for assertions rewriting

0.6.0
~~~~~

* Implemented assertions rewriting with '--assert-steps' option
* Minor changes
* Updated tests

0.5.0
~~~~~

* Implemented new logic for '--staging' option
* Implemented support for dynamical tests marking
* Updated '--bdd-format' logic
* Updated tests

0.4.0
~~~~~

* Implemented detection of not classified functions usage
* Updated documentation
* Updated dev-requirements
* Updated tests

0.3.0
~~~~~

* Updated documentation
* Updated dev-requirements
* Minor fixes

0.2.0
~~~~~

* Implemented ignore of session items which do not contain 'originalname'

0.1.0
~~~~~

* First release