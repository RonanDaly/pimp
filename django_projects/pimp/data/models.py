from django.db import models
from experiments.models import Comparison, Analysis
from groups.models import Attribute
from fileupload.models import Sample, CalibrationSample

# Create your models here.
class Dataset(models.Model):
	created = models.DateTimeField(auto_now_add=True)
	analysis = models.ForeignKey(Analysis)

class Peak(models.Model):
	dataset = models.ForeignKey(Dataset)
	# This is used for display purposes -- each peak in a analysis has an id from 1 to n
	secondaryId = models.IntegerField(null=True, blank=True, db_index=True)
	mass = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
	rt = models.DecimalField(max_digits=20, decimal_places=10, blank=True, null=True)
	polarity = models.CharField(max_length=8, blank=True, null=True)
	type = models.CharField(max_length=100, blank=True, null=True)
	# dtsamples = models.ManyToManyField(DtSample, through='PeakDTSample')

	class Meta:
		ordering = ['secondaryId']

	def _minimum_intensities_present(self, samples, cutoff=2/3):
   		intensities = self.peakdtsample_set.filter(sample__in=samples).values_list("intensity", flat=True)
		percent_present = len([x for x in intensities if x > 0]) / len(intensities)
    	
		return percent_present > cutoff

	def __unicode__(self):
		return "Peak at mz: {}, rt: {}".format(self.mass,self.rt)


# class DtMember(models.Model):
# 	name = models.CharField(max_length=100)

# class DtSample(models.Model):
# 	# dataset = models.ForeignKey(Dataset, blank=True, null=True)
# 	name = models.CharField(max_length=100)
# 	sample = models.ForeignKey(Sample, blank=True, null=True)
# 	# dtmember = models.ForeignKey(DtMember, blank=True, null=True)
# 	peaks = models.ManyToManyField(Peak, through='PeakDTSample')

class PeakDTSample(models.Model):
	# member = models.ForeignKey(Attribute)
	# peakMember = models.ForeignKey(PeakMember)
	peak = models.ForeignKey(Peak)
	sample = models.ForeignKey(Sample)
	# name = models.CharField(max_length=100)
	intensity = models.FloatField(null=True, blank=True)
	# polarity = models.CharField(max_length=1, blank=True, null=True)


class PeakQCSample(models.Model):
	# member = models.ForeignKey(Attribute)
	# peakMember = models.ForeignKey(PeakMember)
	peak = models.ForeignKey(Peak)
	sample = models.ForeignKey(CalibrationSample)
	# name = models.CharField(max_length=100)
	intensity = models.FloatField(null=True, blank=True)
# class DtComparison(models.Model):
# 	dataset = models.ForeignKey(Dataset, blank=True, null=True)
# 	comparison = models.ForeignKey(Comparison)

class PeakDtComparison(models.Model):
	peak = models.ForeignKey(Peak)
	comparison = models.ForeignKey(Comparison)
	logFC = models.FloatField(null=True, blank=True)
	pValue = models.FloatField(null=True, blank=True)
	adjPvalue = models.FloatField(null=True, blank=True)
	logOdds = models.FloatField(null=True, blank=True)

	class Meta:
		ordering = ['comparison']

	def __unicode__(self):
		return u'%s' % (self.logFC)

	def is_significant(self, cutoff=0.05):
		if self.adjPvalue < cutoff:
			return True
		else:
			return False

	def get_fold_change_colour(self):
	#get_fold_change_colour()
		up_colours = ["#FF6666", "#FF9999", "#FFCCCC"]
		down_colours = ["#6666FF", "#9999FF", "#CCCCFF"]
		fold_change_bins = [2, 1, 0.5849625]

		colours = []
		if self.logFC > 0:
			colours = up_colours
		else:
			colours = down_colours

		log_fc = abs(self.logFC)

		colour = None
		for idx, fc in enumerate(fold_change_bins):
			if log_fc > fc:
				colour = colours[idx]
				break

		return colour

	def _get_fold_change_direction(self):
		if self.logFC > 0:
			return "up"
		elif self.logFC < 0:
			return "down"



# class PeakMemberComparisonPeak(models.Model):
# 	peakMember = models.ForeignKey(PeakMember)
# 	comprisonPeak = models.ForeignKey(ComparisonPeak)
# 	control = models.BooleanField()


