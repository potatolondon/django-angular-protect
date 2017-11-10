from django.conf import settings
from django.core.exceptions import SuspiciousOperation


_NG_APP_MARKER = "ng-app"
_NG_SAFE_ATTRIBUTE = "_ng_safe"


class EnsureAngularProtectionMiddleware(object):
    """

        If settings.DEBUG is True, this middleware detects whether returned HTML content
        contains the ng-app directive.

        If it does, and the response wasn't rendered with angular.shortcuts.ng_render()
        a SuspiciousOperation error is thrown.

        This exists to prevent accidental bypass of the protection that ng_render provides.
    """

    def process_response(request, response):
        if not settings.DEBUG:
            return response

        def check_content(content):
            if content.find(_NG_APP_MARKER) != -1:
                if not getattr(response, _NG_SAFE_ATTRIBUTE, False):
                    raise SuspiciousOperation(
                        "Angular template not rendered with ng_render"
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
