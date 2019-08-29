# -*- coding: utf-8 -*-


def test_bar_fixture(testdir):
    """Make sure that pytest accepts our fixture."""

    # create a temporary pytest test module
    testdir.makepyfile("""
        def test_sth(bar):
            assert True
    """)

    # run pytest with the following cmd args
    result = testdir.runpytest(
        '--stage-markers',
        '-v'
    )

    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        '*Cool, every test class is staged.',
        '*no tests ran in *'
    ])

    # make sure that that we get a '0' exit code for the testsuite
    assert result.ret == 0


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
