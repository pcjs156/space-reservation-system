from django import template

register = template.Library()


@register.filter
def index(indexable, i):
    return indexable[i]


@register.filter
def zero_left_padding(target):
    return '{:0>2s}'.format(str(target))
