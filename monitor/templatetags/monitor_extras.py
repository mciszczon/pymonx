from datetime import datetime
from django import template
from monitor.utils import time_since as time_since_func

register = template.Library()


@register.simple_tag
def time_since(timestamp: float | int, now: datetime = None):
    return time_since_func(timestamp, now)
