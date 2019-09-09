# -*- coding: utf-8 -*-
import pytest

from pytest_markers_presence import EXIT_CODE_ERROR, EXIT_CODE_SUCCESS


@pytest.mark.presence_ignore
class TestMarkersPresence:
    @pytest.mark.parametrize(
        ("option", "msg"), [("--bdd-markers", "Cool, every test class with its functions is marked with BDD tags")]
    )
    def test_empty_bdd_markers(self, testdir, option, msg):
        """Make sure that pytest accepts 'bdd-markers' fixtures."""

        # create a temporary pytest test module
        testdir.makepyfile(
            """
            assert True
            """
        )

        # run pytest with the following cmd args
        result = testdir.runpytest(option, "-v")

        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines(["*{}.".format(msg), "*no tests ran in *"])

        # make sure that that we get a '0' exit code for the testsuite
        assert result.ret == EXIT_CODE_SUCCESS

    @pytest.mark.parametrize("option", ["--stage-markers"])
    def test_empty_stage_markers(self, testdir, option):
        """Make sure that pytest accepts 'stage-markers' fixture."""

        # create a temporary pytest test module
        testdir.makepyfile(
            """
            assert True
            """
        )
        result = testdir.runpytest(option, "-v")
        result.stdout.fnmatch_lines(["*no tests ran in *"])
        assert result.ret == 5  # no tests collected

    def test_help_message(self, testdir):
        result = testdir.runpytest("--help")
        # fnmatch_lines does an assertion internally
        result.stdout.fnmatch_lines(
            [
                "Markers presence:*",
                "*--stage-markers*Stage project with markers based on directories names",
                "*in 'tests' folder",
                "*--bdd-markers*Show not classified functions usage and items without",
                "*Allure BDD tags",
            ]
        )

    @pytest.mark.parametrize("option", ["--bdd-markers"])
    def test_markers_with_class(self, testdir, option):
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
                "*You should set BDD tag '@allure.feature'*",
                "*You should set BDD tag '@allure.story'*",
                "*no tests ran in *",
            ]
        )
        assert result.ret == EXIT_CODE_ERROR

    @pytest.mark.parametrize(
        ("option", "msg"),
        [
            ("--bdd-markers", "You should create test class(es) for your test function(s):"),
            ("--bdd-markers", "You should set BDD tag '@allure.story'"),
        ],
    )
    def test_markers_without_class(self, testdir, option, msg):
        """Make sure that pytest fails session with our fixtures."""

        testdir.makepyfile(
            """
            def test_case(self):
                assert True
            """
        )
        result = testdir.runpytest(option)
        result.stdout.fnmatch_lines(["*{}*".format(msg), "*no tests ran in *"])
        assert result.ret == EXIT_CODE_ERROR

    @pytest.mark.parametrize("option", ["--bdd-markers"])
    def test_bdd_markers_complex(self, testdir, option):
        """Make sure that pytest fails session with our fixtures."""

        testdir.makepyfile(
            """
            class TestClass:
                def test_case1(self):
                    assert True
            
            def test_case2(self):
                assert True
            """
        )
        result = testdir.runpytest(option)
        result.stdout.fnmatch_lines(
            ["You should create test class(es) for your test function(s):", "*test_case2*", "*no tests ran in *"]
        )
        assert result.ret == EXIT_CODE_ERROR

    @pytest.mark.parametrize("option", ["--bdd-markers"])
    def test_markers_not_classified_only(self, testdir, option):
        testdir.makepyfile(
            """
            import pytest
            
            class TestClass:
                def test_case(self):
                    assert True
            """
        )
        result = testdir.runpytest(option)
        result.stdout.fnmatch_lines(
            [
                "*You should set BDD tag '@allure.feature' for your test class(es)*",
                "*You should set BDD tag '@allure.story' for your test function(s)*",
            ]
        )
        assert result.ret == EXIT_CODE_ERROR

    @pytest.mark.parametrize("option", ["--bdd-markers"])
    @pytest.mark.parametrize("msg", ["Test function: 'test_case'"])
    def test_bdd_markers_feature_only(self, testdir, option, msg):
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
        result.stdout.fnmatch_lines(["*{}*".format(msg), "*no tests ran in *"])
        assert result.ret == EXIT_CODE_ERROR

    @pytest.mark.parametrize("option", ["--bdd-markers"])
    @pytest.mark.parametrize("msg", ["Test class: 'TestClass'"])
    def test_bdd_markers_story_only(self, testdir, option, msg):
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
        result.stdout.fnmatch_lines(["*{}*".format(msg), "*no tests ran in *"])
        assert result.ret == EXIT_CODE_ERROR

    '''
    @pytest.mark.parametrize("option", ["--bdd-markers"])
    @pytest.mark.parametrize("msg", ["Cool, every test class with its functions is marked with BDD tags"])
    def test_bdd_markers_correct_format(self, testdir, option, msg):
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
        result.stdout.fnmatch_lines(["*{}*".format(msg), "*no tests ran in *"])
        assert result.ret == EXIT_CODE_SUCCESS
    
    
    @pytest.mark.parametrize("options", ["--bdd-markers"])
    def test_all_markers_together(self, testdir, options, tag):
        testdir.makepyfile(
            """
            import allure
            import pytest
            @allure.feature("feature")
            class TestClass:
                @allure.story("story")
                def test_case(self):
                    assert True
            """.format(
                tag
            )
        )
        result = testdir.runpytest(*options)
        result.stdout.fnmatch_lines(
            [
                "*Cool, every function is classified*",
                "*Cool, every test class with its functions is marked with BDD tags*",
                "*no tests ran in *",
            ]
        )
        assert result.ret == EXIT_CODE_SUCCESS
    
    
    @pytest.mark.parametrize("options", ["--bdd-markers"])
    def test_fixture_not_affected(self, testdir, options):
        testdir.makepyfile(
            """
            import pytest
            @pytest.fixture()
            def fixture_def():
                return True
            """
        )
        result = testdir.runpytest(*options)
        result.stdout.fnmatch_lines(
            [
                "*Cool, every test class with its functions is marked with BDD tags*",
                "*no tests ran in *",
            ]
        )
        assert result.ret == EXIT_CODE_SUCCESS
    
    
    @pytest.mark.parametrize("options", ["--bdd-markers"])
    def test_yml_not_affected(self, testdir, options):
        testdir.makefile(
            ".yml",
            """
            test_name: name
            stages:
              - name: test
            """,
        )
    
        result = testdir.runpytest(*options)
        result.stdout.fnmatch_lines(
            [
                "*Cool, every test class with its functions is marked with BDD tags*",
                "*no tests ran in *",
            ]
        )
        assert result.ret == EXIT_CODE_SUCCESS
    
    
    @pytest.mark.parametrize("options", ["--bdd-markers"])
    @pytest.mark.parametrize("framework", ["behave", "pytest_bdd"])
    @pytest.mark.parametrize("bdd_step", ["given", "when", "then"])
    def test_bdd_step_not_affected(self, testdir, options, framework, bdd_step):
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
        result = testdir.runpytest(*options)
        result.stdout.fnmatch_lines(
            [
                "*Cool, every test class is staged, functions are classified*",
                "*Cool, every test class with its functions is marked with BDD tags*",
                "*no tests ran in *",
            ]
        )
        assert result.ret == EXIT_CODE_SUCCESS
    '''
