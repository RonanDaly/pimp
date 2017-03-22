from django import template
import logging

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter(name='get_dictionary_item')
def get_dictionary_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='sample_index')
def sample_index(sample_list, sample):
    return list(sample_list).index(sample)


@register.filter(name='increment')
def increment(counter):
    new_counter = counter + 1
    return new_counter
