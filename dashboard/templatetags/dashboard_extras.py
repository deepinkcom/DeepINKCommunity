from django import template

register = template.Library()


@register.filter
def get_attr(obj, attr):
    value = getattr(obj, attr, '')
    if callable(value) and not isinstance(value, type):
        try:
            return value()
        except TypeError:
            return value
    if hasattr(value, 'get_category_display'):
        pass
    display_method = getattr(obj, f'get_{attr}_display', None)
    if display_method and callable(display_method):
        return display_method()
    return value
