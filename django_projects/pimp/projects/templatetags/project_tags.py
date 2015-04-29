from django import template
from groups.models import Attribute

register = template.Library()

@register.filter
def mysplit(value, sep = "."):
    parts = value.split(sep)
    # print parts[1:][0]
    return (parts[0][0], parts[1:][0])

@register.filter
def count(list, sep = "."):
	mzxml = 0
	csv = 0
	for file in list:
		# print file.name.split(sep)[1:][0]
		if file.name.split(sep)[1:][0].upper() == "MZXML": 
			mzxml += 1
		else:
			csv +=1
	return (mzxml, csv)

@register.simple_tag
def get_pos_tic_from_member_id(member_id):
	if member_id.isdigit():
		number = int(member_id)
	else:
		number = member_id
	return number
	# try:
	# 	return Attribute.objects.get(id=number).ticgroup.postic.ticplot
	# except Attribute.DoesNotExist:
	# 	return 'Unknown'

@register.filter
def project_permission(project, user):
	userproject = project.userproject_set.get(user=user)
	return userproject.permission

@register.filter
def get_pourcent(total, mapped):
	if int(total) == 0:
		pourcentage = 0
	else:
		pourcentage = (mapped*100)/total
	return pourcentage