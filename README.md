
**This is a work in progress and not suitable for production (or any other) use**

# Django Angular Protect

This is a Django app which helps protect against potential XSS issues when using
both Angular's client-side templates alongside Django's server-side template system.

## High-level Overview

This app provides a new function (`angular.shortcuts.ng_render()`) for rendering Django
templates. If you use this function to render a template then all Django template variable
substitutions are disabled by default.

For example this template:

```html
<span>{{user.first_name}}</span>
```

Would output the following when using `ng_render()`

```html
<span></span>
```

That's not that useful when taken on its own. But it's safe for Angular. To get access to Django
variables you must now be explicit:

```html
{% djangoblock %}
<span>{{user.first_name}}</span>
{% enddjangoblock %}

```

This will output the following:

```html
<div ng-non-bindable>
<span>{{user.first_name}}</span>
</div>
```

The `{% djangoblock %}` tag enables Angular's protections by wrapping Django content
in `ng-non-bindable` which disables Angular directives, while temporarily allowing
access to the Django context.

There are occasions though where you need to use data from the Django context which are "safe"
(as in they are not sourced from user input), and you need them for an Angular directive.

In that situation, you can use the `mark_ng_safe` template filter while outside a
`{% djangoblock %}`:

```html
<div ng-if="{{safe_var|mark_ng_safe}}">
```

Which would output the value of `safe_var`, of course, you must ensure the variable
does not contain data which could potentially be malicious. 
