from django import template

register = template.Library()


class DjangoBlockNode(template.Node):
    """
        Performs two tasks:

        1. Wraps content in <div ng-non-bindable>
        2. Temporarily allows access to the context within the block
    """
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        try:
            context._protected = False
            return u"<div ng-non-bindable>{}</div>".format(
                self.nodelist.render(context)
            )
        finally:
            context._protected = True


def do_django_block(parser, token):
    nodelist = parser.parse(('enddjangoblock',))
    parser.delete_first_token()
    return DjangoBlockNode(nodelist)

@register.tag('djangoblock', do_django_block)


@register.filter
def mark_ng_safe(value):
    """
        This will allow access to a value retrieved from an AngularSafeContext
        instance.

        Usage:

            {{my_var|mark_ng_safe}}

        WARNING: THIS COULD EXPOSE YOU TO XSS ATTACKS IF YOU USE IT TO PUT USER
        ENTERED DATA INTO A TEMPLATE. YOU HAVE BEEN WARNED!

        It is recommended you do regular audits of mark_ng_safe usage!
    """
    return value._original


