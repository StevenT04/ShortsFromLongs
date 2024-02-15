from django import template
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def duration(value):
    if not value:
        return ""
    # Assuming value is a timedelta object
    seconds = int(value.total_seconds())
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"
