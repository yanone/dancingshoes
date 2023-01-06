#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = []

setup(
    name="dancingshoes",
    version="0.1.4",
    description="",
    author="Yanone",
    author_email="post@yanone.de",
    url="https://github.com/yanone",
    install_requires=install_requires,
    package_dir={"": "Lib"},
    packages=find_packages("Lib"),
    include_package_data=True,
)
