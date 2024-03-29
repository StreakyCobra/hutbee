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
    install_requires=[
        "apscheduler~=3.6",
        "bcrypt~=3.1",
        "decorator~=4.4",
        "flask-cors~=3.0",
        "flask-jwt-extended~=3.24",
        "flask~=1.1",
        "kombu~=5.0.1",
        "logzero~=1.5",
        "pandas~=1.3.5",
        "pymongo~=3.9",
        "python-dotenv~=0.10",
        "python-telegram-bot~=13.8",
        "pytz~=2021.3",
        "requests~=2.22",
        "seaborn~=0.11",
    ],
)
