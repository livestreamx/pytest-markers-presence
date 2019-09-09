# -*- coding: utf-8 -*-
import pytest

from pytest_markers_presence import (
    EXIT_CODE_ERROR,
    EXIT_CODE_SUCCESS,
    CLASSES_OK_HEADLINE,
    BDD_MARKED_OK_HEADLINE,
    NOT_CLASSIFIED_FUNCTIONS_HEADLINE,
    NO_FEATURE_CLASSES_HEADLINE,
    NO_STORY_FUNCTIONS_HEADLINE,
    UNIT_TESTS_MARKER,
)


@pytest.fixture
def stage_option():
    return "--stage-markers"


@pytest.fixture
def bdd_option():
    return "--bdd-markers"


class TestMarkersPresencePositive:
    def test_stage_markers_globally(self, request, stage_option):
        assert len(
            [
                item
                for item in request.session.items
                if [m for m in item.own_markers if m.name.upper() == UNIT_TESTS_MARKER]
            ]
        ) == len(
            request.session.items
        ), f"I am sure - these tests are not marked as '{UNIT_TESTS_MARKER}' with option '{stage_option}'!"

    def test_empty_stage_markers(self, testdir, stage_option):
        """Make sure that pytest accepts '--stage-markers' fixture"""

        # create a temporary pytest test module
        testdir.makepyfile(
            """
            assert True
            """
        )

        # run pytest with the following cmd args
        result = testdir.runpytest(stage_option, "-v")

        # make sure that that we get a '0' exit code for the testsuite
        assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED

    def test_empty_bdd_markers(self, testdir, bdd_option):
        """Make sure that pytest accepts 'bdd-markers' fixture"""

        # create a temporary pytest test module
        testdir.makepyfile(
            """
            assert True
            """
        )

        # run pytest with the following cmd args
        result = testdir.runpytest(bdd_option, "-v")

        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines([f"*{CLASSES_OK_HEADLINE}*", f"*{BDD_MARKED_OK_HEADLINE}*", "*no tests ran in *"])

        # make sure that that we get a '0' exit code for the testsuite
        assert result.ret == EXIT_CODE_SUCCESS

    def test_help_message(self, testdir, stage_option, bdd_option):
        result = testdir.runpytest("--help")
        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines(
            [
                "Markers presence:*",
                f"*{stage_option}*Stage project with markers based on directories names",
                "*in 'tests' folder",
                f"*{bdd_option}*Show not classified functions usage and items without",
                "*Allure BDD tags",
            ]
        )

    def test_fixture_not_affected(self, testdir, bdd_option):
        testdir.makepyfile(
            """
            import pytest
            @pytest.fixture
            def fixture_def():
                return True
            """
        )
        result = testdir.runpytest(bdd_option)
        result.stdout.fnmatch_lines([f"*{CLASSES_OK_HEADLINE}*", f"*{BDD_MARKED_OK_HEADLINE}*", "*no tests ran in *"])
        assert result.ret == EXIT_CODE_SUCCESS

    @pytest.mark.parametrize("framework", ["behave", "pytest_bdd"])
    @pytest.mark.parametrize("bdd_step", ["given", "when", "then"])
    def test_bdd_step_not_affected(self, testdir, bdd_option, framework, bdd_step):
        testdir.makepyfile(
            """
            import pytest
            from {package} import {step}
            @{step}("Test")
            def some_bdd_step():
                return True
            """.format(
                package=framework, step=bdd_step
            )
        )
        result = testdir.runpytest(bdd_option)
        result.stdout.fnmatch_lines([f"*{CLASSES_OK_HEADLINE}*", f"*{BDD_MARKED_OK_HEADLINE}*", "*no tests ran in *"])
        assert result.ret == EXIT_CODE_SUCCESS


class TestMarkersPresenceNegative:
    def test_bdd_markers_simple(self, testdir, bdd_option):
        """Make sure that pytest fails session with our fixtures."""

        testdir.makepyfile(
            """
            class TestClass:
                def test_case(self):
                    assert True
            """
        )
        result = testdir.runpytest(bdd_option)
        result.stdout.fnmatch_lines(
            [
                f"*{NO_FEATURE_CLASSES_HEADLINE}*",
                "Test class*TestClass*",
                f"*{NO_STORY_FUNCTIONS_HEADLINE}*",
                "Test function*test_case*",
                "*no tests ran in *",
            ]
        )
        assert result.ret == EXIT_CODE_ERROR

    def test_markers_without_class(self, testdir, bdd_option):
        """Make sure that pytest fails session with our fixtures."""

        testdir.makepyfile(
            """
            def test_case(self):
                assert True
            """
        )
        result = testdir.runpytest(bdd_option)
        result.stdout.fnmatch_lines(
            [
                f"*{NOT_CLASSIFIED_FUNCTIONS_HEADLINE}*",
                f"*{NO_STORY_FUNCTIONS_HEADLINE}*",
                "*test_case*",
                "*no tests ran in *",
            ]
        )
        assert result.ret == EXIT_CODE_ERROR
