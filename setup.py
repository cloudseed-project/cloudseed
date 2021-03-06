#!/usr/bin/env python
import os
from setuptools import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


def strip_comments(l):
    return l.split('#', 1)[0].strip()


def reqs(*f):
    return list(filter(None, [strip_comments(l) for l in open(
        os.path.join(os.getcwd(), 'requirements', *f)).readlines()]))

install_requires = reqs('default.txt')
tests_require = ['nose']


packages = [
    'cloudseed',
    'cloudseed.cli',
    'cloudseed.providers',
    'cloudseed.resources',
    'cloudseed.utils',
    'cloudseed.modules'
]

setup(
    name='cloudseed',
    version='0.0.1',
    description='Cloudseed',
    long_description=readme,
    author='Adam Venturella <aventurella@gmail.com>, Dino Petrone <dinopetrone@gmail.com> Aubrey Taylor <aubricus@gmail.com>',
    author_email='aventurella@gmail.com, dinopetrone@gmail.com aubricus@gmail.com',
    url='https://github.com/aventurella/cloudseed',
    license=license,
    packages=packages,
    package_data={'': ['LICENSE'],
                  'cloudseed.masters': ['resources/*.sh'],
                  'cloudseed.minions': ['resources/*.sh']},
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    package_dir={'cloudseed': 'cloudseed'},
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ),

    entry_points={
        'console_scripts': [
            'cloudseed = cloudseed.cli.main:main',
        ],

        'com.cloudseed.providers': [
            'ec2 = cloudseed.providers.ec2:EC2Provider',
        ],
    }
)

