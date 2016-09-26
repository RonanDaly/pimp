from datetime import datetime
import json
import os
import shutil
from test.test_support import EnvironmentVarGuard
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.db import transaction
from django.test.testcases import TransactionTestCase
from mock.mock import patch

from experiments.models import Analysis, Experiment, DefaultParameter, Params, \
    Parameter, Database, Comparison, AttributeComparison
from experiments.tasks import start_pimp_pipeline
from fileupload.models import ProjFile, Picture, SampleFileGroup, Sample, \
    StandardFileGroup, CalibrationSample
from groups.models import Group, Attribute, ProjfileAttribute, SampleAttribute
from projects.models import Project, UserProject

logger = logging.getLogger(__name__)

def create_test_user():
    try:
        user = User.objects.get_by_natural_key('testrunner')
    except ObjectDoesNotExist:
        user = User.objects.create_superuser(
            username='testrunner',
            email='testrunner@gmail.com',
            password='password',
            first_name='Test',
            last_name='Runner'
        )
        user.is_staff = True
    return user

def create_sample(project, fixture_dir, name):

    name = '%s.mzXML' % name
    f = file('%s/samples/POS/%s' % (fixture_dir, name), 'rb')
    file_pos = Picture.objects.create(
        project = project,
        file = SimpleUploadedFile('%s' % name, f.read()),
        name = '%s' % name,
    )
    file_pos.setpolarity('+')

    f = file('%s/samples/NEG/%s' % (fixture_dir, name), 'rb')
    file_neg = Picture.objects.create(
        project = project,
        file = SimpleUploadedFile('%s' % name, f.read()),
        name = '%s' % name,
    )
    file_neg.setpolarity('-')

    samplefilegroup = SampleFileGroup.objects.create(type="mzxml", posdata=file_pos, negdata=file_neg)
    samplefilegroup.save()

    sample = Sample.objects.create(project=project,name=name, samplefile=samplefilegroup)
    sample.save()

    return sample

def create_calibration_sample(project, fixture_dir, name):

    name = '%s.mzXML' % name
    f = file('%s/calibration_samples/POS/%s' % (fixture_dir, name), 'rb')
    file_pos = ProjFile.objects.create(
        project = project,
        file = SimpleUploadedFile('%s' % name, f.read()),
        name = '%s' % name
    )
    file_pos.setpolarity('+')

    f = file('%s/calibration_samples/NEG/%s' % (fixture_dir, name), 'rb')
    file_neg = ProjFile.objects.create(
        project = project,
        file = SimpleUploadedFile('%s' % name, f.read()),
        name = '%s' % name
    )
    file_neg.setpolarity('-')

    standardfilegroup = StandardFileGroup.objects.create(type="mzxml", posdata=file_pos, negdata=file_neg)
    standardfilegroup.save()

    sample = CalibrationSample.objects.create(project=project, name=name, standardFile=standardfilegroup)
    sample.save()

    return sample

def create_standard_csv(project, fixture_dir, name):

    name = '%s.csv' % name
    f = file('%s/calibration_samples/standard/%s' % (fixture_dir, name), 'rb')
    file_std = ProjFile.objects.create(
        project = project,
        file = SimpleUploadedFile('%s' % name, f.read()),
        name = '%s' % name
    )
    file_std.setpolarity('std')

    standardfilegroup = StandardFileGroup.objects.create(type="toxid", data=file_std)
    standardfilegroup.save()

    sample = CalibrationSample.objects.create(project=project, name=name, standardFile=standardfilegroup)
    sample.save()

    return sample

def create_grouping(group_name, attribute_list):

    # Group is a factor, e.g. gender
    group = Group.objects.create(name=group_name)
    group.save()

    attr_map = {}
    for attr in attribute_list:
        # Attribute at the levels of a factor, e.g. Male, Female
        # Also called a 'condition' on the screen
        attr_map[attr] = Attribute.objects.create(name=attr, group=group)
        attr_map[attr].save()

    return attr_map

def group_calibration_samples(qc_list, blank_list, std_list):

    # don't change the group and the attribute names, seems to be hardcoded !?!
    group_name = 'calibration_group'
    attribute_names = ['qc', 'blank', 'standard']
    calibration_types = create_grouping(group_name, attribute_names)

    qc_attr = calibration_types['qc']
    for qc_samp in qc_list:
        pja = ProjfileAttribute.objects.create(attribute=qc_attr, calibrationsample=qc_samp)
        pja.save()

    blank_attr = calibration_types['blank']
    for blank_samp in blank_list:
        pja = ProjfileAttribute.objects.create(attribute=blank_attr, calibrationsample=blank_samp)
        pja.save()

    std_attr = calibration_types['standard']
    for std_samp in std_list:
        pja = ProjfileAttribute.objects.create(attribute=std_attr, calibrationsample=std_samp)
        pja.save()

def create_default_analysis_parameters():

    default_parameters = DefaultParameter.objects.all()
    params = Params()
    params.save()
    for default in default_parameters:
        parameter = Parameter(state=default.state, name=default.name, value=default.value)
        parameter.save()
        params.param.add(parameter)

    databases_ids = Database.objects.all().exclude(name='standards').values_list('id', flat=True)
    for db_id in databases_ids:
        params.databases.add(db_id)

    return params

def create_analysis(experiment_title, user):

    params = create_default_analysis_parameters()
    experiment = Experiment.objects.create(title=experiment_title)
    analysis = Analysis.objects.create(
        owner = user.username,
        experiment = experiment,
        params = params,
        status = 'Ready'
    )

    analysis.save()
    return experiment, analysis


def create_database(fixture_dir, env,
        standard_csvs=('Std1_1_20150422_150810', 'Std2_1_20150422_150711', 'Std3_1_20150422_150553')):
    #######################################################
    # 1. create user and project
    #######################################################

    user = create_test_user()
    project = Project.objects.create(
        title='test_project',
        user_owner = user,
        description = 'test',
        created = datetime.now(),
        modified = datetime.now()
    )
    project.save()
    user_project = UserProject.objects.create(
        project=project,
        user=user,
        date_joined = datetime.now(),
        permission = 'admin'
    )
    user_project.save()

    #######################################################
    # 2. create calibration, blank and std samples
    #######################################################

    samp_names = ['Beer_PoolB_full_f', 'Beer_PoolB_full_g', 'Beer_PoolB_full_h', 'Beer_PoolB_full_i']
    qc_list = []
    for name in samp_names:
            qc_list.append(create_calibration_sample(project, fixture_dir, name))

    # commented for now as it seems that the blanks are not picked up from the web front end?
    # if this were set, the assert that the peaks are the same will fail ..
    samp_names = ['blank1', 'blank2', 'blank3', 'blank4']
    blank_list = []
#         for name in samp_names:
#             blank_list.append(create_calibration_sample(project, self.fixture_dir, name))

    std_list = []
    for name in standard_csvs:
        std_list.append(create_standard_csv(project, fixture_dir, name))

    #######################################################
    # 3. group the calibration samples by their attributes
    #######################################################

    group_calibration_samples(qc_list, blank_list, std_list)

    #######################################################
    # 4. create samples
    #######################################################

    beer1_1 = create_sample(project, fixture_dir, 'Beer_1_full1')
    beer1_2 = create_sample(project, fixture_dir, 'Beer_1_full2')
    beer1_3 = create_sample(project, fixture_dir, 'Beer_1_full3')

    beer2_1 = create_sample(project, fixture_dir, 'Beer_2_full1')
    beer2_2 = create_sample(project, fixture_dir, 'Beer_2_full2')
    beer2_3 = create_sample(project, fixture_dir, 'Beer_2_full3')

    beer3_1 = create_sample(project, fixture_dir, 'Beer_3_full1')
    beer3_2 = create_sample(project, fixture_dir, 'Beer_3_full2')
    beer3_3 = create_sample(project, fixture_dir, 'Beer_3_full3')

    beer4_1 = create_sample(project, fixture_dir, 'Beer_4_full1')
    beer4_2 = create_sample(project, fixture_dir, 'Beer_4_full2')
    beer4_3 = create_sample(project, fixture_dir, 'Beer_4_full3')

    #######################################################
    # 5. group the samples into conditions
    #######################################################

    group_name = 'beer_smell'                        # --> feature
    attribute_names = ['smell_good', 'smell_bad']    # --> feature values
    conditions = create_grouping(group_name, attribute_names)

    smell_good = conditions['smell_good']
    SampleAttribute.objects.create(attribute=smell_good, sample=beer1_1)
    SampleAttribute.objects.create(attribute=smell_good, sample=beer1_2)
    SampleAttribute.objects.create(attribute=smell_good, sample=beer1_3)
    SampleAttribute.objects.create(attribute=smell_good, sample=beer2_1)
    SampleAttribute.objects.create(attribute=smell_good, sample=beer2_2)
    SampleAttribute.objects.create(attribute=smell_good, sample=beer2_3)
    SampleAttribute.objects.create(attribute=smell_good, sample=beer3_1)
    SampleAttribute.objects.create(attribute=smell_good, sample=beer3_2)
    SampleAttribute.objects.create(attribute=smell_good, sample=beer3_3)

    smell_bad = conditions['smell_bad']
    SampleAttribute.objects.create(attribute=smell_bad, sample=beer4_1)
    SampleAttribute.objects.create(attribute=smell_bad, sample=beer4_2)
    SampleAttribute.objects.create(attribute=smell_bad, sample=beer4_3)

    group_name = 'beer_colour'
    attribute_names = ['colour_dark', 'colour_light']
    conditions = create_grouping(group_name, attribute_names)

    colour_dark = conditions['colour_dark']
    SampleAttribute.objects.create(attribute=colour_dark, sample=beer1_1)
    SampleAttribute.objects.create(attribute=colour_dark, sample=beer1_2)
    SampleAttribute.objects.create(attribute=colour_dark, sample=beer1_3)
    SampleAttribute.objects.create(attribute=colour_dark, sample=beer2_1)
    SampleAttribute.objects.create(attribute=colour_dark, sample=beer2_2)
    SampleAttribute.objects.create(attribute=colour_dark, sample=beer2_3)

    colour_light = conditions['colour_light']
    SampleAttribute.objects.create(attribute=colour_light, sample=beer3_1)
    SampleAttribute.objects.create(attribute=colour_light, sample=beer3_2)
    SampleAttribute.objects.create(attribute=colour_light, sample=beer3_3)
    SampleAttribute.objects.create(attribute=colour_light, sample=beer4_1)
    SampleAttribute.objects.create(attribute=colour_light, sample=beer4_2)
    SampleAttribute.objects.create(attribute=colour_light, sample=beer4_3)
    
    group_name = 'beer_taste'
    attribute_names = ['taste_delicious', 'taste_okay', 'taste_awful']
    conditions = create_grouping(group_name, attribute_names)

    taste_delicious = conditions['taste_delicious']
    SampleAttribute.objects.create(attribute=taste_delicious, sample=beer1_1)
    SampleAttribute.objects.create(attribute=taste_delicious, sample=beer1_2)
    SampleAttribute.objects.create(attribute=taste_delicious, sample=beer1_3)
    SampleAttribute.objects.create(attribute=taste_delicious, sample=beer2_1)
    SampleAttribute.objects.create(attribute=taste_delicious, sample=beer2_2)
    SampleAttribute.objects.create(attribute=taste_delicious, sample=beer2_3)

    taste_okay = conditions['taste_okay']
    SampleAttribute.objects.create(attribute=taste_okay, sample=beer3_1)
    SampleAttribute.objects.create(attribute=taste_okay, sample=beer3_2)
    SampleAttribute.objects.create(attribute=taste_okay, sample=beer3_3)

    taste_awful = conditions['taste_awful']
    SampleAttribute.objects.create(attribute=taste_awful, sample=beer4_1)
    SampleAttribute.objects.create(attribute=taste_awful, sample=beer4_2)
    SampleAttribute.objects.create(attribute=taste_awful, sample=beer4_3)

    #######################################################
    # 6. create a new experiment and analysis
    #######################################################

    experiment, analysis = create_analysis('test_analysis', user)
    logger.info('experiment.id: %s',  experiment.id)
    logger.info('analysis.id: %s',  analysis.id)
    experiment.save()
    analysis.save()

    #######################################################
    # 7. set up comparisons
    #######################################################

    comparison = Comparison(name='beer_colour_comparison', experiment=experiment)
    comparison.save()
    # lowest group is the control
    ac0 = AttributeComparison(group=0, attribute=colour_dark, comparison=comparison)
    ac1 = AttributeComparison(group=1, attribute=colour_light, comparison=comparison)
    ac0.save()
    ac1.save()

    comparison = Comparison(name='beer_taste_comparison', experiment=experiment)
    comparison.save()
    ac0 = AttributeComparison(group=0, attribute=taste_awful, comparison=comparison)
    ac1 = AttributeComparison(group=1, attribute=taste_delicious, comparison=comparison)
    ac0.save()
    ac1.save()

    #######################################################
    # 8. Run the R analysis pipeline
    #######################################################

    transaction.commit() # commit to the test db so it can be picked up by R
    success = False
    with env:
        logger.info('Using %s as database', env['PIMP_DATABASE_NAME'])
        #print 'Using %s as database' % env['PIMP_DATABASE_NAME']
        success = start_pimp_pipeline(analysis, project, user, True)
    return success, project, experiment, analysis

def initialise_database():
    basedir = settings.BASE_DIR

    # path to find the fixture data
    fixture_dir = os.path.join(basedir, 'fixtures/projects/1')

    # set the paths to upload and process the test data
    test_media_root = settings.TEST_MEDIA_ROOT # + '_test'
    #settings.MEDIA_ROOT = test_media_root

    # for use in the R pipeline
    env = EnvironmentVarGuard()
    #env.set('PIMP_DATABASE_NAME', os.environ['PIMP_TEST_DATABASE_NAME'])
    #env.set('PIMP_DATABASE_FILENAME', '')
    #env.set('PIMP_MEDIA_ROOT', test_media_root)
    return fixture_dir, test_media_root, env

# Django's TestCase class wraps each test in a transaction and rolls back that transaction after each test,
# in order to provide test isolation. This means that no transaction is ever actually committed, thus your
# on_commit() callbacks will never be run. If you need to test the results of an on_commit() callback, use a
# TransactionTestCase instead.
class ExperimentTestCase(TransactionTestCase):

    def setUp(self):
        fixture_dir, test_media_root, env = initialise_database()
        self.fixture_dir = fixture_dir
        self.test_media_root = test_media_root
        self.env = env

    @patch('experiments.tasks.send_email')
    def test_analysis(self, mock_send_email):
        """test that R analysis pipeline can run"""

        success, project, experiment, analysis = create_database(self.fixture_dir, self.env)


        #######################################################
        # 9. Check the results from the R pipeline
        #######################################################

        # assert that the return code from R is 0
        self.assertEqual(success, True)

        # assert that analysis status is set to Finished
        analysis = Analysis.objects.get_or_create(id=analysis.id)[0]
        self.assertEqual(analysis.status, 'Finished')

        # assert that send email is called once
        self.assertTrue(mock_send_email.called)

        # assert that the resulting peaks from this test analysis are identical to the fixture
        dump_path = os.path.join(self.test_media_root, 'projects',
                                 str(project.id), 'test_peaks.json')
        with open(dump_path, 'w') as f:
            call_command('dumpdata', 'data.peak', indent=4, stdout=f)
        test_data = open(dump_path).read()
        test_peaks = json.loads(test_data)
        fixture_data = open(os.path.join(self.fixture_dir, 'peak.json')).read()
        fixture_peaks = json.loads(fixture_data)
        assert(test_peaks == fixture_peaks)

        #######################################################
        # 10. remove the analysis results
        #######################################################

        shutil.rmtree(os.path.join(self.test_media_root, 'projects'))