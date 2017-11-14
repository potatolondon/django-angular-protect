from django.core.exceptions import SuspiciousOperation
from django.test import TestCase, RequestFactory, override_settings
from angular.shortcuts import render


class DjangoBlockTests(TestCase):

    def test_django_block_inserts_non_bindable(self):
        req = RequestFactory().get("/")
        response = render(req, "django_block.html", {})
        self.assertTrue("<div ng-non-bindable>" in response.content.decode())

    def test_tag_argument(self):
        req = RequestFactory().get("/")
        response = render(req, "django_block.html", {})
        self.assertTrue("<span ng-non-bindable>" in response.content.decode())

    @override_settings(DEBUG=True)
    def test_access_outside_throws_error(self):
        req = RequestFactory().get("/")
        ctx = {
            "test_non_accessible": True,
            "thing": "THING"
        }

        req = RequestFactory().get("/")
        self.assertRaises(SuspiciousOperation, render, req, "django_block.html", ctx)

    def test_django_context_accessible_inside_block(self):
        req = RequestFactory().get("/")

        ctx = {
            "thing": "ROOT_THING",
            "nested": {
                "list": ["LIST_ONE"],
                "thing": "NESTED_THING"
            }
        }
        response = render(req, "django_block.html", ctx)
        content = response.content.decode()

        self.assertTrue("ROOT_THING" in content, content)
        self.assertTrue("LIST_ONE" in content)
        self.assertTrue("NESTED_THING" in content)

