from django.db import models
from data.models import Peak, PeakDtComparison, Dataset
from collections import defaultdict

import numpy as np
import re

# Create your models here.
class Compound(models.Model):
	secondaryId = models.IntegerField(null=True, blank=True)
	peak = models.ForeignKey(Peak)
	formula = models.CharField(max_length=100)
	inchikey = models.CharField(max_length=27, null=True, blank=True)
	# name = models.CharField(max_length=250)
	# db = models.CharField(max_length=100)
	# dbId = models.CharField(max_length=100)
	# dbLink = models.CharField(max_length=250)
	ppm = models.FloatField(null=True, blank=True)
	adduct = models.CharField(max_length=100)
	identified = models.CharField(max_length=10)
	# pathways = models.ManyToManyField(Pathway, through='CompoundPathway')

	class Meta:
		ordering = ['secondaryId']


class RepositoryCompound(models.Model):
	db_name = models.CharField(max_length=100)
	identifier = models.CharField(max_length=100)
	compound_name = models.CharField(max_length=250)
	compound = models.ForeignKey(Compound)

	class Meta:
		ordering = ['db_name']

	def __unicode__(self):
		return self.db_name

class Pathway(models.Model):
	name = models.CharField(max_length=200)

	def get_pathway_url(self, dataset_id, comparison_id=None):
# 		map_id = self.secondaryId
# 		compounds = self.compound.all()
		# dsrcsp: shortcut for "datasource_super_pathway"
		dsrcsp = DataSourceSuperPathway.objects.filter(data_source__name="kegg", pathway=self).first()
		# dsrcsp = self.datasourcesuperpathway_set.all().filter(data_source__name="kegg").first()
		map_id = dsrcsp.identifier

		if DataSourceSuperPathway.objects.filter(data_source__name="kegg", pathway=self, compoundpathway__compound__peak__dataset_id=dataset_id):
			compounds = Compound.objects


# 		kegg_identified_compounds = self.get_pathway_compounds(id_type="identified")
# 		kegg_annotated_compounds = self.get_pathway_compounds(id_type="annotated")

# 		overlap = np.intersect1d(kegg_identified_compounds.keys(), kegg_annotated_compounds.keys())
# 		for key in overlap:
# 			kegg_annotated_compounds.pop(key)

# 		foreground_colours=dict.fromkeys(kegg_annotated_compounds.keys(), "grey")
# 		foreground_colours.update(dict.fromkeys(kegg_identified_compounds.keys(), "gold"))
# 		background_colours = foreground_colours.copy()

# 		if comparison_id:
# 			all_compounds = dict(kegg_identified_compounds.items() + kegg_annotated_compounds.items())
# 			for compound in all_compounds:
# 				sig_fold_changes = PeakDtComparison.objects.filter(peak_id__in=all_compounds[compound], comparison_id=comparison_id, adjPvalue__lt=0.05)
# 				fold_change_colours = []
# 				fold_change_direction = []
# 				fold_change_value = []

# 				for sig_fc in sig_fold_changes:
# 					colour = sig_fc.get_fold_change_colour()
# 					if colour:
# 						fold_change_colours.append(colour)
# 						fold_change_direction.append(sig_fc._get_fold_change_direction())
# 						fold_change_value.append(sig_fc.logFC)

# 				if fold_change_colours:
# 					if "down" in fold_change_direction and "up" in fold_change_direction:
# 						background_colours[compound] = "purple"
# 					else:
# 						fold_change_value = [abs(x) for x in fold_change_value]
# 						minimum = min(fold_change_value)
# 						background_colours[compound] = fold_change_colours[fold_change_value.index(minimum)]

# 		url = self._build_kegg_url(map_id, foreground_colours, background_colours)

# 		return url


# 	def get_pathway_compounds(self, id_type=None):
# 		if id_type=="identified":
# 			compounds = self.compound.filter(identified=True).distinct()
# 		elif id_type=="annotated":
# 			identified_compounds = self.compound.filter(identified=True).distinct()
# 			compounds = self.compound.filter(identified=False).exclude(secondaryId__in=identified_compounds.values_list("secondaryId", flat=True)).distinct()
# 		else:
# 			compounds = self.compound.distinct()

# 		kegg_compounds = defaultdict(list)
# 		for compound in compounds:
# 			repos_objs = compound.repositorycompound_set.filter(db_name="kegg")
# 			if repos_objs:
# 				for ro in repos_objs:
# 					kegg_compounds[ro.identifier].append(compound.peak_id)				

# 		return kegg_compounds

# 	def _build_kegg_url(self, map_id, foreground_colours, background_colours):
# 		url = "http://www.kegg.jp/kegg-bin/show_pathway?" + map_id

# 		for compound in background_colours.keys():
# 			url += "/%s%%09%s,%s" % (compound, foreground_colours[compound], background_colours[compound]) #compound + "%%09" + foreground_colours[compound] + "," background_colours[compound]

# 		url = self._clean_url(url)
		
# 		return url

# 	def _clean_url(self, url):
# 		url = re.sub(" ", "%20", url)
# 		url = re.sub("#", "%23", url)
# 		url = re.sub(":", "%3a", url)
# 		url =re.sub("http%3a//", "http://", url)

# 		return url

class SuperPathway(models.Model):
	name = models.CharField(max_length=200)

class DataSource(models.Model):
	name = models.CharField(max_length=100)

class DataSourceSuperPathway(models.Model):
	super_pathway = models.ForeignKey(SuperPathway)
	pathway = models.ForeignKey(Pathway)
	data_source = models.ForeignKey(DataSource)
	compound_number = models.IntegerField(max_length=10, null=True, blank=True)
	identifier = models.CharField(max_length=100, null=True, blank=True)

# class Pathway(models.Model):
# 	secondaryId = models.CharField(max_length=100)
# 	name = models.CharField(max_length=100)
# 	compoundNumber = models.IntegerField(null=True, blank=True)
# 	# pathwayMap = models.CharField(max_length=250)
# 	compound = models.ManyToManyField(Compound, through='CompoundPathway')

# 	def get_pathway_url(self, comparison_id=None):
# 		map_id = self.secondaryId
# 		compounds = self.compound.all()

# 		kegg_identified_compounds = self.get_pathway_compounds(id_type="identified")
# 		kegg_annotated_compounds = self.get_pathway_compounds(id_type="annotated")

# 		overlap = np.intersect1d(kegg_identified_compounds.keys(), kegg_annotated_compounds.keys())
# 		for key in overlap:
# 			kegg_annotated_compounds.pop(key)

# 		foreground_colours=dict.fromkeys(kegg_annotated_compounds.keys(), "grey")
# 		foreground_colours.update(dict.fromkeys(kegg_identified_compounds.keys(), "gold"))
# 		background_colours = foreground_colours.copy()

# 		if comparison_id:
# 			all_compounds = dict(kegg_identified_compounds.items() + kegg_annotated_compounds.items())
# 			for compound in all_compounds:
# 				sig_fold_changes = PeakDtComparison.objects.filter(peak_id__in=all_compounds[compound], comparison_id=comparison_id, adjPvalue__lt=0.05)
# 				fold_change_colours = []
# 				fold_change_direction = []
# 				fold_change_value = []

# 				for sig_fc in sig_fold_changes:
# 					colour = sig_fc.get_fold_change_colour()
# 					if colour:
# 						fold_change_colours.append(colour)
# 						fold_change_direction.append(sig_fc._get_fold_change_direction())
# 						fold_change_value.append(sig_fc.logFC)

# 				if fold_change_colours:
# 					if "down" in fold_change_direction and "up" in fold_change_direction:
# 						background_colours[compound] = "purple"
# 					else:
# 						fold_change_value = [abs(x) for x in fold_change_value]
# 						minimum = min(fold_change_value)
# 						background_colours[compound] = fold_change_colours[fold_change_value.index(minimum)]

# 		url = self._build_kegg_url(map_id, foreground_colours, background_colours)

# 		return url


# 	def get_pathway_compounds(self, id_type=None):
# 		if id_type=="identified":
# 			compounds = self.compound.filter(identified=True).distinct()
# 		elif id_type=="annotated":
# 			identified_compounds = self.compound.filter(identified=True).distinct()
# 			compounds = self.compound.filter(identified=False).exclude(secondaryId__in=identified_compounds.values_list("secondaryId", flat=True)).distinct()
# 		else:
# 			compounds = self.compound.distinct()

# 		kegg_compounds = defaultdict(list)
# 		for compound in compounds:
# 			repos_objs = compound.repositorycompound_set.filter(db_name="kegg")
# 			if repos_objs:
# 				for ro in repos_objs:
# 					kegg_compounds[ro.identifier].append(compound.peak_id)				

# 		return kegg_compounds

# 	def _build_kegg_url(self, map_id, foreground_colours, background_colours):
# 		url = "http://www.kegg.jp/kegg-bin/show_pathway?" + map_id

# 		for compound in background_colours.keys():
# 			url += "/%s%%09%s,%s" % (compound, foreground_colours[compound], background_colours[compound]) #compound + "%%09" + foreground_colours[compound] + "," background_colours[compound]

# 		url = self._clean_url(url)
		
# 		return url

# 	def _clean_url(self, url):
# 		url = re.sub(" ", "%20", url)
# 		url = re.sub("#", "%23", url)
# 		url = re.sub(":", "%3a", url)
# 		url =re.sub("http%3a//", "http://", url)

# 		return url

class CompoundPathway(models.Model):
	compound = models.ForeignKey(Compound)
	pathway = models.ForeignKey(DataSourceSuperPathway)

	