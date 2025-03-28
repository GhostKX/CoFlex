from django import template
from datetime import timedelta

register = template.Library()


@register.filter
def add_days(value, days):
    """Adding a specified number of days to a date"""
    return value + timedelta(days=int(days))
