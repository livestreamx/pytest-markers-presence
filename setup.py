#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
import re

from setuptools import Command, setup

BASE_PATH = os.path.abspath(os.path.dirname(__file__))


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding="utf-8").read()


def get_version():
    changes_path = os.path.join(BASE_PATH, "CHANGES.rst")
    regex = r"^#*\s*(?P<version>[0-9]+\.[0-9]+(\.[0-9]+)?)$"
    with codecs.open(changes_path, encoding="utf-8") as changes_file:
        for line in changes_file:
            res = re.match(regex, line)
            if res:
                return res.group("version")
    return "0.0.0"


version = get_version()


class VersionCommand(Command):
    description = "print current library version"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        print(version)


setup(
    name="pytest-markers-presence",
    version=version,
    author="Vladislav Mukhamatnurov",
    author_email="livestreamepidemz@yandex.ru",
    maintainer="Vladislav Mukhamatnurov",
    maintainer_email="livestreamepidemz@yandex.ru",
    license="MIT",
    url="https://github.com/livestreamx/pytest-markers-presence",
    description='A simple plugin to detect missed pytest tags and markers"',
    long_description=read("README.rst"),
    py_modules=["pytest_markers_presence"],
    python_requires=">=3.7",
    install_requires=[
        "pytest>=6.0",
        "allure-pytest>=2.8.19",
        "pydantic>=1.2",
        "pytest-bdd>=4.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    cmdclass={"version": VersionCommand},
    entry_points={"pytest11": ["markers-presence = pytest_markers_presence"]},
)
