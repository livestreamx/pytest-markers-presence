# -*- coding: utf-8 -*-
import enum
import json
from dataclasses import asdict
from typing import List

import warnings
import _pytest.config
import _pytest.python
import allure
import pytest
from _pytest.main import wrap_session
import py
from _pytest.mark import Mark
from more_itertools import first
from pydantic import BaseModel, Any
from pydantic.dataclasses import dataclass


class Options(str, enum.Enum):
    # decoration
    STAGING = "--staging"
    ASSERT_STEPS = "--assert-steps"
    BDD_TITLES = "--bdd-titles"
    # linter
    BDD_FORMAT = "--bdd-format"


class ExitCodes(int, enum.Enum):
    SUCCESS = 0
    ERROR = 11


CORRECT_TESTS_FOLDER_PATTERN = "tests"
UNIT_TESTS_MARKER = "UNIT"
MIN_TESTS_SUBFOLDERS_NUM = 3

BDD_CHECKING_EXCLUDED_MARKERS = ["BEHAVE", "BEHAVIOR", "BDD", "PRESENCE_IGNORE"]
ALLURE_FEATURE_TAG = "feature"
ALLURE_STORY_TAG = "story"

NOT_CLASSIFIED_FUNCTIONS_HEADLINE = "You should create test class(es) for your test function(s):"
CLASSES_OK_HEADLINE = "Cool, every function is classified."

NO_FEATURE_CLASSES_HEADLINE = "You should set BDD tag '@allure.feature' for your test class(es):"
NO_STORY_FUNCTIONS_HEADLINE = "You should set BDD tag '@allure.story' for your test function(s):"
BDD_MARKED_OK_HEADLINE = "Cool, every test class with its functions is marked with BDD tags."

STAGING_HELP = f"Stage project with markers based on directories names in '{CORRECT_TESTS_FOLDER_PATTERN}' folder"
ASSERT_STEPS_HELP = "Represent assertion comparisons with Allure steps"
BDD_TITLES_HELP = "Set Allure titles for BDD test scenarios"
BDD_FORMAT_HELP = "Show not classified functions usage and items without Allure BDD tags"

ASSERTION_FAILED_MESSAGE = 'Assertion failed'
ALLURE_MAX_STRING_LENGTH = 25

CURDIR = py.path.local()


def pytest_addoption(parser):
    group = parser.getgroup("markers-presence", 'Markers presence')
    group.addoption(Options.STAGING, action="store_true", dest="stage_markers", default=False, help=STAGING_HELP)
    group.addoption(
        Options.ASSERT_STEPS, action="store_true", dest="assert_steps", default=False, help=ASSERT_STEPS_HELP
    )
    group.addoption(Options.BDD_TITLES, action="store_true", dest="bdd_titles", default=False, help=BDD_TITLES_HELP)
    group.addoption(Options.BDD_FORMAT, action="store_true", dest="bdd_markers", default=False, help=BDD_FORMAT_HELP)


def pytest_cmdline_main(config):
    if config.option.bdd_markers:
        config.option.verbose = -1
        if wrap_session(config, is_checking_failed):
            return ExitCodes.ERROR
        return ExitCodes.SUCCESS


def pytest_collection_modifyitems(session, config):
    if config.option.stage_markers:
        mark_tests_by_location(session)
    if config.option.bdd_titles:
        set_bdd_titles_if_necessary(session)


def pytest_assertrepr_compare(config, op, left, right):
    if config.option.assert_steps:
        comparison = AllureComparison(op=op, left=left, right=right)
        comparison.compile_allure_step()
        return comparison.get_pytest_assertrepr()


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

    return issues.are_exists()


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
    return [item for item in session.items if hasattr(item, 'originalname')]


class Issues:
    not_classified_functions: List = []
    no_feature_classes: List = []
    no_story_functions: List = []

    def are_exists(self):
        return bool(self.not_classified_functions + self.no_feature_classes + self.no_story_functions)


@dataclass(frozen=True)
class JSONDumpsKwargs:
    sort_keys: bool = True
    indent: int = 4
    ensure_ascii: bool = False


JSON_DUMPS_KWARGS = asdict(JSONDumpsKwargs())


class AllureComparison(BaseModel):
    op: str
    left: Any
    right: Any

    @staticmethod
    def is_str_longer_than_max_len(string):
        return len(string) > ALLURE_MAX_STRING_LENGTH

    @classmethod
    def str_with_fixed_len(cls, obj):
        string = str(obj)
        if cls.is_str_longer_than_max_len(string):
            return f"{string[0:ALLURE_MAX_STRING_LENGTH]}..."
        return string

    def get_allure_step_description(self):
        return (
            f"{ASSERTION_FAILED_MESSAGE}: \"{self.str_with_fixed_len(self.left)} {self.str_with_fixed_len(self.op)}"
            f" {self.str_with_fixed_len(self.right)}\""
        )

    @staticmethod
    def _attach_json(dumped, name):
        allure.attach(dumped, name, allure.attachment_type.JSON)

    @classmethod
    def attach_as_is(cls, obj, name):
        if isinstance(obj, BaseModel):
            cls._attach_json(obj.json(**JSON_DUMPS_KWARGS), name)
        elif isinstance(obj, (dict, list)):
            cls._attach_json(json.dumps(obj, **JSON_DUMPS_KWARGS), name)
        else:
            allure.attach(str(obj), name, allure.attachment_type.TEXT)

    def compile_allure_step(self):
        with pytest.raises(AssertionError):
            with allure.step(self.get_allure_step_description()):
                if self.is_str_longer_than_max_len(str(self.left)) or self.is_str_longer_than_max_len(str(self.right)):
                    self.attach_as_is(self.left, "Left")
                    self.attach_as_is(self.right, "Right")
                raise AssertionError

    def get_pytest_assertrepr(self):
        return [f'\"{self.left} {self.op} {self.right}\"', f"    {ASSERTION_FAILED_MESSAGE}!"]


def get_not_marked_items(session):
    issues = Issues()
    for cls, func in get_items(session):
        if cls and not detect_excluded_markers(cls):
            include_if_class_without_feature(cls, issues.no_feature_classes)
        if not detect_excluded_markers(func) and not is_parent_excluded(func):
            include_if_function_without_class(func, issues.not_classified_functions)
            include_if_function_without_story(func, issues.no_story_functions)
    return issues


def mark_tests_by_location(session):
    try:
        test_dir = first(CURDIR.listdir(fil=lambda x: x.check(dir=True) and x.fnmatch(CORRECT_TESTS_FOLDER_PATTERN)))
    except ValueError:
        warnings.warn(f"Could not find folder '{CORRECT_TESTS_FOLDER_PATTERN}' in '{CURDIR.strpath}'!", UserWarning)
        return

    staging_markers = [d.basename for d in test_dir.listdir(fil=lambda x: x.check(dir=True) and x.fnmatch('[!__]*'))]
    if not staging_markers:
        warnings.warn(
            f"No one subfolder was found in '{test_dir.basename}' folder, so test markers had not been generated!",
            UserWarning,
        )
        return
    if len(staging_markers) < MIN_TESTS_SUBFOLDERS_NUM:
        warnings.warn(
            f"You should have at least {MIN_TESTS_SUBFOLDERS_NUM} directories for tests to make staging better.",
            UserWarning,
        )
    if UNIT_TESTS_MARKER not in to_upper_case(staging_markers):
        warnings.warn(f"Does your project really contain no '{UNIT_TESTS_MARKER}' tests? Amazing.", UserWarning)

    for item in get_valid_session_items(session):
        try:
            marker = next(m for m in staging_markers if test_dir.join(m).strpath in item.fspath.strpath)
        except StopIteration:
            warnings.warn(
                f"Could not add item for test function '{get_function_name(item)}'! Please, place your function "
                f"into {CORRECT_TESTS_FOLDER_PATTERN} folder and create directories (for example, 'unit') for "
                f"tests classification.",
                UserWarning,
            )
            continue
        item.add_marker(marker)


def to_upper_case(lst):
    return [item.upper() for item in lst]


def get_item_markers_names(item):
    return [m.name for m in item.own_markers]


def detect_excluded_markers(item):
    return set(to_upper_case(get_item_markers_names(item))) & set(BDD_CHECKING_EXCLUDED_MARKERS)


def is_allure_marker_with_label(marker, label):
    return marker.name == "allure_label" and marker.kwargs.get("label_type") == label


def include_if_function_without_class(func, lst):
    if not func.getparent(_pytest.python.Class):
        lst.append(func)


def include_if_class_without_feature(cls, lst):
    if not [m for m in cls.own_markers if is_allure_marker_with_label(m, ALLURE_FEATURE_TAG)]:
        lst.append(cls)


def include_if_function_without_story(func, lst):
    if not [m for m in func.own_markers if is_allure_marker_with_label(m, ALLURE_STORY_TAG)]:
        lst.append(func)


def is_parent_excluded(func):
    parent = func.getparent(_pytest.python.Class)
    return parent and detect_excluded_markers(parent)


def set_bdd_titles_if_necessary(session):
    for item in get_valid_session_items(session):
        if hasattr(item, "_obj") and hasattr(item._obj, "__scenario__"):
            item.own_markers.append(
                Mark(name="allure_display_name", args=(f"{item._obj.__scenario__.name}",), kwargs={})
            )
