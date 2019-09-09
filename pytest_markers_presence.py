# -*- coding: utf-8 -*-
from typing import List

import _pytest.config
import _pytest.python
from _pytest.main import wrap_session
import py
from more_itertools import first

EXIT_CODE_ERROR = 11
EXIT_CODE_SUCCESS = 0

NOT_CLASSIFIED_FUNCTIONS_HEADLINE = "You should create test class(es) for your test function(s):"
CLASSES_OK_HEADLINE = "Cool, every function is classified."

NO_FEATURE_CLASSES_HEADLINE = "You should set BDD tag '@allure.feature' for your test class(es):"
NO_STORY_FUNCTIONS_HEADLINE = "You should set BDD tag '@allure.story' for your test function(s):"
BDD_MARKED_OK_HEADLINE = "Cool, every test class with its functions is marked with BDD tags."

CURDIR = py.path.local()


def pytest_addoption(parser):
    group = parser.getgroup("markers-presence", 'Markers presence')
    group.addoption(
        "--stage-markers",
        action="store_true",
        dest="stage_markers",
        default=False,
        help="Stage project with markers based on directories names in 'tests' folder",
    )
    group.addoption(
        "--bdd-markers",
        action="store_true",
        dest="bdd_markers",
        default=False,
        help="Show not classified functions usage and items without Allure BDD tags",
    )


def pytest_collection_modifyitems(session, config):
    if config.option.stage_markers:
        test_dir = first(CURDIR.listdir(fil=lambda x: x.check(dir=True) and x.fnmatch('tests')))
        staging_markers = [
            d.basename for d in test_dir.listdir(fil=lambda x: x.check(dir=True) and x.fnmatch('[!__]*'))
        ]
        for item in get_valid_session_items(session):
            try:
                marker = next(m for m in staging_markers if test_dir.join(m).strpath in item.fspath.strpath)
                item.add_marker(marker)
            except StopIteration:
                raise NameError(
                    f"Could not collect test function '{get_function_name(item)}'! Please, place your tests into "
                    f"'tests' folder and create directories (for example, 'unit') for tests classification."
                )


def pytest_cmdline_main(config):
    if config.option.bdd_markers:
        config.option.verbose = -1
        if wrap_session(config, is_checking_failed):
            return EXIT_CODE_ERROR
        return EXIT_CODE_SUCCESS


def include_if_class_without_feature(cls, lst):
    if not [m for m in cls.own_markers if m.name == "allure_label" and m.kwargs.get("label_type") == "feature"]:
        lst.append(cls)


def include_if_function_without_class(func, lst):
    if not func.getparent(_pytest.python.Class):
        lst.append(func)


def include_if_function_without_story(func, lst):
    if not [m for m in func.own_markers if m.name == "allure_label" and m.kwargs.get("label_type") == "story"]:
        lst.append(func)


def get_function_name(func):
    """
    No need to show function name with specified parameter for user.
    If the function was parametrized, it contains 'originalname' attribute.
    If the function was not parametrized, it has simple name.
    Plugin shows only simple name for fast debug and trouble shooting.
    """
    if func.originalname:
        return func.originalname
    return func.name


def get_valid_session_items(session):
    """
    Function that return only session items with attribute 'originalname'.
    It is necessary in case of different pytest plugins those provide incompatible
    logical constructions, for example Tavern framework.
    """
    return [item for item in session.items if hasattr(item, 'originalname') and hasattr(item, '_fixtureinfo')]


def get_items(session):
    seen_classes = {None}
    seen_functions = {None}
    for function in get_valid_session_items(session):
        func_name = get_function_name(function)
        if func_name not in seen_functions:
            seen_functions.add(func_name)
            cls = function.getparent(_pytest.python.Class)
            if cls not in seen_classes:
                seen_classes.add(cls)
                yield cls, function
            else:
                yield None, function


class Issues:
    not_classified_functions: List = []
    no_feature_classes: List = []
    no_story_functions: List = []

    def are_exists(self):
        return bool(self.not_classified_functions + self.no_feature_classes + self.no_story_functions)


def get_not_marked_items(session):
    issues = Issues()
    for cls, func in get_items(session):
        if cls:
            include_if_class_without_feature(cls, issues.no_feature_classes)
        include_if_function_without_class(func, issues.not_classified_functions)
        include_if_function_without_story(func, issues.no_story_functions)
    return issues


def write_classes(tw, classes):
    for cls in classes:
        tplt = "Test class: '{}', location: {}"
        tw.line(tplt.format(cls.name, CURDIR.bestrelpath(cls.fspath)))


def write_functions(tw, functions):
    for function in functions:
        tplt = "Test function: '{}', location: {}"
        tw.line(tplt.format(get_function_name(function), CURDIR.bestrelpath(function.fspath)))


def is_checking_failed(config, session):
    session.perform_collect()
    tw = _pytest.config.create_terminal_writer(config)
    tw.line()
    issues = get_not_marked_items(session)
    if not issues.are_exists():
        tw.line(CLASSES_OK_HEADLINE, green=True)
        tw.line(BDD_MARKED_OK_HEADLINE, green=True)

    if issues.not_classified_functions:
        tw.line(NOT_CLASSIFIED_FUNCTIONS_HEADLINE, red=True)
        write_functions(tw, issues.not_classified_functions)
        tw.line()

    if issues.no_feature_classes:
        tw.line(NO_FEATURE_CLASSES_HEADLINE, red=True)
        write_classes(tw, issues.no_feature_classes)
        tw.line()

    if issues.no_story_functions:
        tw.line(NO_STORY_FUNCTIONS_HEADLINE, red=True)
        write_functions(tw, issues.no_story_functions)
        tw.line(NO_STORY_FUNCTIONS_HEADLINE, red=True)

    return issues.are_exists()
