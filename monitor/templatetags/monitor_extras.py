from django import template

from monitor.utils import bytes_to_mib


register = template.Library()


@register.simple_tag
def format_memory(memory: int) -> str:
    return "{:.2f}".format(bytes_to_mib(memory))
