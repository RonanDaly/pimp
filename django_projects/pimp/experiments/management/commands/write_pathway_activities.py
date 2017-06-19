from django.core.management.base import BaseCommand, CommandError
from experiments.pipelines.pathway_analysis import PlageAnalysis
from experiments.models import Analysis

# Run in docker using: honcho run python manage.py write_pathway_activities analysis.id
# where analysis.id is just an integer

class Command(BaseCommand):
    args = 'Analysis - a chosen analysis'
    help = 'Calculates and writes a csv file for the pathway activities in an Analysis'

    def handle(self, *args, **options):

        try:
            analysis = Analysis.objects.get(id=args[0])
            plage_analysis = PlageAnalysis(analysis)
            activity_df = plage_analysis.get_plage_activity_df()
            plage_analysis.write_activity_df(activity_df)

        except Exception as e:
            raise CommandError(e, "Something went horribly wrong")
