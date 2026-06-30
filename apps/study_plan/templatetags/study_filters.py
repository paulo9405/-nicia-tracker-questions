import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='render_markdown')
def render_markdown(value):
    """Render markdown text to HTML, preserving tables, headers and formatting."""
    if not value:
        return ''
    extensions = ['tables', 'fenced_code', 'sane_lists']
    html = md.markdown(str(value), extensions=extensions)
    return mark_safe(html)
