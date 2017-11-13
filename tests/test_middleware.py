from django.conf.urls import url
from django.core.exceptions import SuspiciousOperation
from django.template import Template
from django.test import TestCase, override_settings, modify_settings

from django.shortcuts import render
from angular.shortcuts import render as ng_render


def bad_django_view(request):
    return render(request, "home.html", {})


def good_django_view(request):
    return ng_render(request, "home.html", {})


urlpatterns = [
    url("^bad_view/$", bad_django_view),
    url("^good_view/$", good_django_view)
]


@override_settings(ROOT_URLCONF=__name__, DEBUG=True)
@modify_settings(MIDDLEWARE_CLASSES={
    'append': 'angular.middleware.EnsureAngularProtectionMiddleware'
})
class MiddlewareTests(TestCase):
    def test_middleware_flags_django_render(self):

        with self.assertRaises(SuspiciousOperation):
            self.client.get("/bad_view/")

        try:
            self.client.get("/good_view/")
        except SuspiciousOperation:
            self.fail("Good view incorrectly threw SuspiciousOperation")
