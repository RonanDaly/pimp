from django import template
from compound.models import Compound
import numpy as np
import timeit
import logging

logger = logging.getLogger(__name__)

register = template.Library()

@register.filter(name='timer_start')
def timer_start(object):
    time = timeit.default_timer()
    return str(time)

@register.filter(name='timer_end')
def timer_end(prev_timer, msg):
    timer = timeit.default_timer()
    duration = timer-float(prev_timer)
    logger.info('Elapsed time %s = %s', msg, duration)
    return True

@register.filter(name='log_message')
def log_message(msg):
    logger.info('%s', msg)
    return True

@register.filter(name='database_search')
def database_search(objects, list):
    print "in tag",list
    print objects
    return list

@register.filter(name='getlist')
def getlist(object, database):
    # response = []
    # # print objects
    # for repo in objects:
    # 	response.append(repo.db_name)
    # print "tag response: ",map(str,response)
    try:
        repo = object.repositorycompound_set.get(db_name=database)
        response = [repo.compound_name, repo.identifier]
    except:
        response = ["",""]
    # print "tag response: ",response
    return response

@register.filter(name='compoundname')
def compoundname(objects):
    names = objects.values_list('compound_name', flat=True).distinct()
    names = list(set([x.lower() for x in names]))
    string = ""
    for name in names:
        string += name + '  '
    # print string
    return string

@register.filter(name='comparisoninfo')
def comparisoninfo(objects, compId):
    obj = objects.get(comparison=compId)
    # print obj
    return obj

@register.filter(name='minuslogten')
def minuslogten(object):
    # print object.adjPvalue
    # return -np.log10(object.adjPvalue)
    return -np.log10(object)

@register.filter(name='samplelistlength')
def samplelistlength(list):
    length = 0
    for sublist in list:
        length += len(sublist)
    return length

@register.filter(name='sampletable')
def sampletable(memberlist):
    maxlength = 0
    for member in memberlist:
        if len(member.sample.all()) > maxlength:
            maxlength = len(member.sample.all())
    mytable = [[None]*len(memberlist) for i in range(maxlength)]
    for i in range(len(memberlist)):
        for j in range(len(memberlist[i].sample.all())):
            mytable[j][i] = memberlist[i].sample.all()[j].name.split(".")[0]
    print mytable
    return mytable

@register.filter(name='fold_change_colour')
def fold_change_colour(object):
    colour = object.get_fold_change_colour()
    #print color
    if colour == None:
        colour = "None"
    return ' style="background-color:' + colour + '"'

@register.filter(name='get_fold_change_colour')
def get_fold_change_colour(value):
    #get_fold_change_colour()
    up_colours = ["#FF6666", "#FF9999", "#FFCCCC"]
    down_colours = ["#6666FF", "#9999FF", "#CCCCFF"]
    fold_change_bins = [2, 1, 0.5849625]

    colours = []
    if value > 0:
        colours = up_colours
    else:
        colours = down_colours

    log_fc = abs(value)

    colour = None
    for idx, fc in enumerate(fold_change_bins):
        if log_fc > fc:
            colour = colours[idx]
            break

    if colour == None:
        colour = "None"
    return ' style="background-color:' + colour + '"'

    return colour

@register.filter(name='significant_pathway_coverage')
def significant_pathway_coverage(object, cutoff=75):
    return len([p for p in object if p[3] > cutoff])

@register.filter(name='number_unique_compounds')
def number_unique_compounds(dataset, identified):
    compounds = Compound.objects.values_list('inchikey', flat=True).filter(peak__dataset=dataset, identified=identified)
    return len(set(compounds))

#@register.filter(name='number_unique_compounds')
#def number_unique_compounds(dataset, identified):
#	compounds = Compound.objects.values_list('inchikey', flat=True).filter(peak__dataset=dataset, identified=identified)
#	return len(set(compounds))

#@register.filter(name='kegg_pathway_url')
# def kegg_pathway_url():

# 	pathway.compoundpathway_set.first().compound.repositorycompound_set.last()
# 	identified_peak = Peak.objects.filter(dataset__analysis=analysis,compound__identified='True').distinct()
# 	identified_peak = Peak.objects.filter(dataset__analysis=analysis_id,compound__identified='True')
#     annotated_peak = Peak.objects.filter(dataset__analysis=analysis).exclude(compound__identified='True').distinct()
#     identified_peakdtcomparisonList = c.peakdtcomparison_set.exclude(adjPvalue__gt=0.05).filter(peak__in=identified_peak).extra(select={"absLogFC": "abs(logFC)"}).order_by("-absLogFC")
#     annotated_peakdtcomparisonList = c.peakdtcomparison_set.exclude(adjPvalue__gt=0.05).filter(peak__in=annotated_peak).extra(select={"absLogFC": "abs(logFC)"}).order_by("-absLogFC")
    
