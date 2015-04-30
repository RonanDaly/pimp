# Create your views here.
from django.shortcuts import render
from projects.models import Project
from projects.models import UserProject
from projects.forms import ProjectForm, EditDescriptionForm, AddUserForm, GroupCreationForm
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.template import RequestContext
from django.shortcuts import render_to_response
from data.models import Analysis

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

def newproject(request):
	if request.method == 'POST':
		form = ProjectForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data['title']
			description = form.cleaned_data['description']
			created = datetime.datetime.now()
			user = request.user
			name = user.username
			new_project = Project.objects.create(title=title, description=description, owner=name, created=created, modified=created)
			new_user_project = UserProject.objects.create(user=user, project=new_project, date_joined=created, permission="admin")
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
		return HttpResponse(response, mimetype='application/json')




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
		return HttpResponse(response, mimetype='application/json')

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
		if polarity == "NEG":
			mzxmlfile = Sample.objects.get(id=sample_id).samplefile.negdata
		else:
			mzxmlfile = Sample.objects.get(id=sample_id).samplefile.posdata
		data = get_scan_data(mzxmlfile, rt)
		print "my polarity : ",polarity
		print "my sample id : ",sample_id
		print "my retention time : ",rt
		message = "my sample id on the server side is : " + str(sample_id)
		response = simplejson.dumps(data)
		return HttpResponse(response, mimetype='application/json')

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
		return HttpResponse(response, mimetype='application/json')

def create_member_tic(attribute_id):
	attribute = Attribute.objects.get(id=attribute_id)
	attribute_name = attribute.name
	sampleList = attribute.sample.all()

	sampleCurveList = []

	for sample in sampleList :
		sample_name = sample.name
		if not sample.samplefile.posdata :
			posdata = "None"
		else:
			posmzxmlfile = sample.samplefile.posdata
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
				posBarTic = [mean,median]

				# print x

				print "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT"

				curve = Curve.objects.create(x_axis=x,y_axis=y,mean=mean,median=median)
				curve.save()
				posmzxmlfile.tic = curve
				posmzxmlfile.save()

				print posmzxmlfile.tic.x_axis
				# posintensity = posdata[0]
				# postime = posdata[1]
			else:
				print "tic exist"
				# print str(posmzxmlfile.tic.x_axis)
				x_axis = pickle.loads(str(posmzxmlfile.tic.x_axis))
				y_axis = pickle.loads(str(posmzxmlfile.tic.y_axis))
				print "pos median : ",posmzxmlfile.tic.median
				print "pos mean : ",posmzxmlfile.tic.mean
				posBarTic = [posmzxmlfile.tic.mean,posmzxmlfile.tic.median]
				posdata = []
				print "after loads"
				for i in range(len(x_axis)):
					posdata.append([float(x_axis[i]),float(y_axis[i])])
				print "after for"
					# print posdata
		if not sample.samplefile.negdata :
			negdata = "None"
		else:
			negmzxmlfile = sample.samplefile.negdata
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
				negBarTic = [mean,median]

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
				negBarTic = [negmzxmlfile.tic.mean,negmzxmlfile.tic.median]
				negdata = []
				for i in range(len(x_axis)):
					negdata.append([float(x_axis[i]),float(y_axis[i])])
		fileList = [sample_name,posdata,negdata,posBarTic,negBarTic]
		sampleCurveList.append(fileList)

	# print attributeResponse
	# ++++++++++++++++++++++++++++++++++++++ Previous version of group tic creation ++++++++++++++++++++++++++++++++++++++
	# if not Attribute.objects.get(id=attribute_id).ticgroup.postic :
	# 	posticfile = "None"
	# else:
	# 	posticfile = Attribute.objects.get(id=attribute_id).ticgroup.postic.ticplot
	# 	# print posticfile
	# if not Attribute.objects.get(id=attribute_id).ticgroup.negtic :
	# 	negticfile = "None"
	# else:
	# 	negticfile = Attribute.objects.get(id=attribute_id).ticgroup.negtic.ticplot
	# fileList = [attribute_name,posticfile,negticfile]
	attributeResponse = [attribute_name, sampleCurveList]
	return attributeResponse

# Ajax call for member TIC display -> forloop through the files, 
# creation of tic curve if not there already, 
# send back info to client side
def get_tic(request, project_id, attribute_id):
	if request.is_ajax():
		attribute_id = request.GET['id']
		print attribute_id
		attributeResponse = create_member_tic(attribute_id)
		response = simplejson.dumps(attributeResponse)
		return HttpResponse(response, mimetype='application/json')
	else:
		print "request is not ajax, project: ",project_id," attribute: ",attribute_id

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
		projfileattributes = []
		comparisons = []
		experiments = []
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


		return render(request, 'project/detail.html', {'project': project, 'permission':permission, 'groups':groups, 'projfileattributes':projfileattributes, 'experiments':experiments})

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
	





