# -*- coding: utf-8 -*-
import pytest

from pytest_markers_presence import (
    ASSERT_STEPS_HELP,
    ASSERTION_FAILED_MESSAGE,
    BDD_FORMAT_HELP,
    BDD_MARKED_OK_HEADLINE,
    FEATURE_TITLE_MARKED_OK_HEADLINE,
    CLASSES_OK_HEADLINE,
    FAIL_ON_ALL_SKIPPED_HELP,
    NO_FEATURE_CLASSES_HEADLINE,
    NO_STORY_FUNCTIONS_HEADLINE,
    NO_TITLE_FUNCTIONS_HEADLINE,
    NOT_CLASSIFIED_FUNCTIONS_HEADLINE,
    STAGING_HELP,
    STAGING_WARNINGS_HELP,
    FEATURE_TITLE_HELP,
    UNIT_TESTS_MARKER,
    ExitCodes,
    Options,
)

_DEFAULT_HELP_CHECKING_LENGTH = 40


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

        # make sure that we get a '0' exit code for the testsuite
        assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED

    def test_empty_assertions(self, testdir):
        f"""Make sure that pytest accepts '{Options.ASSERT_STEPS}' fixture"""
        testdir.makepyfile(
            """
            assert True
            """
        )
        result = testdir.runpytest(Options.ASSERT_STEPS, "-v")
        assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED

    @pytest.mark.parametrize(
        ("option", "message"),
        [
            pytest.param(Options.BDD_FORMAT, BDD_MARKED_OK_HEADLINE),
            pytest.param(Options.FEATURE_TITLE, FEATURE_TITLE_MARKED_OK_HEADLINE),
        ],
    )
    def test_empty_linter_markers(self, testdir, option, message):
        f"""Make sure that pytest accepts '{option}' fixture"""

        # create a temporary pytest test module
        testdir.makepyfile(
            """
            assert True
            """
        )

        # run pytest with the following cmd args
        result = testdir.runpytest(option, "-v")

        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines(
            [
                f"*{CLASSES_OK_HEADLINE}*",
                f"*{message}*",
                "*no tests ran in *",
            ]
        )

        # make sure that we get a '0' exit code for the testsuite
        assert result.ret == ExitCodes.SUCCESS

    @pytest.mark.parametrize(
        ("option", "message", "tag"),
        [
            pytest.param(Options.BDD_FORMAT, BDD_MARKED_OK_HEADLINE, "@allure.story('Story')"),
            pytest.param(Options.FEATURE_TITLE, FEATURE_TITLE_MARKED_OK_HEADLINE, "@allure.title('Title')"),
        ],
    )
    def test_success_linter_markers(self, testdir, option, message, tag):
        f"""Make sure that pytest accepts '{option}' fixture"""

        # create a temporary pytest test module
        testdir.makepyfile(
            f"""
            import allure
            
            @allure.feature('Feature')
            class TestFeature:
                {tag}
                def test_func(self):
                    assert True
            """
        )

        # run pytest with the following cmd args
        result = testdir.runpytest(option, "-v")

        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines(
            [
                f"*{CLASSES_OK_HEADLINE}*",
                f"*{message}*",
                "*no tests ran in *",
            ]
        )

        # make sure that we get a '0' exit code for the testsuite
        assert result.ret == ExitCodes.SUCCESS

    def test_empty_fail_on_all_skipped(self, testdir):
        f"""Make sure that pytest accepts '{Options.FAIL_ON_ALL_SKIPPED}' fixture"""
        testdir.makepyfile(
            """
            assert True
            """
        )
        result = testdir.runpytest(Options.FAIL_ON_ALL_SKIPPED, "-v")
        assert result.ret == pytest.ExitCode.NO_TESTS_COLLECTED

    def test_help_message(self, testdir):
        result = testdir.runpytest("--help")
        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines(
            [
                "Markers presence:*",
                f"*{Options.STAGING}*{STAGING_HELP[:_DEFAULT_HELP_CHECKING_LENGTH]}*",
                f"*{Options.ASSERT_STEPS}*{ASSERT_STEPS_HELP[:_DEFAULT_HELP_CHECKING_LENGTH]}*",
                f"*{Options.BDD_FORMAT}*{BDD_FORMAT_HELP[:_DEFAULT_HELP_CHECKING_LENGTH]}*",
                f"*{Options.FEATURE_TITLE}*{FEATURE_TITLE_HELP[:_DEFAULT_HELP_CHECKING_LENGTH]}*",
                f"*{Options.WARNINGS}*{STAGING_WARNINGS_HELP[:_DEFAULT_HELP_CHECKING_LENGTH]}*",
                f"*{Options.FAIL_ON_ALL_SKIPPED}*{FAIL_ON_ALL_SKIPPED_HELP[:_DEFAULT_HELP_CHECKING_LENGTH]}*",
            ]
        )

    @pytest.mark.parametrize(
        ("option", "message"),
        [
            pytest.param(Options.BDD_FORMAT, BDD_MARKED_OK_HEADLINE),
            pytest.param(Options.FEATURE_TITLE, FEATURE_TITLE_MARKED_OK_HEADLINE),
        ],
    )
    def test_fixture_not_affected(self, testdir, option, message):
        testdir.makepyfile(
            """
            import pytest
            @pytest.fixture
            def fixture_def():
                return True
            """
        )
        result = testdir.runpytest(option)
        result.stdout.fnmatch_lines(
            [
                f"*{CLASSES_OK_HEADLINE}*",
                f"*{message}*",
                "*no tests ran in *",
            ]
        )
        assert result.ret == ExitCodes.SUCCESS

    @pytest.mark.parametrize("framework", ["behave", "pytest_bdd"])
    @pytest.mark.parametrize("bdd_step", ["given", "when", "then"])
    @pytest.mark.parametrize(
        ("option", "message"),
        [
            pytest.param(Options.BDD_FORMAT, BDD_MARKED_OK_HEADLINE),
            pytest.param(Options.FEATURE_TITLE, FEATURE_TITLE_MARKED_OK_HEADLINE),
        ],
    )
    def test_bdd_step_not_affected(self, testdir, framework, bdd_step, option, message):
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
        result = testdir.runpytest(option)
        result.stdout.fnmatch_lines(
            [
                f"*{CLASSES_OK_HEADLINE}*",
                f"*{message}*",
                "*no tests ran in *",
            ]
        )
        assert result.ret == ExitCodes.SUCCESS


class TestMarkersPresenceNegative:
    @pytest.mark.parametrize(
        ("option", "message"),
        [
            pytest.param(Options.BDD_FORMAT, NO_STORY_FUNCTIONS_HEADLINE),
            pytest.param(Options.FEATURE_TITLE, NO_TITLE_FUNCTIONS_HEADLINE),
        ],
    )
    def test_linter_markers_simple(self, testdir, option, message):
        """Make sure that pytest fails session with our fixtures."""

        testdir.makepyfile(
            """
            class TestClass:
                def test_case(self):
                    assert True
            """
        )
        result = testdir.runpytest(option)
        result.stdout.fnmatch_lines(
            [
                f"*{NO_FEATURE_CLASSES_HEADLINE}*",
                "Test class*TestClass*",
                f"*{message}*",
                "Test function*test_case*",
                "*no tests ran in *",
            ]
        )
        assert result.ret == ExitCodes.ERROR

    @pytest.mark.parametrize(
        ("option", "message"),
        [
            pytest.param(Options.BDD_FORMAT, NO_STORY_FUNCTIONS_HEADLINE),
            pytest.param(Options.FEATURE_TITLE, NO_TITLE_FUNCTIONS_HEADLINE),
        ],
    )
    def test_markers_without_class(self, testdir, option, message):
        """Make sure that pytest fails session with our fixtures."""

        testdir.makepyfile(
            """
            def test_case():
                assert True
            """
        )
        result = testdir.runpytest(option)
        result.stdout.fnmatch_lines(
            [
                f"*{NOT_CLASSIFIED_FUNCTIONS_HEADLINE}*",
                f"*{message}*",
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
                "very very very long string, i can not see the end!..",
                "other very very very long string, i can not see the end again!..",
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
        result.stdout.fnmatch_lines([f"*- {str_y}*", f"*+ {str_x}*", "*AssertionError", "*1 failed in*"])
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
                f"*assert \"attr_1=1 attr_2='{str_attr}' == attr_1=1 attr_2='err'\"",
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

    @pytest.mark.parametrize(
        ("str_bool", "exit_code"),
        [("True", pytest.ExitCode.OK), ("False", pytest.ExitCode.TESTS_FAILED)],
    )
    def test_fail_on_all_skipped_when_no_skip(self, testdir, str_bool, exit_code):
        testdir.makepyfile(
            (
                """
                def test_case():
                    assert {str_bool}
                """
            ).format(str_bool=str_bool)
        )
        result = testdir.runpytest(Options.FAIL_ON_ALL_SKIPPED, "-v")
        assert result.ret == exit_code

    def test_fail_on_all_skipped_when_skip(self, testdir):
        testdir.makepyfile(
            """
            import pytest
            def test_case():
                pytest.skip('kek')
            """
        )
        result = testdir.runpytest(Options.FAIL_ON_ALL_SKIPPED, "-v")
        assert result.ret == pytest.ExitCode.TESTS_FAILED
