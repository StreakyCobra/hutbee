# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name="hutbee",
    version="0.0.1",
    description="Control and monitor your mountain hut remotely",
    author="Fabien Dubosson",
    author_email="fabien.dubosson@gmail.com",
    url="https://github.com/StreakyCobra/hutbee",
    packages=find_packages(),
    install_requires=["flask-cors~=3.0", "flask~=1.1", "python-dotenv~=0.10"],
)
