from django import template

from etapasJuego.services.story import get_story

register = template.Library()


@register.simple_tag
def mission_story(key):
    return get_story(key)
