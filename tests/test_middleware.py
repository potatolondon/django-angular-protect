from django.conf.urls import url
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseServerError
from django.template import Template
from django.test import TestCase, override_settings, modify_settings

from django.shortcuts import render
from angular.shortcuts import render as ng_render


def bad_django_view(request):
    return render(request, "home.html", {})


def good_django_view(request):
    return ng_render(request, "home.html", {})

NG_APP_MARKER = 'ng-app-marker'
def errors_django_view(request):
    return HttpResponseServerError(NG_APP_MARKER)


urlpatterns = [
    url("^bad_view/$", bad_django_view),
    url("^good_view/$", good_django_view),

    url("^errors_view/$", errors_django_view),
]


@override_settings(ROOT_URLCONF=__name__, DEBUG=True)
@modify_settings(MIDDLEWARE={
    'append': 'angular.middleware.EnsureAngularProtectionMiddleware'
})
class MiddlewareTests(TestCase):
    def test_middleware_flags_django_render(self):
        response = self.client.get("/bad_view/")
        self.assertEqual(response.status_code, 400)

        response = self.client.get("/good_view/")
        self.assertEqual(response.status_code, 200)

    def test_middleware_ignores_checking_erroring_views(self):
        # It's possible that the ng marker gets injected into the error page e.g.
        # because it's in the settings file.
        # If we have an error response we just ignore any checks.
        with override_settings(NG_APP_MARKER=NG_APP_MARKER):
            response = self.client.get("/errors_view/")
            self.assertEqual(response.status_code, 500)
