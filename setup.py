import os
from setuptools import setup, find_packages


NAME = 'django-angular-protect'
PACKAGES = find_packages(exclude=["docs", "example", "libs"])
DESCRIPTION = 'Protections against XSS when using Angular with Django'
URL = "https://github.com/potatolondon/django-angular-protect"
LONG_DESCRIPTION = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
AUTHOR = 'Potato London Ltd.'

EXTRAS = {
    "test": ["django"],
}

setup(
    name=NAME,
    version='0.1.0',
    packages=PACKAGES,

    # metadata for upload to PyPI
    author=AUTHOR,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    keywords=["django", "angularjs", "xss"],
    url=URL,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    tests_require=EXTRAS['test'],
)
