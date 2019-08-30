# -*- coding: utf-8 -*-
import _pytest.config
import _pytest.python
from _pytest.main import wrap_session

EXIT_CODE_ERROR = 11
EXIT_CODE_SUCCESS = 0

STAGE_MARKERS = ["unit", "integration", "system"]

NOT_STAGED_CLASSES_HEADLINE = (
    "You should set stage marker with '@pytest.mark' ('unit', 'integration' or 'system') for your test class(es):"
)
CLASSES_STAGED_OK_HEADLINE = "Cool, every test class is staged."

NO_FEATURE_CLASSES_HEADLINE = "You should set BDD marker '@allure.feature' for your test class(es):"
NO_STORY_FUNCTIONS_HEADLINE = "You should set BDD marker '@allure.story' for your test function(s):"
BDD_MARKED_OK_HEADLINE = "Cool, every test class with its functions is marked with BDD tags."


def pytest_addoption(parser):
    group = parser.getgroup("markers-presence")
    group.addoption(
        "--stage-markers", action="store_true", dest="stage_markers", default=False, help="Show not staged classes"
    )
    group.addoption(
        "--bdd-markers",
        action="store_true",
        dest="bdd_markers",
        default=False,
        help="Show items without allure BDD markers",
    )


def pytest_cmdline_main(config):
    if config.option.stage_markers or config.option.bdd_markers:
        config.option.verbose = -1
        if _is_checking_failed(config):
            return EXIT_CODE_ERROR
        return EXIT_CODE_SUCCESS


def _is_checking_failed(config):
    return wrap_session(config, is_checking_failed)


def detect_not_staged_class(cls, lst):
    if not hasattr(cls, "own_markers") or not [m for m in cls.own_markers if m.name in STAGE_MARKERS]:
        lst.append(cls)


def detect_class_without_feature(cls, lst):
    if not [m for m in cls.own_markers if m.name == "allure_label" and m.kwargs.get("label_type") == "feature"]:
        lst.append(cls)


def detect_function_without_story(func, lst):
    if not [m for m in func.own_markers if m.name == "allure_label" and m.kwargs.get("label_type") == "story"]:
        lst.append(func)


def get_function_name(func):
    if func.originalname:
        return func.originalname
    return func.name


def get_items(session):
    seen_classes = {None}
    seen_functions = {None}
    for function in [item for item in session.items if hasattr(item, 'originalname')]:
        func_name = get_function_name(function)
        if func_name not in seen_functions:
            seen_functions.add(func_name)
            cls = function.getparent(_pytest.python.Class)
            if cls not in seen_classes:
                seen_classes.add(cls)
                yield cls, function
            else:
                yield None, function


def get_not_staged_classes(session):
    not_staged_classes = []
    for cls, _ in get_items(session):
        if cls:
            detect_not_staged_class(cls, not_staged_classes)
    return not_staged_classes


def get_not_marked_items(session):
    no_feature_classes = []
    no_story_functions = []
    for cls, func in get_items(session):
        if cls:
            detect_class_without_feature(cls, no_feature_classes)
        detect_function_without_story(func, no_story_functions)
    return no_feature_classes, no_story_functions


def write_classes(tw, classes):
    for cls in classes:
        tplt = "Test class: '{}', location: {}"
        tw.line(tplt.format(cls.name, cls.fspath))


def write_functions(tw, functions):
    for function in functions:
        tplt = "Test function: '{}', location: {}"
        tw.line(tplt.format(get_function_name(function), function.fspath))


def is_checking_failed(config, session):
    session.perform_collect()
    tw = _pytest.config.create_terminal_writer(config)
    failed = False

    if config.option.stage_markers:
        not_staged_classes = get_not_staged_classes(session)
        tw.line()
        if not_staged_classes:
            tw.line(NOT_STAGED_CLASSES_HEADLINE, red=True)
            write_classes(tw, not_staged_classes)
            failed = True
        else:
            tw.line(CLASSES_STAGED_OK_HEADLINE, green=True)
        tw.line()

    if config.option.bdd_markers:
        no_feature_classes, no_story_functions = get_not_marked_items(session)
        if not no_feature_classes and not no_story_functions:
            tw.line(BDD_MARKED_OK_HEADLINE, green=True)
        if no_feature_classes:
            tw.line(NO_FEATURE_CLASSES_HEADLINE, red=True)
            write_classes(tw, no_feature_classes)
            failed = True
            tw.line()
        if no_story_functions:
            tw.line(NO_STORY_FUNCTIONS_HEADLINE, red=True)
            write_functions(tw, no_story_functions)
            failed = True

    return failed
