# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='hipbot',
    version='1.0',
    author='Boberro (Mateusz Cyraniak)',
    author_email='m.cyraniak@gmail.com',
    install_requires=[
        'discord.py==0.10.0a0',
        'google-api-python-client==1.5.1',
    ],
    dependency_links=[
        'git+https://github.com/Rapptz/discord.py@async#egg=discord.py-0.10.0a0',
    ],
)