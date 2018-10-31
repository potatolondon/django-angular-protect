from __future__ import unicode_literals

from django.conf import settings
from django.core.exceptions import SuspiciousOperation


_NG_APP_MARKER = getattr(settings, "NG_APP_MARKER", "ng-app")
_NG_SAFE_ATTRIBUTE = "_ng_safe"


class EnsureAngularProtectionMiddleware(object):
    """
        If settings.DEBUG is True, this middleware detects whether returned HTML content
        contains the ng-app directive.

        If it does, and the response wasn't rendered with `angular.shortcuts.render()`
        a SuspiciousOperation error is thrown.

        This exists to prevent accidental bypass of the protection that `render()` provides.
    """

    def process_response(self, request, response):
        if not settings.DEBUG or 'text/html' not in response.get('Content-Type', ''):
            return response

        def check_content(content):
            # Content is raw bytes, not unicode
            if _NG_APP_MARKER.encode() in content:
                if not getattr(response, _NG_SAFE_ATTRIBUTE, False):
                    raise SuspiciousOperation(
                        ("Angular template not rendered with angular.shorcuts.render or "
                         "attempt to access Django context in protected area.")
                    )
            return content

        if response.streaming:
            def wrap_streaming_content(content):
                for chunk in content:
                    yield check_content(content)

            response.streaming_content = wrap_streaming_content(response.streaming_content)
        else:
            response.content = check_content(response.content)

        return response
