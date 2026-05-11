from django import template
from django.contrib.humanize.templatetags.humanize import intcomma as django_intcomma

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by arg"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def intcomma(value):
    """Add comma to numbers"""
    return django_intcomma(value)
