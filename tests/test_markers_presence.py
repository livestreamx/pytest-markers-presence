# -*- coding: utf-8 -*-
import pytest
from pytest_markers_presence import EXIT_CODE_ERROR, EXIT_CODE_SUCCESS, STAGE_MARKERS


@pytest.mark.parametrize(('option', 'msg'), [('--stage-markers', 'Cool, every test class is staged'), (
        '--bdd-markers', 'Cool, every test class with its functions is marked with BDD tags')])
def test_markers(testdir, option, msg):
    """Make sure that pytest accepts our fixtures."""

    # create a temporary pytest test module
    testdir.makepyfile("""
        assert True
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest(option, '-v')

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*{}.'.format(msg),
        '*no tests ran in *'
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == EXIT_CODE_SUCCESS


def test_help_message(testdir):
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'markers-presence:*',
        '*--stage-markers*Show not staged classes',
        '*--bdd-markers*Show items without allure BDD markers'
    ])


@pytest.mark.parametrize(('option', 'msg'), [('--stage-markers', 'You should set stage marker'), (
        '--bdd-markers', 'You should set BDD marker \'@allure.feature\''),
                                             ('--bdd-markers', 'You should set BDD marker \'@allure.story\'')])
def test_markers_in_work(testdir, option, msg):
    """Make sure that pytest fails session with our fixtures."""

    testdir.makepyfile(
        """
        class TestClass:
            def test_case(self):
                assert True
        """
    )
    result = testdir.runpytest(option)
    result.stdout.fnmatch_lines([
        '*{}*'.format(msg),
        '*no tests ran in *'
    ])
    assert result.ret == EXIT_CODE_ERROR


@pytest.mark.parametrize('option', ['--stage-markers'])
@pytest.mark.parametrize('tag', STAGE_MARKERS)
@pytest.mark.parametrize('msg', ['Cool, every test class is staged.'])
def test_stage_markers_only(testdir, option, tag, msg):
    testdir.makepyfile(
        """
        import pytest
        @pytest.mark.{}
        class TestClass:
            def test_case(self):
                assert True
        """.format(tag)
    )
    result = testdir.runpytest(option)
    result.stdout.fnmatch_lines([
        '*{}*'.format(msg),
        '*no tests ran in *'
    ])
    assert result.ret == EXIT_CODE_SUCCESS


@pytest.mark.parametrize('option', ['--bdd-markers'])
@pytest.mark.parametrize('msg', ['Test case name: \'test_case\''])
def test_bdd_markers_feature_only(testdir, option, msg):
    testdir.makepyfile(
        """
        import allure
        import pytest
        @allure.feature("feature")
        class TestClass:
            def test_case(self):
                assert True
        """
    )
    result = testdir.runpytest(option)
    result.stdout.fnmatch_lines([
        '*{}*'.format(msg),
        '*no tests ran in *'
    ])
    assert result.ret == EXIT_CODE_ERROR


@pytest.mark.parametrize('option', ['--bdd-markers'])
@pytest.mark.parametrize('msg', ['Test class name: \'TestClass\''])
def test_bdd_markers_story_only(testdir, option, msg):
    testdir.makepyfile(
        """
        import allure
        import pytest
        class TestClass:
            @allure.story("story")
            def test_case(self):
                assert True
        """
    )
    result = testdir.runpytest(option)
    result.stdout.fnmatch_lines([
        '*{}*'.format(msg),
        '*no tests ran in *'
    ])
    assert result.ret == EXIT_CODE_ERROR


@pytest.mark.parametrize('option', ['--bdd-markers'])
@pytest.mark.parametrize('msg', ['Cool, every test class with its functions is marked with BDD tags'])
def test_bdd_markers_only(testdir, option, msg):
    testdir.makepyfile(
        """
        import allure
        import pytest
        @allure.feature("feature")
        class TestClass:
            @allure.story("story")
            def test_case(self):
                assert True
        """
    )
    result = testdir.runpytest(option)
    result.stdout.fnmatch_lines([
        '*{}*'.format(msg),
        '*no tests ran in *'
    ])
    assert result.ret == EXIT_CODE_SUCCESS


@pytest.mark.parametrize('options', [('--stage-markers', '--bdd-markers')])
@pytest.mark.parametrize('tag', STAGE_MARKERS)
def test_all_markers_together(testdir, options, tag):
    testdir.makepyfile(
        """
        import allure
        import pytest
        @pytest.mark.{}
        @allure.feature("feature")
        class TestClass:
            @allure.story("story")
            def test_case(self):
                assert True
        """.format(tag)
    )
    result = testdir.runpytest(*options)
    result.stdout.fnmatch_lines([
        '*Cool, every test class is staged*',
        '*Cool, every test class with its functions is marked with BDD tags*',
        '*no tests ran in *'
    ])
    assert result.ret == EXIT_CODE_SUCCESS
