import six

from django.conf import settings
from django import template
from django.core.exceptions import ImproperlyConfigured

from angular.shortcuts import _local

register = template.Library()


class DjangoBlockNode(template.Node):
    """
        Performs two tasks:

        1. Wraps content in <div ng-non-bindable>
        2. Temporarily allows access to the context within the block

        Usage:

        ```
        {% djangoblock %}
            {{django_var}}
        {% enddjangoblock %}

        Optionally...

        {% djangoblock span %} {# Uses a span rather than a div #}
            {{django_var}}
        {% enddjangoblock %}
        ```
    """
    def __init__(self, tag_element, nodelist):
        self.tag_element = tag_element
        self.nodelist = nodelist

    def render(self, context):
        assert(hasattr(_local, "ng_protected"))

        try:
            _local.ng_protected = False
            return u"<{tag} ng-non-bindable>{content}</{tag}>".format(
                tag=self.tag_element,
                content=self.nodelist.render(context)
            )
        finally:
            _local.ng_protected = True


@register.tag(name='djangoblock')
def do_django_block(parser, token):
    try:
        _, tag_element = token.split_contents()
    except ValueError:
        tag_element = 'div'

    nodelist = parser.parse(('enddjangoblock',))
    parser.delete_first_token()
    return DjangoBlockNode(tag_element, nodelist)


@register.filter
def ng_mark_safe(value):
    """
        This will allow access to a value retrieved from an AngularSafeContext
        instance.

        Usage:

            {{my_var|mark_ng_safe}}

        WARNING! THIS COULD EXPOSE YOU TO XSS ATTACKS IF YOU USE IT TO PUT USER
        ENTERED DATA INTO A TEMPLATE. YOU HAVE BEEN WARNED!

        It is recommended you do regular audits of mark_ng_safe usage!
    """
    if value is None:
        return None

    return value._original


@register.filter
def ng_escape(value):
    """
        This has the same effect as mark_ng_safe however all instances of
        of the closing tag (e.g. ]]) will have a backslash inserted after the
        first character to force Angular to ignore it.

        WARNING! THIS COULD EXPOSE YOU TO XSS ATTACKS IF YOU USE IT TO PUT USER
        ENTERED DATA INTO A TEMPLATE. YOU HAVE BEEN WARNED!

        SPECIFICALLY THIS WILL NOT PROTECT YOU IF YOU USE IN ANGULAR DIRECTIVES LIKE
        NG-IF, NG-REPEAT ETC.!
    """

    # Intentionally no default, we want people to do this explicitly
    try:
        ng_closing_tag = getattr(settings, "NG_CLOSING_TAG")
    except AttributeError:
        raise ImproperlyConfigured("You must set settings.NG_CLOSING_TAG (e.g. ']]')")

    # Escape closing tags by inserting a slash after the first character
    replacement = "/".join([ng_closing_tag[0], ng_closing_tag[1:]])

    value = ng_mark_safe(value)
    if value is None:
        return value

    return six.text_type(value).replace(ng_closing_tag, replacement)

