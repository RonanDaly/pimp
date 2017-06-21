#!/usr/bin/python2.7
# -*-coding:Utf-8 -*

from lxml import etree

class Xmltree:

    """
    Xmltree load and parse the given xml file, it provides methods to navigate within the xml file and exctrat all information.
    See Xmltree Methods below
    """

    def __init__(self, inputDoc):
        self.file = inputDoc
        self.tree = etree.parse(inputDoc)
        self.root = self.tree.getroot()


    def allGroups(self):

        """ 
        return all groups in the file
        """

        groups = self.tree.xpath("//group")
        if len(groups) > 0:
            return groups
        else:
            return None

    def allMembers(self):

        """ 
        return all members in the file
        """

        members = self.tree.xpath("//member")
        if len(members) > 0:
            return members
        else:
            return None

    def allSamples(self):

        """
        return all samples in the file
        """

        samples = self.tree.xpath("//sample")
        if len(samples) > 0:
            return samples
        else:
            return None

    def allMemberComparisons(self):

        """ 
        return all member_comparisons in the file
        """

        memberComparisons = self.tree.xpath("//member_comparison")
        if len(memberComparisons) > 0:
            return memberComparisons
        else:
            return None

    def allParameters(self):

        """
        return all parameters in the file
        """

        parameters = self.tree.xpath("//parameter")
        if len(parameters) > 0:
            return parameters
        else:
            return None

    def allPeaks(self):

        """
        return all peaks in the file
        """

        peaks = self.tree.xpath("//peak")
        if len(peaks) > 0:
            return peaks
        else:
            return None

    def allCompounds(self):

        """ 
        return all compopunds in the file
        """

        compounds = self.tree.xpath("//compound")
        if len(compounds) > 0:
            return compounds
        else:
            return None

    def allComparisons(self):

        """ 
        return all comparisons in the file
        """

        comparisons = self.tree.xpath("//comparison")
        if len(comparisons) > 0:
            return comparisons
        else:
            return None

    def allSampleReferences(self):

        """ 
        return all sample_reference in the file
        """

        sampleReferences = self.tree.xpath("//sample_reference")
        if len(sampleReferences) > 0:
            return sampleReferences
        else:
            return None

    def allPathways(self):

        """ 
        return all pathways in the file
        """

        pathways = self.tree.xpath("//pathway")
        if len(pathways) > 0:
            return pathways
        else:
            return None

    def allCompoundInPathways(self):

        """ 
        return all compound_in_pathway in the file
        """

        compoundInPathways = self.tree.xpath("//compound_in_pathway")
        if len(compoundInPathways) > 0:
            return compoundInPathways
        else:
            return None

    def getMembers(self,id):

        """ 
        return list of members in a group from group id
        """

        group_id = str(id)
        members = self.tree.xpath("//group[@id='"+group_id+"']/memberset/member")
        if len(members) > 0:
            return members
        else:
            return None

    def getGroupName(self,id):

        """ 
        return group name from group id
        """

        group_id = str(id)
        if len(self.tree.xpath("//group[@id='"+group_id+"']")) > 0:
            group_name = self.tree.xpath("//group[@id='"+group_id+"']/name/text()")[0]
            return group_name
        else:
            return None

    def getMemberName(self,id):

        """ 
        return member name from member id
        """

        member_id = str(id)
        if len(self.tree.xpath("//member[@id='"+member_id+"']")) > 0:
            member_name = self.tree.xpath("//member[@id='"+member_id+"']/name/text()")[0]
            return member_name
        else:
            return None

    def getSamples(self,id):

        """ 
        return list of samples in a member from member id
        """

        member_id = str(id)
        samples = self.tree.xpath("//member[@id='"+member_id+"']/sampleset/sample")
        if len(samples) > 0:
            return samples
        else:
            return None

    def getSampleName(self,id):

        """ 
        return sample name from sample id
        """

        sample_id = str(id)
        if len(self.tree.xpath("//sample[@id='"+sample_id+"']")) > 0:
            sample_name = self.tree.xpath("//sample[@id='"+sample_id+"']/name/text()")[0]
            return sample_name
        else:
            return None

    def getMemberReferenceId(self,id):

        """ 
        return list of members id in a member_comparison element from member_comparison id
        """

        member_comparison_id = str(id)
        if len(self.tree.xpath("//member_comparison[@id='"+member_comparison_id+"']")) > 0:
            member_id_1 = self.tree.xpath("//member_comparison[@id='"+member_comparison_id+"']/member_reference")[0].attrib["id"]
            member_id_2 = self.tree.xpath("//member_comparison[@id='"+member_comparison_id+"']/member_reference")[1].attrib["id"]
            return map(int, [member_id_1,member_id_2])
        else:
            return None

    def getPeakIds(self):

        """ 
        return list of peak ids
        """

        peaks = self.tree.xpath("//peak/@id")
        if len(peaks) > 0:
            return map(int, peaks)
        else:
            return None

    def getPeakMass(self,id):

        """ 
        return peak mass from peak id
        """

        peak_id = str(id)
        if len(self.tree.xpath("//peak[@id='"+peak_id+"']")) > 0:
            mass = self.tree.xpath("//peak[@id='"+peak_id+"']/mass/text()")[0]
            return float(mass)
        else:
            return None

    def getPeakRT(self,id):

        """ 
        return peak retention time from peak id
        """

        peak_id = str(id)
        if len(self.tree.xpath("//peak[@id='"+peak_id+"']")) > 0:
            rt = self.tree.xpath("//peak[@id='"+peak_id+"']/retention_time/text()")[0]
            return float(rt)
        else:
            return None

    def getPeakPolarity(self,id):

        """ 
        return peak polarity from peak id
        """

        peak_id = str(id)
        if len(self.tree.xpath("//peak[@id='"+peak_id+"']")) > 0:
            polarity = self.tree.xpath("//peak[@id='"+peak_id+"']/polarity/text()")[0]
            return polarity
        else:
            return None

    def getPeakInfo(self, id):

        """ 
        return peak info from peak id
        """

        peak_id = str(id)
        if len(self.tree.xpath("//peak[@id='"+peak_id+"']")) > 0:
            mass = self.getPeakMass(id)
            rt = self.getPeakRT(id)
            polarity = self.getPeakPolarity(id)
            return {"mass":mass,"retention_time":rt,"polarity":polarity}
        else:
            return None


    def getCompounds(self,id):

        """ 
        return list of compounds in a peak from peak id
        """

        peak_id = str(id)
        compounds = self.tree.xpath("//peak[@id='"+peak_id+"']/compoundset/compound")
        if len(compounds) > 0:
            return compounds
        else:
            return None


    def getCompoundIds(self,id):

        """ 
        return list of compound ids in a peak from peak id
        """

        peak_id = str(id)
        compounds = self.tree.xpath("//peak[@id='"+peak_id+"']/compoundset/compound/@id")
        if len(compounds) > 0:
            return map(int, compounds)
        else:
            return None

    def getCompoundFormula(self, id):

        """ 
        return compound formula from compound id
        """

        compound_id = str(id)
        if len(self.tree.xpath("//compound[@id='"+compound_id+"']")) > 0:
            formula = self.tree.xpath("//compound[@id='"+compound_id+"']/formula/text()")[0]
            return formula
        else:
            return None

    def getCompoundName(self, id):

        """ 
        return compound name from compound id
        """

        compound_id = str(id)
        if len(self.tree.xpath("//compound[@id='"+compound_id+"']")) > 0:
            name = self.tree.xpath("//compound[@id='"+compound_id+"']/name/text()")[0]
            return name
        else:
            return None

    def getCompoundDb(self, id):

        """ 
        return compound database from compound id
        """

        compound_id = str(id)
        if len(self.tree.xpath("//compound[@id='"+compound_id+"']")) > 0:
            db = self.tree.xpath("//compound[@id='"+compound_id+"']/db/text()")[0]
            return db
        else:
            return None

    def getCompoundDbId(self, id):

        """ 
        return compound database id from compound id
        """

        compound_id = str(id)
        if len(self.tree.xpath("//compound[@id='"+compound_id+"']")) > 0:
            dbId = self.tree.xpath("//compound[@id='"+compound_id+"']/dbid/text()")[0]
            return dbId
        else:
            return None

    def getCompoundDbLink(self, id):

        """
        Deprecated
        """

        compound_id = str(id)
        if len(self.tree.xpath("//compound[@id='"+compound_id+"']")) > 0:
            dbLink = self.tree.xpath("//compound[@id='"+compound_id+"']/dblink/text()")[0]
            return dbLink
        else:
            return None

    def getCompoundPpm(self, id):

        """ 
        return compound ppm from compound id
        """

        compound_id = str(id)
        if len(self.tree.xpath("//compound[@id='"+compound_id+"']")) > 0:
            ppm = self.tree.xpath("//compound[@id='"+compound_id+"']/ppm/text()")[0]
            return float(ppm)
        else:
            return None

    def getCompoundAdduct(self, id):

        """ 
        return compound adduct from compound id
        """

        compound_id = str(id)
        if len(self.tree.xpath("//compound[@id='"+compound_id+"']")) > 0:
            adduct = self.tree.xpath("//compound[@id='"+compound_id+"']/adduct/text()")[0]
            return adduct
        else:
            return None

    def getCompoundIdentified(self, id):

        """ 
        return compound identification status from compound id
        """

        compound_id = str(id)
        if len(self.tree.xpath("//compound[@id='"+compound_id+"']")) > 0:
            identified = self.tree.xpath("//compound[@id='"+compound_id+"']/identified/text()")[0]
            if identified == "True":
                return True
            else:
                return False
        else:
            return None

    def getCompoundInfo(self, id):

        """ 
        return all compound information from compound id
        """

        compound_id = str(id)
        if len(self.tree.xpath("//compound[@id='"+compound_id+"']")) > 0:
            formula = self.getCompoundFormula(id)
            name = self.getCompoundName(id)
            db = self.getCompoundDb(id)
            dbId = self.getCompoundDbId(id)
            # dbLink = self.getCompoundDbLink(id)
            ppm = self.getCompoundPpm(id)
            adduct = self.getCompoundAdduct(id)
            identified = self.getCompoundIdentified(id)
            return {"formula":formula,"name":name,"db":db,"dbId":dbId,"ppm":ppm,"adduct":adduct,"identified":identified}
        else:
            return None


    def getComparisons(self,id):

        """ 
        return list of comparison in a peak from peak id
        """

        peak_id = str(id)
        comparisons = self.tree.xpath("//peak[@id='"+peak_id+"']/comparisonset/comparison")
        if len(comparisons) > 0:
            return comparisons
        else:
            return None

    def getComparisonIds(self,id):

        """ 
        return list of comparison ids in a peak from peak id
        """

        peak_id = str(id)
        comparisons = self.tree.xpath("//peak[@id='"+peak_id+"']/comparisonset/comparison/@id")
        if len(comparisons) > 0:
            return map(int, comparisons)
        else:
            return None

    def getComparisonLogfc(self, peak_id, comparison_id):

        """ 
        return comparison log fold change from peak and comparison id
        """

        peak_id = str(peak_id)
        comparison_id = str(comparison_id)
        if len(self.tree.xpath("//peak[@id='"+peak_id+"']/comparisonset/comparison[@id='"+comparison_id+"']")) > 0:
            logFC = self.tree.xpath("//peak[@id='"+peak_id+"']/comparisonset/comparison[@id='"+comparison_id+"']/logfc/text()")[0]
            return float(logFC)
        else:
            return None

    def getComparisonPvalue(self, peak_id, comparison_id):

        """ 
        return comparison p-value from peak and comparison id
        """

        peak_id = str(peak_id)
        comparison_id = str(comparison_id)
        if len(self.tree.xpath("//peak[@id='"+peak_id+"']/comparisonset/comparison[@id='"+comparison_id+"']")) > 0:
            pvalue = self.tree.xpath("//peak[@id='"+peak_id+"']/comparisonset/comparison[@id='"+comparison_id+"']/pvalue/text()")[0]
            return float(pvalue)
        else:
            return None

    def getComparisonAdjPvalue(self, peak_id, comparison_id):

        """ 
        return comparison adjusted p-value from peak and comparison id
        """

        peak_id = str(peak_id)
        comparison_id = str(comparison_id)
        if len(self.tree.xpath("//peak[@id='"+peak_id+"']/comparisonset/comparison[@id='"+comparison_id+"']")) > 0:
            adjPvalue = self.tree.xpath("//peak[@id='"+peak_id+"']/comparisonset/comparison[@id='"+comparison_id+"']/adjpvalue/text()")[0]
            return float(adjPvalue)
        else:
            return None

    def getComparisonInfo(self, peak_id, comparison_id):

        """ 
        return all comparison information from peak and comparison id
        """

        peakId = str(peak_id)
        comparisonId = str(comparison_id)
        if len(self.tree.xpath("//peak[@id='"+peakId+"']/comparisonset/comparison[@id='"+comparisonId+"']")) > 0:
            logFC = self.getComparisonLogfc(peak_id,comparison_id)
            pvalue = self.getComparisonPvalue(peak_id,comparison_id)
            adjPvalue = self.getComparisonAdjPvalue(peak_id,comparison_id)
            return {"logfc":logFC,"pvalue":pvalue,"adjpvalue":adjPvalue}
        else:
            return None

    def getSampleReferenceIds(self,id):

        """ 
        return list of samples ids in a peak from peak id
        """

        peak_id = str(id)
        sampleReferences = self.tree.xpath("//peak[@id='"+peak_id+"']/sample_intensity_set/sample_reference/@id")
        if len(sampleReferences) > 0:
            return map(int, sampleReferences)
        else:
            return None

    def getSampleReferenceIntensity(self, peak_id, sampleReference_id):

        """ 
        return sample peak intensity from peak id and sample id
        """

        peak_id = str(peak_id)
        sampleReference_id = str(sampleReference_id)
        if len(self.tree.xpath("//peak[@id='"+peak_id+"']/sample_intensity_set/sample_reference[@id='"+sampleReference_id+"']")) > 0:
            intensity = self.tree.xpath("//peak[@id='"+peak_id+"']/sample_intensity_set/sample_reference[@id='"+sampleReference_id+"']/intensity/text()")[0]
            return float(intensity)
        else:
            return None

    def getPathwayIds(self):

        """ 
        return list of pathway ids in the file
        """

        # pathway_id = str(id)
        pathways = self.tree.xpath("//pathway/@id")
        if len(pathways) > 0:
            return pathways
        else:
            return None

    def getPathwayName(self,id):

        """ 
        return pathway name from pathway id
        """

        pathway_id = str(id)
        if len(self.tree.xpath("//pathway[@id='"+pathway_id+"']")) > 0:
            name = self.tree.xpath("//pathway[@id='"+pathway_id+"']/name/text()")[0]
            return name
        else:
            return None

    def getPathwayCompoundNumber(self,id):

        """ 
        return number of compound in pathway from pathway id
        """

        pathway_id = str(id)
        if len(self.tree.xpath("//pathway[@id='"+pathway_id+"']")) > 0:
            compoundNumber = self.tree.xpath("//pathway[@id='"+pathway_id+"']/compound_number/text()")[0]
            return int(compoundNumber)
        else:
            return None

    def getPathwayMap(self,id):

        """ 
        Deprecated 
        """

        pathway_id = str(id)
        if len(self.tree.xpath("//pathway[@id='"+pathway_id+"']")) > 0:
            pathwayMap = self.tree.xpath("//pathway[@id='"+pathway_id+"']/pathway_map/text()")[0]
            return pathwayMap
        else:
            return None

    def getPathwayInfo(self, id):

        """ 
        return all pathway info from pathway id
        """

        pathway_id = str(id)
        if len(self.tree.xpath("//pathway[@id='"+pathway_id+"']")) > 0:
            name = self.getPathwayName(id)
            compoundNumber = self.getPathwayCompoundNumber(id)
            # pathwayMap = self.getPathwayMap(id)
            return {"name":name,"compoundNumber":compoundNumber}
        else:
            return None

    def getCompoundInPathway(self, id):

        """ 
        return list of compound ids in pathway from pathway id
        """

        pathway_id = str(id)
        if len(self.tree.xpath("//pathway[@id='"+pathway_id+"']")) > 0:
            compoundIds = self.tree.xpath("//pathway[@id='"+pathway_id+"']/compound_in_pathwayset/compound_in_pathway/@id")
            if len(compoundIds) > 0:
                return map(int, compoundIds)
            else:
                return None


