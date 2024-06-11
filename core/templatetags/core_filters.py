from django import template
from urllib.parse import urlencode

register = template.Library()


@register.filter(name="times")
def times(number, start=0, inclusive=None):
    if start == 1:
        return range(start, number + 1)

    return range(start, number)

@register.simple_tag
def query_string(query_params_dict):
    res = urlencode(query_params_dict)
    return str(res)
