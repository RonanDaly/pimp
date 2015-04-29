from groups.models import *
from django.contrib import admin

admin.site.register(Attribute)

class AttributeAdmin(admin.TabularInline):
    model = Attribute
    extra = 0

class GroupAdmin(admin.ModelAdmin):
    inlines = [AttributeAdmin]

admin.site.register(Group, GroupAdmin)
