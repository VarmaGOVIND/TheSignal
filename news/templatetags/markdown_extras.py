from django import template
import markdown

register = template.Library()

@register.filter(name='markdown')
def markdown_filter(text):
    return markdown.markdown(text, extensions=['extra', 'codehilite'])