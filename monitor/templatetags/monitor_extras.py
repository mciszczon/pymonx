from django import template
from monitor.utils import time_since as time_since_func

register = template.Library()


@register.simple_tag
def time_since(timestamp: int):
    return time_since_func(timestamp)
