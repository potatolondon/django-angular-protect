from django.shortcuts import render


class AngularContextValue(object):
    """
        Wraps a value from the Django context, but evalutes
        to an empty string when printed. If the mark_ng_safe
        filter is applied to this then the original value is returned
    """
    def __init__(self, original):
        self._original = original

    def __getattr__(self, name):
        return AngularContextValue(getattr(self._original, name))

    def __unicode__(self):
        return u""


class AngularSafeContext(object):
    """
        A wrapper around a Django context which by default
        performs no substitutions (or rather replaces all substitutions with
        an empty string).

        Access to the context is only granted in the following cases:

        1. You are in a {% djangoblock %} tag
        2. You are using the |mark_ng_safe filter
    """
    is_angular_template = True

    def __init__(self, original):
        # This is set to False by {% django_block %}, and set back to true by
        # {% enddjango_block %}
        self._protected = True

        # Make the original as inaccessible as possible
        self.__original = original

    def __getitem__(self, key):
        if self._protected:
            return AngularContextValue(self.__original[key])
        else:
            return self._original[key]


def ng_render(request, template_name, context=None, **kwargs):
    """
        Calls through to django.shortcuts.render but wraps the passed context
        in an AngularSafeContext object which by default will not allow access
        to the context unless inside a {% django_block %} template tag (which
        will ensure ng-non-bindable has been applied).
    """

    response = render(
        request,
        template_name,
        AngularSafeContext(context)
        **kwargs
    )

    response._ng_safe = True
    return response
