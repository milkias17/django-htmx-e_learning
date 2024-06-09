from django import template

register = template.Library()


@register.filter(name="times")
def times(number, start=0, inclusive=None):
    if start == 1:
        return range(start, number + 1)

    return range(start, number)
