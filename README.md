
**This is a work in progress and not suitable for production (or any other) use**

# Django Angular Protect

This is a Django app which helps protect against potential XSS issues when using
both Angular's client-side templates alongside Django's server-side template system.

## High-level Overview

This app provides a new function (`angular.shortcuts.render()`) for rendering Django
templates. If you use this function to render a template then all Django template variable
substitutions are disabled by default.

For example this template:

```html
<span>{{user.first_name}}</span>
```

Would output the following when using `angular.shortcuts.render()`

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

In that situation, you can use the `ng_mark_safe` template filter while outside a
`{% djangoblock %}`:

```html
<div data-my-attribute="{{safe_var|ng_mark_safe}}">
```

Which would output the value of `safe_var`, of course, you must ensure the variable
does not contain data which could potentially be malicious.

`ng_escape` is does the same thing as `ng_mark_safe` except it will disrupt any Angular
closing tags by inserting a slash in them. (e.g. `]]` would become `]/]`) which prevents
Angular expanding them.

## Configuration

 - Add the `'angular'` app to your `INSTALLED_APPS` setting.
 - Add `'angular.middleware.EnsureAngularProtectionMiddleware'` to your `MIDDLEWARE_CLASSES`
   setting.
 - Set `settings.NG_CLOSING_TAG` and `settings.NG_OPENING_TAG` setting. This has no default as it's essential that it is
   set to match your `$interpolateProvider.startSymbol('[[').endSymbol(']]');` setting.

## USE WITH CAUTION!

Using `ng_escape` and `ng_mark_safe` with user submitted data can expose you to XSS attacks!

In particular, you should *not* use them inside Angular directives (such as `ng-if`) or HTML tag
attributes unless you are certain the variable does not contain any data coming from a user.

`ng_escape` will not protect you at all inside HTML attributes as all it does is escape the `endSymbol`
and malicious Javascript will not need those (e.g. `ng-if="{{user_var|ng_escape}}"` could evaulate to `ng-if="alert(0)"`).
