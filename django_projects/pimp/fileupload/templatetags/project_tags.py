from django import template

register = template.Library()

@register.filter(name='mysplit')
def mysplit(value, sep = "."):
    parts = value.split(sep)
    print parts[1:]
    return (parts[0], parts[1:])

@register.filter(name='count')
def count(list, sep = "."):
    mzxml = 0
    csv = 0
    for file in list:
        if file.name.split(sep)[1:].upper() == "MZXML":
            mzxml += 1
        else:
            csv +=1
    return (mzxml, csv)
