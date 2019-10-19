# -*- coding: utf-8 -*-
import pytest

from pytest_markers_presence import (
    Options,
    ExitCodes,
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
        ), f"I am sure - these tests are not marked as '{UNIT_TESTS_MARKER}' with option '{Options.STAGING}'!"

    def test_empty_stage_markers(self, testdir):
        f"""Make sure that pytest accepts '{Options.STAGING}' fixture"""

        # create a temporary pytest test module
        testdir.makepyfile(
            """
            assert True
            """
        )

        # run pytest with the following cmd args
        result = testdir.runpytest(Options.STAGING, "-v")

        # make sure that that we get a '0' exit code for the testsuite
        assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED

    def test_empty_assertions(self, testdir):
        f"""Make sure that pytest accepts '{Options.ASSERT_STEPS}' fixture"""

        # create a temporary pytest test module
        testdir.makepyfile(
            """
            assert True
            """
        )

        # run pytest with the following cmd args
        result = testdir.runpytest(Options.ASSERT_STEPS, "-v")

        # make sure that that we get a '0' exit code for the testsuite
        assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED

    def test_empty_titles(self, testdir):
        f"""Make sure that pytest accepts '{Options.BDD_TITLES}' fixture"""

        # create a temporary pytest test module
        testdir.makepyfile(
            """
            assert True
            """
        )

        # run pytest with the following cmd args
        result = testdir.runpytest(Options.BDD_TITLES, "-v")

        # make sure that that we get a '0' exit code for the testsuite
        assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED

    def test_empty_bdd_markers(self, testdir):
        f"""Make sure that pytest accepts '{Options.BDD_FORMAT}' fixture"""

        # create a temporary pytest test module
        testdir.makepyfile(
            """
            assert True
            """
        )

        # run pytest with the following cmd args
        result = testdir.runpytest(Options.BDD_FORMAT, "-v")

        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines([f"*{CLASSES_OK_HEADLINE}*", f"*{BDD_MARKED_OK_HEADLINE}*", "*no tests ran in *"])

        # make sure that that we get a '0' exit code for the testsuite
        assert result.ret == ExitCodes.SUCCESS

    def test_help_message(self, testdir):
        result = testdir.runpytest("--help")
        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines(
            [
                "Markers presence:*",
                f"*{Options.STAGING}*Stage project with markers based on directories names*",
                f"*{Options.ASSERT_STEPS}*Represent assertion comparisons with Allure steps*",
                f"*{Options.BDD_TITLES}*Set Allure titles for BDD test scenarios*",
                f"*{Options.BDD_FORMAT}*Show not classified functions usage*",
                f"*{Options.WARNINGS}*Enable warnings for staging*",
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
        result = testdir.runpytest(Options.BDD_FORMAT)
        result.stdout.fnmatch_lines([f"*{CLASSES_OK_HEADLINE}*", f"*{BDD_MARKED_OK_HEADLINE}*", "*no tests ran in *"])
        assert result.ret == ExitCodes.SUCCESS

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
        result = testdir.runpytest(Options.BDD_FORMAT)
        result.stdout.fnmatch_lines([f"*{CLASSES_OK_HEADLINE}*", f"*{BDD_MARKED_OK_HEADLINE}*", "*no tests ran in *"])
        assert result.ret == ExitCodes.SUCCESS


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
        result = testdir.runpytest(Options.BDD_FORMAT)
        result.stdout.fnmatch_lines(
            [
                f"*{NO_FEATURE_CLASSES_HEADLINE}*",
                "Test class*TestClass*",
                f"*{NO_STORY_FUNCTIONS_HEADLINE}*",
                "Test function*test_case*",
                "*no tests ran in *",
            ]
        )
        assert result.ret == ExitCodes.ERROR

    def test_markers_without_class(self, testdir):
        """Make sure that pytest fails session with our fixtures."""

        testdir.makepyfile(
            """
            def test_case():
                assert True
            """
        )
        result = testdir.runpytest(Options.BDD_FORMAT)
        result.stdout.fnmatch_lines(
            [
                f"*{NOT_CLASSIFIED_FUNCTIONS_HEADLINE}*",
                f"*{NO_STORY_FUNCTIONS_HEADLINE}*",
                "*test_case*",
                "*no tests ran in *",
            ]
        )
        assert result.ret == ExitCodes.ERROR

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
        result = testdir.runpytest(Options.ASSERT_STEPS)
        result.stdout.fnmatch_lines([f"*assert 1 == 2", "*AssertionError", "*1 failed in*"])
        assert result.ret == pytest.ExitCode.TESTS_FAILED

    def test_assert_false(self, testdir):
        testdir.makepyfile(
            """
            def test_case():
                assert False
            """
        )
        result = testdir.runpytest(Options.ASSERT_STEPS)
        result.stdout.fnmatch_lines([f"*assert False", "*AssertionError", "*1 failed in*"])
        assert result.ret == pytest.ExitCode.TESTS_FAILED

    @pytest.mark.parametrize(
        ("str_x, str_y"),
        [
            (
                'very very very long string, i can not see the end!..',
                'other very very very long string, i can not see the end again!..',
            )
        ],
    )
    def test_assert_long_strings(self, testdir, str_x, str_y):
        testdir.makepyfile(
            """
            x = '{str_x}'
            y = '{str_y}'
            def test_case():
                assert x == y
            """.format(
                str_x=str_x, str_y=str_y
            )
        )
        result = testdir.runpytest(Options.ASSERT_STEPS)
        result.stdout.fnmatch_lines([f"*- {str_x}*", f"*+ {str_y}*", "*AssertionError", "*1 failed in*"])
        assert result.ret == pytest.ExitCode.TESTS_FAILED

    @pytest.mark.parametrize("str_attr", ["tst", "very very very long string, i can not see the end!.."])
    def test_assert_base_model(self, testdir, str_attr):
        testdir.makepyfile(
            """
            from pydantic import BaseModel
            
            class Cls(BaseModel):
                attr_1: int
                attr_2: str
                
            x = Cls(attr_1 = 1, attr_2 = '{str}')
            y = Cls(attr_1 = 1, attr_2 = 'err')
            
            def test_case():
                assert x == y
            """.format(
                str=str_attr
            )
        )
        result = testdir.runpytest(Options.ASSERT_STEPS)
        result.stdout.fnmatch_lines(
            [
                f"*assert \"Cls attr_1=1 attr_2='{str_attr}' == Cls attr_1=1 attr_2='err'\"",
                f"*{ASSERTION_FAILED_MESSAGE}*",
                "*AssertionError",
                "*1 failed in*",
            ]
        )
        assert result.ret == pytest.ExitCode.TESTS_FAILED

    def test_assert_dict(self, testdir):
        testdir.makepyfile(
            """
            x = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
            y = {"a": 1, "b": 2, "c": 3, "d": 4, "f": 6}

            def test_case():
                assert x == y
            """
        )
        result = testdir.runpytest(Options.ASSERT_STEPS)
        result.stdout.fnmatch_lines([f"*Omitting 4 identical items*", "*AssertionError", "*1 failed in*"])
        assert result.ret == pytest.ExitCode.TESTS_FAILED

    @pytest.mark.parametrize("str_attr", ["tst", "very very very long string, i can not see the end!.."])
    def test_assert_dataclass(self, testdir, str_attr):
        testdir.makepyfile(
            """
            from pydantic.dataclasses import dataclass
            
            @dataclass
            class Cls1:
                attr_1: str = 'err'
                
            @dataclass
            class Cls2:
                attr_2: str = "{str}"

            x = Cls1()
            y = Cls2()

            def test_case():
                assert x == y
            """.format(
                str=str_attr
            )
        )
        result = testdir.runpytest(Options.ASSERT_STEPS)
        result.stdout.fnmatch_lines(
            [
                f"*assert \"Cls1(attr_1='err') == Cls2(attr_2='{str_attr}')\"",
                f"*{ASSERTION_FAILED_MESSAGE}*",
                "*AssertionError",
                "*1 failed in*",
            ]
        )
        assert result.ret == pytest.ExitCode.TESTS_FAILED
