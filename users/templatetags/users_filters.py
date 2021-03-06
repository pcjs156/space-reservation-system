from django import template

register = template.Library()


@register.simple_tag
def call_method(obj, method_name, *args):
    method = getattr(obj, method_name)
    return method(*args)


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def get_obj_attr(obj, attr):
    return getattr(obj, attr)
