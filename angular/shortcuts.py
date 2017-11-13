from __future__ import unicode_literals

import threading

from django.utils.encoding import python_2_unicode_compatible
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render as django_render


@python_2_unicode_compatible
class AngularContextValue(object):
    """
        Wraps a value from the Django context, but evalutes
        to an empty string when printed. If the mark_ng_safe
        filter is applied to this then the original value is returned
    """
    def __init__(self, original):
        self._original = original

    def __getattr__(self, name):
        value = getattr(self._original, name)
        if _local.ng_protected:
            return AngularContextValue(value)
        return value

    def __getitem__(self, name):
        value = self._original[name]
        if _local.ng_protected:
            return AngularContextValue(value)
        return value

    def __str__(self):
        if _local.ng_protected:
            if settings.DEBUG:
                raise SuspiciousOperation("Attempted to access Django context in protected area")
            else:
                return ""
        else:
            return str(self._original)


_local = threading.local()

def render(request, template_name, context=None, **kwargs):
    """
        Calls through to django.shortcuts.render but wraps the passed context
        in an AngularSafeContext object which by default will not allow access
        to the context unless inside a {% django_block %} template tag (which
        will ensure ng-non-bindable has been applied).
    """

    context = context.copy() or {}

    def make_safe(ctx):
        for k in ctx:
            ctx[k] = AngularContextValue(ctx[k])
        return ctx

    context = make_safe(context)
    context["is_angular_template"] = True

    try:
        _local.ng_protected = True

        response = django_render(
            request,
            template_name,
            context,
            **kwargs
        )
    finally:
        delattr(_local, "ng_protected")

    response._ng_safe = True
    return response
