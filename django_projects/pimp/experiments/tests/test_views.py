import timeit

from django.test import TestCase, override_settings
from experiments.models import Analysis, Attribute
from fileupload.models import Sample
from experiments.views import get_best_hits_comparison


class BestHitsTestCase(TestCase):
    fixtures = ['test_database.fixture.json']

    def setup(self):
        pass

    @override_settings(DEBUG=True)
    def test_get_best_hits_comparison(self):
        analysis = Analysis.objects.first()
        dataset = analysis.dataset_set.all()[0]
        comparisons = analysis.experiment.comparison_set.all().order_by('id')
        s = Sample.objects.filter(
            attribute=Attribute.objects.filter(comparison=comparisons).distinct().order_by('id')).distinct().order_by(
            'attribute__id', 'id')
        comp_start = timeit.default_timer()
        experiments.views.get_best_hits_comparison(dataset, comparisons, s)
        comp_stop = timeit.default_timer()
        print("comp time: %s", str(comp_stop - comp_start))
