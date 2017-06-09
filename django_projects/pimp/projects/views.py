# Create your views here.
from django.shortcuts import render
from projects.models import Project
from projects.models import UserProject
from projects.forms import ProjectForm, EditDescriptionForm, AddUserForm, GroupCreationForm, EditTitleForm
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import render_to_response
from data.models import Analysis
from support.logging_support import attach_logging_info

#For Frank Integration

from frank.models import PimpProjectFrankExp, ExperimentalProtocol
from frank.models import Experiment as FrankExperiment
from frank.models import ExperimentalCondition as FrankExpCondition
from frank.models import FragmentationSet, UserExperiment
from frank.models import Sample as FrankSample
from frank.models import SampleFile as FrankSampleFile

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)


from groups.models import Attribute, Group

from fileupload.models import Sample, CalibrationSample, Curve

#TODO : change httpResponseRedirect and reverse by other protocole
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.http import Http404
import datetime
import pickle 
import base64

try:
	from django.utils import simplejson
except:
	import json as simplejson
from django.http import HttpResponse

# Rpy2 import for TIC creation
from rpy2.robjects.packages import importr
from rpy2 import robjects
import numpy as np


#Not used, delete this view
def summary(request):
	if request.method == 'GET':
		#try:
		#	p = Project.objects.get(pk=project_id)
		#except Project.DoesNotExist:
		#	raise Http404
		user = request.user
		if user.is_authenticated() :
			project_list = []
			for project in user.project_set.all():
				project_analysis = [project,Analysis.objects.filter(experiment__comparison__attribute__sample__project=project.id).distinct()]
				project_list.append(project_analysis)
			return render(request, 'project/projects.html', {'projects': project_list})
		else :
			return HttpResponseRedirect(reverse('auth_login'))

#TODO : remove groupcreation view from this app -> add it in groups app
#delete this view
def groupcreation(request, project_id):
	if request.method == 'GET':
		user = request.user
		if user.is_authenticated() :
			try:
				project = Project.objects.get(pk=project_id)
				permission = project.userproject_set.get(user=user).permission
			except Project.DoesNotExist:
				raise Http404
			form = GroupCreationForm()
			return render(request, 'project/groupcreation.html', {'project': project, 'permission':permission, 'form':form})
		else :
			return HttpResponseRedirect(reverse('auth_login'))

def create_frank_project_objects(user, title, description, new_project):
	#Set up initial Frank integration objects
	#New experiment currently has ionisation and detection_methods hard coded in.

	#Get LCMS method for detection (id=1)
	frank_detect_method = ExperimentalProtocol.objects.get(id=1)

	expt_name ="Pimp-"+title+"-created"

	frank_experiment = FrankExperiment.objects.create(title=expt_name, description=description, created_by=user, ionisation_method="ESI", detection_method=frank_detect_method)
	exCond_name =title+"-ExCond"

	frank_experimental_condition = FrankExpCondition.objects.create(name=exCond_name, description="Pimp generated FrAnk condition", experiment =frank_experiment)

	#Create user experiment for Frank so that it can be used as a stand alone.
	logger.finest("Creating userexperiment")
	UserExperiment.objects.create(user=user, experiment=frank_experiment)

	#Create the sample file here as the name is auto-generated

	sample_name =title+"-fragments"
	sample_desc="FrAnK sample loaded with PiMP project "+title
	FrankSample.objects.create(experimental_condition = frank_experimental_condition, name=sample_name, description=sample_desc)

	#Create the fragmention set that will be linked to the Experiement
	frag_title = title+"fragSet"
	FragmentationSet.objects.create(name=frag_title, experiment=frank_experiment)

	#Set up the link between Experiment and Project

	PimpProjectFrankExp.objects.create(pimp_project=new_project, frank_expt=frank_experiment)

def newproject(request):
	if request.method == 'POST':
		form = ProjectForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data['title']
			description = form.cleaned_data['description']
			created = datetime.datetime.now()
			user = request.user
			name = user.username
			new_project = Project.objects.create(title=title, description=description, user_owner=user, created=created, modified=created)
			new_user_project = UserProject.objects.create(user=user, project=new_project, date_joined=created, permission="admin")

			create_frank_project_objects(user, title, description, new_project)

			request.session['new_project'] = True
			print request.session['new_project']
			# return redirect('project-summary')
			return redirect('project_detail', project_id=new_project.id)#, context_instance=RequestContext(request))
			# return render(request, 'project-summary')

	else:
		form = ProjectForm()
	return render(request, 'project/project_form.html', {'form': form,})

def getIntensity(mzxmlFile):
	xcms = importr("xcms")
	intensity = []
	file = xcms.xcmsRaw(mzxmlFile.file.path)
	print "file opened"
	intensity = [int(i) for i in list(file.do_slot("tic"))]
	time = [str(i) for i in list(file.do_slot("scantime"))]
	print "intensity list created"
	# scan = xcms.getScan(file, 1)
	# print "scan : ",scan
	# print intensity
	# print time
	lineList = []
	for i in range(len(intensity)):
		lineList.append([float(time[i]),intensity[i]])
	# print lineList 
	return lineList

@attach_logging_info
def peak_discovery(request, project_id):
	if request.is_ajax():
		print "AJAX call detected!"
		ppm = int(request.GET['ppm'])
		rtWindow = int(request.GET['rt_window'])
		polarity = request.GET['polarity']
		rt = float(request.GET['rt'])
		mass = float(request.GET['mass'])
		proton_mass = 1.0072766
		# ids = request.GET['ids']
		ids = map(int, request.GET.getlist('ids'))
		print "ppm ",ppm
		print "rt window ",rtWindow
		print "polarity ",polarity
		print "rt ",rt
		print "mass ",mass
		print "ids ",ids
		print "ids 1 ",ids[0]
		neg_exact_mass = mass - proton_mass
		neg_massWindow = neg_exact_mass * ppm * 0.000001
		print "after mass window ",neg_massWindow
		neg_massUp = neg_exact_mass + neg_massWindow
		print "after massUP ",neg_massUp
		neg_massLow = neg_exact_mass - neg_massWindow
		print "after massMIN ",neg_massLow
		rtUp = rt + rtWindow/2
		print "after rtMax ",rtUp
		rtLow = rt - rtWindow/2
		print "after rtLow ",rtLow
		neg_u = robjects.FloatVector([neg_massLow,neg_massUp])
		neg_mzrange = robjects.r['matrix'](neg_u, ncol = 2)
		pos_exact_mass = mass + proton_mass
		pos_massWindow = pos_exact_mass * ppm * 0.000001
		print "after mass window ",pos_massWindow
		pos_massUp = pos_exact_mass + pos_massWindow
		print "after massUP ",pos_massUp
		pos_massLow = pos_exact_mass - pos_massWindow
		print "after massMIN ",pos_massLow
		pos_u = robjects.FloatVector([pos_massLow,pos_massUp])
		pos_mzrange = robjects.r['matrix'](pos_u, ncol = 2)
		w = robjects.FloatVector([rtLow,rtUp])
		rtrange = robjects.r['matrix'](w, ncol = 2)
		xcms = importr("xcms")
		data = []
		for sample_id in ids:
			name = Sample.objects.get(id=sample_id).name.split(".")[0]
			print "name: ",name
			if polarity != "dual":
				if polarity == "negative":
					mzrange = neg_mzrange
					mzxmlfile = Sample.objects.get(id=sample_id).samplefile.negdata
				elif polarity == "positive":
					mzrange = pos_mzrange
					mzxmlfile = Sample.objects.get(id=sample_id).samplefile.posdata
				print "mzmxml file used here :",mzxmlfile.file.path
				file = xcms.xcmsRaw(mzxmlfile.file.path)
				print "file opened"
				print "mzrange: ",mzrange
				print "rtrange: ",rtrange
				y = xcms.rawMat(file,mzrange, rtrange)
				# print "Y : ",y
				lineList = []
				try:
					time = list(y.rx(True, 1))
					print "time :",time
					# print "time"
					intensity = list(y.rx(True, 3))
					print "intensity :",intensity
					for i in range(len(intensity)):
						lineList.append([float(time[i]),round(float(intensity[i]), 3)])
				except:
					lineList = None
					print "EXCEPTION TRIGGERED!!!!!"
				# print lineList
				data.append([name,lineList])
			else:
				negMzxmlfile = Sample.objects.get(id=sample_id).samplefile.negdata
				posMzxmlfile = Sample.objects.get(id=sample_id).samplefile.posdata
				mzxmlfiles = [negMzxmlfile,posMzxmlfile]
				mzranges = [neg_mzrange,pos_mzrange]
				fileInfo = [name]
				for j in range(len(mzxmlfiles)):
					mzxmlfile = mzxmlfiles[j]
					mzrange = mzranges[j]
					file = xcms.xcmsRaw(mzxmlfile.file.path)
					print "file opened"
					print "mzrange: ",mzrange
					print "rtrange: ",rtrange
					y = xcms.rawMat(file,mzrange, rtrange)
					# print "Y : ",y
					lineList = []
					try:
						time = list(y.rx(True, 1))
						# print "time"
						intensity = list(y.rx(True, 3))
						for i in range(len(intensity)):
							lineList.append([float(time[i]),round(float(intensity[i]), 3)])
					except:
						lineList = None
						print "EXCEPTION TRIGGERED!!!!!"
					fileInfo.append(lineList)
				data.append(fileInfo)


		message = "got somthing on the server!!!"
		response = simplejson.dumps(data)
		return HttpResponse(response, content_type='application/json')



@attach_logging_info
def get_mzxml_tic(request, project_id, sample_id):
	if request.is_ajax():
		sample_type = request.GET['type']
		print sample_id
		if sample_type == "sample":
			sample_name = Sample.objects.get(id=sample_id).name
			sample = Sample.objects.get(id=sample_id).samplefile
		elif sample_type == "calibration":
			sample_name = CalibrationSample.objects.get(id=sample_id).name
			sample = CalibrationSample.objects.get(id=sample_id).standardFile
		if not sample.posdata :
			posdata = "None"
		else:
			posmzxmlfile = sample.posdata
			print "bien ici"
			if not posmzxmlfile.tic:
				print "over here"
				posdata = getIntensity(posmzxmlfile)
				# print "posdata ",[i[0] for i in posdata]
				x_axis = [i[0] for i in posdata]
				y_axis = [i[1] for i in posdata]
				x = pickle.dumps(x_axis)
				y = pickle.dumps(y_axis)
				mean = np.mean(y_axis)
				median = np.median(y_axis)
				print "pos median : ",median
				print "pos mean : ",mean

				# print x

				print "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT"

				curve = Curve.objects.create(x_axis=x,y_axis=y,mean=mean,median=median)
				curve.save()
				posmzxmlfile.tic = curve
				posmzxmlfile.save()

				# print posmzxmlfile.tic.x_axis
				# posintensity = posdata[0]
				# postime = posdata[1]
			else:
				print "tic exist"
				# print str(posmzxmlfile.tic.x_axis)
				x_axis = pickle.loads(str(posmzxmlfile.tic.x_axis))
				y_axis = pickle.loads(str(posmzxmlfile.tic.y_axis))
				print "pos median : ",posmzxmlfile.tic.median
				print "pos mean : ",posmzxmlfile.tic.mean
				posdata = []
				print "after loads"
				for i in range(len(x_axis)):
					posdata.append([float(x_axis[i]),float(y_axis[i])])
				print "after for"
					# print posdata
		if not sample.negdata :
			negdata = "None"
		else:
			negmzxmlfile = sample.negdata
			if not negmzxmlfile.tic:
				print "over there :)"
				negdata = getIntensity(negmzxmlfile)
				x_axis = [i[0] for i in negdata]
				y_axis = [i[1] for i in negdata]
				x = pickle.dumps(x_axis)
				y = pickle.dumps(y_axis)
				mean = np.mean(y_axis)
				median = np.median(y_axis)
				print "neg median : ",median
				print "neg mean : ",mean

				curve = Curve.objects.create(x_axis=x,y_axis=y,mean=mean,median=median)
				curve.save()
				negmzxmlfile.tic = curve
				negmzxmlfile.save()
			else:
				print "tic exist"
				x_axis = pickle.loads(str(negmzxmlfile.tic.x_axis))
				y_axis = pickle.loads(str(negmzxmlfile.tic.y_axis))
				print "neg median : ",negmzxmlfile.tic.median
				print "neg mean : ",negmzxmlfile.tic.mean
				negdata = []
				for i in range(len(x_axis)):
					negdata.append([float(x_axis[i]),float(y_axis[i])])

			# negintensity = getIntensity(negmzxmlfile)
		# message = "my sample id on the server side is : " + str(sample_id)
		# response = simplejson.dumps(message)
		fileList = [sample_name,posdata,negdata]
		response = simplejson.dumps(fileList)
		return HttpResponse(response, content_type='application/json')


@attach_logging_info
def get_scan_data(mzxmlFile, rt):
	xcms = importr("xcms")
	file = xcms.xcmsRaw(mzxmlFile.file.path)
	time = [str(i) for i in list(file.do_slot("scantime"))]
	index = time.index(str(rt))
	scan = xcms.getScan(file, index+1)
	# for i in range(len(scan)):
	# 	print scan[i]
	mass = list(scan.rx(True, 1))
	# print mass
	print "+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
	# print type(scan)
	intensity = list(scan.rx(True, 2))
	# print intensity
	lineList = []
	for i in range(len(intensity)):
		lineList.append([float(mass[i]),intensity[i]])
	return lineList
	# print "index : ",index


def get_scan(request, project_id, sample_id):
	if request.is_ajax():
		sample_id = request.GET['id']
		polarity = request.GET['polarity']
		rt = request.GET['rt']
		sample_type = request.GET['type']
		if sample_type == "sample":
			sample = Sample.objects.get(id=sample_id).samplefile
		elif sample_type == "calibration":
			sample = CalibrationSample.objects.get(id=sample_id).standardFile
		if polarity == "NEG":
			# mzxmlfile = Sample.objects.get(id=sample_id).samplefile.negdata
			mzxmlfile = sample.negdata
		else:
			# mzxmlfile = Sample.objects.get(id=sample_id).samplefile.posdata
			mzxmlfile = sample.posdata
		data = get_scan_data(mzxmlfile, rt)
		print "my polarity : ",polarity
		print "my sample id : ",sample_id
		print "my retention time : ",rt
		message = "my sample id on the server side is : " + str(sample_id)
		response = simplejson.dumps(data)
		return HttpResponse(response, content_type='application/json')

# We do not use this view anymore, the call to create_member_tic is now wrong as it requires 2 parameters: attribute id and sample type 
@attach_logging_info
def get_group_tic(request, project_id, group_id):
	if request.is_ajax():
		group_id = request.GET['id']
		print "group is ",group_id
		group = Group.objects.get(id=group_id)
		group_name = group.name
		attribute_list = group.attribute_set.all()
		member_tic_list = []
		for attribute in attribute_list:
			attributeResponse = create_member_tic(attribute.id)
			member_tic_list.append(attributeResponse)
		groupResponse = [group_name, member_tic_list]
		# message = "we are on the server side" 
		# response = simplejson.dumps(message)
		# fileList = [sample_name,posdata,negdata]
		response = simplejson.dumps(groupResponse)
		
		# response = simplejson.dumps(fileList)
		return HttpResponse(response, content_type='application/json')

def create_member_tic(attribute_id, sample_type):
	attribute = Attribute.objects.get(id=attribute_id)
	attribute_name = attribute.name
	sampleList = attribute.sample.all()

	if sample_type == "sample":
		sampleList =  attribute.sample.all()
	elif sample_type == "calibration":
		sampleList = attribute.calibrationsample.all()

	sampleCurveList = []
	if sample_type == "sample":
		for sample in sampleList :
			sample_name = sample.name
			if not sample.samplefile.posdata :
				posdata = "None"
				posBarTic = "None"
			else:
				posmzxmlfile = sample.samplefile.posdata
				if not posmzxmlfile.tic:
					posdata = getIntensity(posmzxmlfile)
					x_axis = [i[0] for i in posdata]
					y_axis = [i[1] for i in posdata]
					x = pickle.dumps(x_axis)
					y = pickle.dumps(y_axis)
					mean = np.mean(y_axis)
					median = np.median(y_axis)
					posBarTic = [mean,median]

					curve = Curve.objects.create(x_axis=x,y_axis=y,mean=mean,median=median)
					curve.save()
					posmzxmlfile.tic = curve
					posmzxmlfile.save()
				else:
					x_axis = pickle.loads(str(posmzxmlfile.tic.x_axis))
					y_axis = pickle.loads(str(posmzxmlfile.tic.y_axis))
					posBarTic = [posmzxmlfile.tic.mean,posmzxmlfile.tic.median]
					posdata = []
					for i in range(len(x_axis)):
						posdata.append([float(x_axis[i]),float(y_axis[i])])
			if not sample.samplefile.negdata :
				negdata = "None"
				negBarTic = "None"
			else:
				negmzxmlfile = sample.samplefile.negdata
				if not negmzxmlfile.tic:
					negdata = getIntensity(negmzxmlfile)
					x_axis = [i[0] for i in negdata]
					y_axis = [i[1] for i in negdata]
					x = pickle.dumps(x_axis)
					y = pickle.dumps(y_axis)
					mean = np.mean(y_axis)
					median = np.median(y_axis)
					negBarTic = [mean,median]

					curve = Curve.objects.create(x_axis=x,y_axis=y,mean=mean,median=median)
					curve.save()
					negmzxmlfile.tic = curve
					negmzxmlfile.save()
				else:
					x_axis = pickle.loads(str(negmzxmlfile.tic.x_axis))
					y_axis = pickle.loads(str(negmzxmlfile.tic.y_axis))
					negBarTic = [negmzxmlfile.tic.mean,negmzxmlfile.tic.median]
					negdata = []
					for i in range(len(x_axis)):
						negdata.append([float(x_axis[i]),float(y_axis[i])])
			fileList = [sample_name,posdata,negdata,posBarTic,negBarTic]
			sampleCurveList.append(fileList)

	elif sample_type == "calibration":
		for sample in sampleList :
			sample_name = sample.name
			if not sample.standardFile.posdata :
				posdata = "None"
				posBarTic = "None"
			else:
				posmzxmlfile = sample.standardFile.posdata
				if not posmzxmlfile.tic:
					posdata = getIntensity(posmzxmlfile)
					x_axis = [i[0] for i in posdata]
					y_axis = [i[1] for i in posdata]
					x = pickle.dumps(x_axis)
					y = pickle.dumps(y_axis)
					mean = np.mean(y_axis)
					median = np.median(y_axis)
					posBarTic = [mean,median]


					curve = Curve.objects.create(x_axis=x,y_axis=y,mean=mean,median=median)
					curve.save()
					posmzxmlfile.tic = curve
					posmzxmlfile.save()
				else:
					x_axis = pickle.loads(str(posmzxmlfile.tic.x_axis))
					y_axis = pickle.loads(str(posmzxmlfile.tic.y_axis))
					posBarTic = [posmzxmlfile.tic.mean,posmzxmlfile.tic.median]
					posdata = []
					for i in range(len(x_axis)):
						posdata.append([float(x_axis[i]),float(y_axis[i])])
						# print posdata
			if not sample.standardFile.negdata :
				negdata = "None"
				negBarTic = "None"
			else:
				negmzxmlfile = sample.standardFile.negdata
				if not negmzxmlfile.tic:
					negdata = getIntensity(negmzxmlfile)
					x_axis = [i[0] for i in negdata]
					y_axis = [i[1] for i in negdata]
					x = pickle.dumps(x_axis)
					y = pickle.dumps(y_axis)
					mean = np.mean(y_axis)
					median = np.median(y_axis)
					negBarTic = [mean,median]

					curve = Curve.objects.create(x_axis=x,y_axis=y,mean=mean,median=median)
					curve.save()
					negmzxmlfile.tic = curve
					negmzxmlfile.save()
				else:
					x_axis = pickle.loads(str(negmzxmlfile.tic.x_axis))
					y_axis = pickle.loads(str(negmzxmlfile.tic.y_axis))
					negBarTic = [negmzxmlfile.tic.mean,negmzxmlfile.tic.median]
					negdata = []
					for i in range(len(x_axis)):
						negdata.append([float(x_axis[i]),float(y_axis[i])])
			fileList = [sample_name,posdata,negdata,posBarTic,negBarTic]
			sampleCurveList.append(fileList)

	attributeResponse = [attribute_name, sampleCurveList]
	return attributeResponse

# Ajax call for member TIC display -> forloop through the files, 
# creation of tic curve if not there already, 
# send back info to client side
@attach_logging_info
def get_tic(request, project_id, attribute_id):
	if request.is_ajax():
		attribute_id = request.GET['id']
		sample_type = request.GET['type']
		print attribute_id
		attributeResponse = create_member_tic(attribute_id, sample_type)
		response = simplejson.dumps(attributeResponse)
		return HttpResponse(response, content_type='application/json')
	else:
		print "request is not ajax, project: ",project_id," attribute: ",attribute_id


@attach_logging_info
def detail(request, project_id):
	if 'new_project' in request.session:
		print "my session : ",request.session['new_project']
		del request.session['new_project']
	if 'new_project' in request.session:
		print "my session : ",request.session['new_project']
	else:
		print "no session"
	if request.method == 'GET':
		print "detail project view"
		try:
			project = Project.objects.get(pk=project_id)
			user = request.user
			permission = project.userproject_set.get(user=user).permission
		except Project.DoesNotExist:
			raise Http404
		groups = []
		attributes = []
		files = project.picture_set.all()
		samples = project.sample_set.all()
		# projfiles = project.projfile_set.all()
		calibrationsamples = project.calibrationsample_set.all()

		#A trail to get to the Frank sample files without changing the Pimp code too much.
		pimpFrankLink = PimpProjectFrankExp.objects.get(pimp_project=project)
		frank_experiment = pimpFrankLink.frank_expt
		print "the experiment is", frank_experiment
		frank_expt_condition = frank_experiment.experimentalcondition_set.all()[0]
		print "the condition is", frank_expt_condition
		frank_sample = frank_expt_condition.sample_set.all()[0]
		print "the Frank sample is", frank_sample
		fragment_files = FrankSampleFile.objects.filter(sample__experimental_condition__experiment=frank_experiment)

		#frank_samplefiles = frank_sample.samplefile_set.all()

		#This is a list of the sample files to pass to detail.
		#fragfiles = list(frank_samplefiles)


		projfileattributes = []
		comparisons = []
		experiments = []


		print "Frank sample is", frank_sample

		for sample in samples:
			if sample.attribute_set.all():
				attributeSet = set(attributes).union(set(sample.attribute_set.all()))
				attributes = list(attributeSet)
		for attribute in attributes:
			if attribute.group not in groups:
				groups.append(attribute.group)
			if attribute.comparison_set.all():
				comparisonSet = set(comparisons).union(set(attribute.comparison_set.all()))
				comparisons = list(comparisonSet)
		for comparison in comparisons:
			if comparison.experiment not in experiments:
				experiments.append(comparison.experiment)
		# print "experiments : ",experiments
		# print groups
		for projfile in calibrationsamples:
			if projfile.attribute_set.all():
				projfileattSet = set(projfileattributes).union(set(projfile.attribute_set.all()))
				projfileattributes = list(projfileattSet)
		# print "projfile attribute : ",projfileattributes
		print "At the end of the detail view"
		return render(request, 'project/detail.html', {'project': project, 'permission':permission, 'groups':groups, 'projfileattributes':projfileattributes, 'experiments':experiments, 'frank_sample':frank_sample, 'fragment_files':fragment_files})


@attach_logging_info
def sampleDelete(request, project_id):
	if request.method == 'POST':
		# nothing
		pass
	else:
		try:
			project = Project.objects.get(pk=project_id)
			user = request.user
			permission = project.userproject_set.get(user=user).permission
		except Project.DoesNotExist:
			raise Http404
		files = project.picture_set.all()
		return render(request, 'project/delete_samples.html', {'project': project, 'permission':permission})


@attach_logging_info
def fragmentFileDelete(request, project_id):
	if request.method == 'POST':
		# nothing
		pass
	else:
		try:
			project = Project.objects.get(pk=project_id)
			user = request.user
			permission = project.userproject_set.get(user=user).permission
		except Project.DoesNotExist:
			raise Http404
		return render(request, 'project/delete_fragfile.html', {'project': project, 'permission':permission})


@attach_logging_info
def projectFileDelete(request, project_id):
	if request.method == 'POST':
		# nothing
		pass
	else:
		try:
			project = Project.objects.get(pk=project_id)
			user = request.user
			permission = project.userproject_set.get(user=user).permission
		except Project.DoesNotExist:
			raise Http404
		return render(request, 'project/delete_projectfile.html', {'project': project, 'permission':permission})


@attach_logging_info
def edit_title(request, project_id):
	p = Project.objects.get(pk=project_id)

	if request.method =='POST':
		form = EditTitleForm(request.POST)
		
		if form.is_valid():
			title = form.cleaned_data['title']
			p.title = title
			p.modified = datetime.datetime.now()
			p.save()
			return HttpResponseRedirect(reverse('project_detail', args=(p.id,)))
		else: # form.is_valid() == False
			return render(request, 'project/edit_title_form.html', {'form': form, 'project': p})
	else:
		title = p.title
		form = EditTitleForm()
		form.fields['title'].initial = title
		user = request.user
		
		if user.userproject_set.get(project=p).permission == "read":
			raise Http404
		else:
			return render(request, 'project/edit_title_form.html', {'form': form, 'project': p})


@attach_logging_info
def editdescription(request, project_id):
	if request.method == 'POST':
		form = EditDescriptionForm(request.POST)
		if form.is_valid():
			print form
			description = form.cleaned_data['description']
			p = Project.objects.get(pk=project_id)
			p.description = description
			p.modified = datetime.datetime.now()
			p.save()
			return HttpResponseRedirect(reverse('project_detail', args=(p.id,)))
	else:
		p = Project.objects.get(pk=project_id)
		description = p.description
		form = EditDescriptionForm()
		form.fields['description'].initial = description
		user = request.user
		if user.userproject_set.get(project=p).permission == "read":
			raise Http404
		else:
			return render(request, 'project/edit_description_form.html', {'form': form, 'project':p})


@attach_logging_info
def adduser(request, project_id):
	if request.method == 'POST':
		form = AddUserForm(request.POST)
		if form.is_valid():
			name = form.cleaned_data['name']
			permission = form.cleaned_data['permission']
			project = Project.objects.get(pk=project_id)
			try: 
				user = User.objects.get(username=name)
			except User.DoesNotExist:
				user = User.objects.get(email=name)
			date_joined = datetime.datetime.now()
			if user.userproject_set.all():
				try: 
					userproject = user.userproject_set.get(project=project)
				except UserProject.DoesNotExist:
					userproject = None
				if userproject:
					#alert = "user_already_exist"
					return HttpResponseRedirect(reverse('project_detail', args=(project.id,)))
				else:
					project.modified = date_joined
					project.save()
					new_user_project = UserProject(user=user, project=project, date_joined=date_joined, permission=permission)
					new_user_project.save()
					return HttpResponseRedirect(reverse('project_detail', args=(project.id,)))
			else:
				project.modified = date_joined
				new_user_project = UserProject(user=user, project=project, date_joined=date_joined, permission=permission)
				new_user_project.save()
				return HttpResponseRedirect(reverse('project_detail', args=(project.id,)))
		else:
			project = Project.objects.get(pk=project_id)
			return render(request, 'project/adduser.html', {'form': form, 'project': project})
	else:
		form = AddUserForm()
		p = Project.objects.get(pk=project_id)
		user = request.user
		if user.userproject_set.get(project=p).permission != "admin":
			raise Http404
		else:
			return render(request, 'project/adduser.html', {'project':p,'form': form})

def userpermission(request, project_id):
	if request.method == 'POST':
		form = ChangePermissionForm(request.POST)
		if form.is_valid():
			user = form.cleaned_data['user']
			permission = form.cleaned_data['permission']
			user = User.objects.get(username=name)
			project = Project.objects.get(pk=project_id)
			try: 
				userproject = user.userproject_set.get(project=project)
			except UserProject.DoesNotExist:
				print "we have a problem here"
				return HttpResponseRedirect(reverse('project_detail', args=(project.id,)))
			userproject.permission = permission
			userproject.save()


def createdataset(request, file_path):
	pimpXmlFile = file_path


@attach_logging_info
def removeUserProject(request,project_id,user_id):
	project = Project.objects.get(id = project_id)
	user_to_remove = User.objects.get(id = user_id)
	current_user = request.user
	current_user_project = UserProject.objects.get(project=project,user=current_user)
	remove_user_project = UserProject.objects.get(project = project, user = user_to_remove)
	# We can only delete if the current user has admin rights and they are not trying to delete the owner!
	if current_user_project.permission == 'admin':
		if not user_to_remove is project.user_owner:
			remove_user_project.delete()
	return HttpResponseRedirect(reverse('project_detail', args=(project_id,)))



