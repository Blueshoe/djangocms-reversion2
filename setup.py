# -*- coding: utf-8 -*-
from setuptools import find_packages
from distutils.core import setup
from djangocms_reversion2 import __version__

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Framework :: Django',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
]

REQUIREMENTS = [
    'django>=1.8.17,<1.9',
    'django-cms>=3.4.3',
    'diff-match-patch==20110725.1',
    'django-sekizai==0.9.0'
]

setup(
    name='djangocms-reversion2',
    packages=find_packages(exclude=('test_app', 'docs')),
    version=__version__,
    description='page versioning for django-cms',
    author='Daniel Pollithy',
    author_email='daniel@blueshoe.de',
    url='https://github.com/Blueshoe/djangocms-reversion2',
    download_url='https://github.com/Blueshoe/djangocms-reversion2/archive/{}.zip'.format(__version__),
    install_requires=REQUIREMENTS,
    keywords=['django', 'Django CMS', 'version history', 'versioning',
              'reversion', 'revision', 'CMS', 'Blueshoe', 'basket', 'bin', 'revert'],
    classifiers=CLASSIFIERS,
)
