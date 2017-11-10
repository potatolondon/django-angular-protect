#!/usr/bin/env python3
import os
import sys
import subprocess

this_dir = os.path.dirname(os.path.abspath(__file__))
libs = os.path.join(this_dir, "libs")

if not os.path.exists(libs):
    os.makedirs(libs)

    subprocess.check_call(
        "pip install -t {} -r requirements-dev.txt".format(libs).split()
    )

sys.path.insert(1, libs)

import django
from django.conf import settings

settings.configure(
    DEBUG = True,
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        }
    },
    ROOT_URLCONF = 'angular.urls',
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        'angular',
    )
)

django.setup()

from django.test.runner import DiscoverRunner
test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests(['tests'])
if failures:
    sys.exit(failures)
