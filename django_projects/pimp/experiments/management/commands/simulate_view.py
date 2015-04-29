# from django.core.management.base import NoArgsCommand
# Command to run in order to create dataset on database, replace the file by "yourFile"
# python manage.py create_dataset "/Users/yoanngloaguen/Documents/ideomWebSite/lydia_for_yoann.xml"
from django.core.management.base import BaseCommand
from fileupload.models import Sample
from experiments.models import Comparison, Analysis
from data.models import *
from compound.models import *


class Command(BaseCommand):
	def handle(self, *args, **options):
		try:
			project = Project.objects.get(pk=2)
			analysis = Analysis.objects.get(pk=3)
			user = request.user
			permission = project.userproject_set.get(user=user).permission
		except Project.DoesNotExist:
			raise Http404
		comparisons = analysis.experiment.comparison_set.all()
		# print comparisons
		dataset = analysis.dataset_set.all()[0]
		compounds = Compound.objects.filter(peak__dataset=dataset)
		print dataset
		member_set = set()
		for comparison in comparisons:
			member_set = member_set.union(set(comparison.attribute.all()))
		member_list = list(member_set)
		member_list.append(Sample.objects.get(id=47).attribute_set.all()[0])
		print member_list[0].id

		print "member list: ",member_list
		sample_member_hash = {}
		sample_list = []
		for member in member_list:
			sample_list.append(list(member.sample.all()))
			for sample in member.sample.all():
				sample_member_hash[sample] = member_list.index(member)
		print "sample member hash: ",sample_member_hash
		# sample_list.append([Sample.objects.get(id=46),Sample.objects.get(id=47)])
		print "sample list: ",sample_list
		peak_set = dataset.peak_set.all()
		peak_table = {}
		databases = []
		pca_table = []
		for peak in peak_set:
			intensity_list = [[None]*len(samples) for samples in sample_list]#len(member_list)
			for peak_dt_sample in peak.peakdtsample_set.all():
				i = sample_member_hash[peak_dt_sample.sample]
				# print i
				# print sample_list[i]
				# print type(sample_list[i])
				j = sample_list[i].index(peak_dt_sample.sample)
				intensity_list[i][j] = peak_dt_sample
			peak_table[peak] = intensity_list
			pca_table.append([item.intensity for sublist in intensity_list for item in sublist])
			for compound in peak.compound_set.all():
				for repository in compound.repositorycompound_set.all():
					if repository.db_name not in databases:
						databases.append(repository.db_name)
				# if len(compound.repositorycompound_set.all()) > databases_nb:
				# 	databases_nb = len(compound.repositorycompound_set.all())
			if peak.secondaryId == 50:
				break
		print ("hah pca")

		############################################################################
		############################# PCA calculation ##############################
		############################################################################
		pca_table = np.array(pca_table)
		pca_matrix = pca_table.T
		# print "pca_table :",pca_matrix
		index_of_zero = np.where(pca_matrix == 0)[1]
		# print "len pca matrix 1 :", len(pca_matrix[0])
		# print "index_of_zero : ",index_of_zero
		pca_matrix = np.delete(pca_matrix, index_of_zero, 1)
		# print "after delete : ",np.where(pca_matrix == 0)[1]
		log_pca_matrix = np.log2(pca_matrix)

		# print "len pca matrix 1 :", pca_matrix[0][0]
		# print "len log pca matrix 1 :", log_pca_matrix[0][0]
		# for yty in log_pca_matrix[0]:
		# 	print yty
		pcan = mdp.nodes.PCANode(output_dim=3, svd=True)
		pcar = pcan.execute(log_pca_matrix)


		# print "pcar ",pcar
		# print "pcan ",pcan.d[0],"  ",pcan.d[1]
		# print "pcan again",pcan.d
		# print "explained variance : ",pcan.explained_variance


		pca_info = [pcan.d[0],pcan.d[1]]
		pca_data_point = []
		i = 0
		j = 0
		for member in sample_list:
			pca_serie = [member_list[j].name]
			for sample in member:
				dic = []
				dic.append(sample.name)
				dic.append(pcar[i][0])
				dic.append(pcar[i][1]) 
				pca_serie.append(dic)
				i += 1
			pca_data_point.append(pca_serie)
			j += 1
		pca_info.append(pca_data_point)
		# print "pca_series: ",pca_data_point
		############################################################################
		########################## End PCA calculation #############################
		############################################################################

		############################################################################
		########################## Best hits comparison ############################
		############################################################################
		comparison_hits_list = {}
		for c in comparisons:
			identified_peak = Peak.objects.filter(dataset__analysis=analysis,compound__identified='True')
			annotated_peak = Peak.objects.filter(dataset__analysis=analysis).exclude(compound__identified='True')

			identified_peakdtcomparisonList = c.peakdtcomparison_set.exclude(adjPvalue__gt=0.05).filter(peak__in=identified_peak).extra(select={"absLogFC": "abs(logFC)"}).order_by("-absLogFC")
			annotated_peakdtcomparisonList = c.peakdtcomparison_set.exclude(adjPvalue__gt=0.05).filter(peak__in=annotated_peak).extra(select={"absLogFC": "abs(logFC)"}).order_by("-absLogFC")



			identified_info_list = []
			for identified_compound in identified_peakdtcomparisonList:
				compound_name = list(set(RepositoryCompound.objects.filter(compound__peak__peakdtcomparison=identified_compound,compound__identified="True").values_list('compound_name', flat=True)))
				intensities = get_intensities_values(identified_compound)
				identified_info_list.append([identified_compound,compound_name,intensities])

			annotated_info_list = []
			for annotated_compound in annotated_peakdtcomparisonList:
				intensities = get_intensities_values(annotated_compound)
				annotated_info_list.append([annotated_compound,intensities])

			comparison_hits = [identified_info_list,annotated_info_list]
			comparison_hits_list[c] = comparison_hits
		print "comparison hits: ",comparison_hits_list

		############################################################################
		######################## End Best hits comparison ##########################
		############################################################################


		databases.sort()
		databases = map(str, databases)
		# print "databases: ",databases

		pathways = Pathway.objects.filter(compound__peak__dataset=dataset).distinct()
		print "pathway : ",len(pathways)
		pathway_list = []

		for pathway in pathways:
			all_compounds = pathway.compound.all()
			identified = 0
			annotated = 0
			identified_kegg_id = []
			annotated_kegg_id = []
			distinct_compound = set([c.secondaryId for c in all_compounds])
			for secondary_compound_id in distinct_compound:
				if "True" in pathway.compound.filter(secondaryId=secondary_compound_id).values_list('identified', flat=True):
					identified += 1
					compounds_list = pathway.compound.filter(secondaryId=secondary_compound_id)
					tmp_id_list = RepositoryCompound.objects.filter(compound=compounds_list).filter(db_name='kegg').values_list('identifier',flat=True)
					identified_kegg_id = identified_kegg_id + list(tmp_id_list)
				else:
					annotated += 1
					compounds_list = pathway.compound.filter(secondaryId=secondary_compound_id)
					tmp_id_list = RepositoryCompound.objects.filter(compound=compounds_list).filter(db_name='kegg').values_list('identifier',flat=True)
					annotated_kegg_id = annotated_kegg_id + list(tmp_id_list)
			coverage = round(((annotated+identified)*100)/float(pathway.compoundNumber),2)
			info = [pathway,identified,annotated,coverage,[list(set(identified_kegg_id)),list(set(annotated_kegg_id))]]
			pathway_list.append(info)
		print "pathway len ",len(pathway_list)
		# print "pathway list ",pathway_list[0]
		# print "compound number ",pathway_list[0][0].compoundNumber

		peak_comparison_list = Peak.objects.filter(peakdtcomparison__comparison=comparisons,dataset__analysis=analysis)
		# print intensity_list
		# print intensity_list[0]
		c = {'peak_table': peak_table,
			'member_list': member_list,
			'sample_list': sample_list,
			'pathway_list': pathway_list,
			'databases': databases,
			'dataset': dataset,
			'compounds': compounds,
			'project': project,
			'analysis': analysis,
			'peak_comparison_list': peak_comparison_list,
			'comparisons': comparisons,
			'pca_data_point': pca_info,
			'comparison_hits_list': comparison_hits_list,
		}
		# print len(peak_set)
		return render(request, 'base_result3.html', c)