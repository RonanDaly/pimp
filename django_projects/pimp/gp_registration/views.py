from django.shortcuts import render
from django.db.models import Q
from projects.models import *
from fileupload.models import *


# Create your views here.
def profile(request):
    # user
    user = request.user

    # Get all samples associated with a user
    owned_projects = Project.objects.filter(user_owner=user)
    calibration_samples = ProjFile.objects.filter(project__in=owned_projects).order_by('project__id')
    samples = Picture.objects.filter(project__in=owned_projects).order_by('project__id')

    storage_taken = {'samples': 0, 'calibration_samples': 0}

    sample_number = calibration_samples.count() + samples.count()

    for calibration_sample in calibration_samples:
        storage_taken['calibration_samples'] += calibration_sample.file.size
    for sample in samples:
        storage_taken['samples'] += sample.file.size

    storage_taken_percent = {}
    total_storage = 53687091200
    storage_taken_percent['calibration_samples'] = (storage_taken['calibration_samples'] / float(total_storage)) * 100
    storage_taken_percent['samples'] = (storage_taken['samples'] / float(total_storage)) * 100

    storage_used = storage_taken['calibration_samples'] + storage_taken['samples']
    storage_remaining = float(total_storage) - storage_used


    # collaborators and collaborated projects
    collaborated_projects = Project.objects.filter(users=user).exclude(user_owner=user)
    total_projects = owned_projects.count() + collaborated_projects.count()

    collaborators = User.objects.filter(Q(project=collaborated_projects) | Q(project=owned_projects)).exclude(id=user.id).distinct()

    return render(request, 'registration/profile.html', locals())
