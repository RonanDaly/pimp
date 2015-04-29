from django import template

register = template.Library()


@register.filter(name='database_search')
def database_search(objects, list):
	print "in tag",list
	print objects
	return list
