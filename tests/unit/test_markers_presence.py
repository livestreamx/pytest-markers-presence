# -*- coding: utf-8 -*-
import pytest

from pytest_markers_presence import (
    STAGE_MARKERS_OPT,
    BDD_MARKERS_OPT,
    ASSERT_STEPS_OPT,
    EXIT_CODE_ERROR,
    EXIT_CODE_SUCCESS,
    CLASSES_OK_HEADLINE,
    BDD_MARKED_OK_HEADLINE,
    NOT_CLASSIFIED_FUNCTIONS_HEADLINE,
    NO_FEATURE_CLASSES_HEADLINE,
    NO_STORY_FUNCTIONS_HEADLINE,
    UNIT_TESTS_MARKER,
    ASSERTION_FAILED_MESSAGE,
)


class TestMarkersPresencePositive:
    def test_stage_markers_globally(self, request):
        assert len(
            [
                item
                for item in request.session.items
                if [m for m in item.own_markers if m.name.upper() == UNIT_TESTS_MARKER]
            ]
        ) == len(
            request.session.items
        ), f"I am sure - these tests are not marked as '{UNIT_TESTS_MARKER}' with option '{STAGE_MARKERS_OPT}'!"

    def test_empty_stage_markers(self, testdir):
        f"""Make sure that pytest accepts '{STAGE_MARKERS_OPT}' fixture"""

        # create a temporary pytest test module
        testdir.makepyfile(
            """
            assert True
            """
        )

        # run pytest with the following cmd args
        result = testdir.runpytest(STAGE_MARKERS_OPT, "-v")

        # make sure that that we get a '0' exit code for the testsuite
        assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED

    def test_empty_assertions(self, testdir):
        f"""Make sure that pytest accepts '{ASSERT_STEPS_OPT}' fixture"""

        # create a temporary pytest test module
        testdir.makepyfile(
            """
            assert True
            """
        )

        # run pytest with the following cmd args
        result = testdir.runpytest(ASSERT_STEPS_OPT, "-v")

        # make sure that that we get a '0' exit code for the testsuite
        assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED

    def test_empty_bdd_markers(self, testdir):
        f"""Make sure that pytest accepts '{BDD_MARKERS_OPT}' fixture"""

        # create a temporary pytest test module
        testdir.makepyfile(
            """
            assert True
            """
        )

        # run pytest with the following cmd args
        result = testdir.runpytest(BDD_MARKERS_OPT, "-v")

        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines([f"*{CLASSES_OK_HEADLINE}*", f"*{BDD_MARKED_OK_HEADLINE}*", "*no tests ran in *"])

        # make sure that that we get a '0' exit code for the testsuite
        assert result.ret == EXIT_CODE_SUCCESS

    def test_help_message(self, testdir):
        result = testdir.runpytest("--help")
        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines(
            [
                "Markers presence:*",
                f"*{STAGE_MARKERS_OPT}*Stage project with markers based on directories names",
                "*in 'tests' folder",
                f"*{BDD_MARKERS_OPT}*Show not classified functions usage and items without",
                "*Allure BDD tags",
                f"*{ASSERT_STEPS_OPT}*Represent assertion comparisons with Allure steps",
            ]
        )

    def test_fixture_not_affected(self, testdir):
        testdir.makepyfile(
            """
            import pytest
            @pytest.fixture
            def fixture_def():
                return True
            """
        )
        result = testdir.runpytest(BDD_MARKERS_OPT)
        result.stdout.fnmatch_lines([f"*{CLASSES_OK_HEADLINE}*", f"*{BDD_MARKED_OK_HEADLINE}*", "*no tests ran in *"])
        assert result.ret == EXIT_CODE_SUCCESS

    @pytest.mark.parametrize("framework", ["behave", "pytest_bdd"])
    @pytest.mark.parametrize("bdd_step", ["given", "when", "then"])
    def test_bdd_step_not_affected(self, testdir, framework, bdd_step):
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
        result = testdir.runpytest(BDD_MARKERS_OPT)
        result.stdout.fnmatch_lines([f"*{CLASSES_OK_HEADLINE}*", f"*{BDD_MARKED_OK_HEADLINE}*", "*no tests ran in *"])
        assert result.ret == EXIT_CODE_SUCCESS


class TestMarkersPresenceNegative:
    def test_bdd_markers_simple(self, testdir):
        """Make sure that pytest fails session with our fixtures."""

        testdir.makepyfile(
            """
            class TestClass:
                def test_case(self):
                    assert True
            """
        )
        result = testdir.runpytest(BDD_MARKERS_OPT)
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

    def test_markers_without_class(self, testdir):
        """Make sure that pytest fails session with our fixtures."""

        testdir.makepyfile(
            """
            def test_case():
                assert True
            """
        )
        result = testdir.runpytest(BDD_MARKERS_OPT)
        result.stdout.fnmatch_lines(
            [
                f"*{NOT_CLASSIFIED_FUNCTIONS_HEADLINE}*",
                f"*{NO_STORY_FUNCTIONS_HEADLINE}*",
                "*test_case*",
                "*no tests ran in *",
            ]
        )
        assert result.ret == EXIT_CODE_ERROR

    def test_complex_assert(self, testdir):
        """Make sure that pytest fails session with our fixtures."""

        testdir.makepyfile(
            """
            x = 1
            y = 2
            def test_case():
                assert x == y
            """
        )
        result = testdir.runpytest(ASSERT_STEPS_OPT)
        result.stdout.fnmatch_lines(
            [f"*assert \"1 == 2\"", f"*{ASSERTION_FAILED_MESSAGE}*", "*AssertionError", "*1 failed in*"]
        )
        assert result.ret == pytest.ExitCode.TESTS_FAILED

    def test_assert_false(self, testdir):
        testdir.makepyfile(
            """
            def test_case():
                assert False
            """
        )
        result = testdir.runpytest(ASSERT_STEPS_OPT)
        result.stdout.fnmatch_lines([f"*assert False", "*AssertionError", "*1 failed in*"])
        assert result.ret == pytest.ExitCode.TESTS_FAILED
