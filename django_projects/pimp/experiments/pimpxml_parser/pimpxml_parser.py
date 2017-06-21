#!/usr/bin/python2.7
# -*-coding:Utf-8 -*

from lxml import etree


class Xmltree:

    """
    Xmltree is the based object that allow you to access all object in your xml file
    """

    def __init__(self, inputDoc):
        self.file = inputDoc
        self.tree = etree.parse(inputDoc)
        self.root = self.tree.getroot()

    def getAnalysisId(self):

        """ 
        return analysis id in the file
        """

        # pathway_id = str(id)
        analysis_id = self.tree.xpath('/gpimp:pimp_analysis/@id',
                                      namespaces={'gpimp':'http://puma.ibls.gla.ac.uk/ns/gpimp/1.0'})
        if len(analysis_id) > 0:
            return int(analysis_id[0])
        else:
            return None

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
            return peaks
        else:
            return None

    def getPeaks(self):

        """
        return peak elements list
        """

        peaks = self.tree.xpath("//peak")
        if len(peaks) > 0:
            return peaks
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

    def getPeakMassFromElement(self,peak):

        """ 
        return peak mass from peak element
        """

        mass = peak.xpath("./mass/text()")[0]
        return float(mass)

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

    def getPeakRtFromElement(self,peak):

        """ 
        return peak retention time from peak element
        """

        rt = peak.xpath("./retention_time/text()")[0]
        return float(rt)

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

    def getPeakPolarityFromElement(self,peak):

        """ 
        return peak polarity from peak element
        """

        polarity = peak.xpath("./polarity/text()")[0]
        return polarity

    def getPeakTypeFromElement(self,peak):

        """ 
        return peak polarity from peak element
        """

        peak_type = peak.xpath("./type/text()")[0]
        return peak_type

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

    def getPeakInfoFromElement(self, peak):

        """ 
        return peak info from peak element
        """

        mass = self.getPeakMassFromElement(peak)
        rt = self.getPeakRtFromElement(peak)
        polarity = self.getPeakPolarityFromElement(peak)
        peak_type = self.getPeakTypeFromElement(peak)
        return {"mass":mass,"retention_time":rt,"polarity":polarity,"peak_type":peak_type}


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


    def getCompoundsFromElement(self,peak):

        """ 
        return list of compounds in a peak from peak element
        """

        compounds = peak.xpath("./compoundset/compound")
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


    def getCompoundId(self,compound):

        """ 
        return if of compound from compound element
        """

        id = compound.xpath("./@id")[0]
        return int(id)


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

    def getCompoundFormulaFromElement(self, compound):

        """ 
        return compound formula from compound element
        """

        formula = compound.xpath("./formula/text()")[0]
        return formula


    def getCompoundInchikeyFromElement(self, compound):

        """ 
        return compound inchikey from compound element
        """
        if compound.xpath("./inchikey/text()"):
            inchikey = compound.xpath("./inchikey/text()")[0]
            return inchikey
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

    # Deprecated
    # def getCompoundNameFromElement(self, compound):

    # 	"""
    # 	return compound name from compound element
    # 	"""

    # 	name = compound.xpath("./name/text()")[0]
    # 	return name


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


    def getCompoundDbFromElement(self, compound):

        """ 
        return compound database from compound element
        """

        db = compound.xpath("./db/text()")[0]
        return db


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


    def getCompoundDbIdFromElement(self, compound):

        """ 
        return compound database id from compound element
        """

        dbId = compound.xpath("./dbid/text()")[0]
        return dbId


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


    def getCompoundPpmFromElement(self, compound):

        """ 
        return compound ppm from compound element
        """

        ppm = compound.xpath("./ppm/text()")[0]
        return float(ppm)


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

    def getCompoundAdductFromElement(self, compound):

        """ 
        return compound adduct from compound element
        """

        adduct = compound.xpath("./adduct/text()")[0]
        return adduct


    def getCompoundIdentified(self, id):

        """ 
        return compound identification status from compound id
        """

        compound_id = str(id)
        if len(self.tree.xpath("//compound[@id='"+compound_id+"']")) > 0:
            identified = self.tree.xpath("//compound[@id='"+compound_id+"']/identified/text()")[0]
            if (identified == "True") or (identified == "Identified"):
                return True
            else:
                return False
        else:
            return None

    def getCompoundIdentifiedFromElement(self, compound):

        """ 
        return compound identification status from compound element
        """

        identified = compound.xpath("./identified/text()")[0]
        if (identified == "True") or (identified == "Identified"):
            return True
        else:
            return False


    def getCompoundInfo(self, id):

        """ 
        return all compound information from compound id
        """

        compound_id = str(id)
        if len(self.tree.xpath("//compound[@id='"+compound_id+"']")) > 0:
            formula = self.getCompoundFormula(id)
            # name = self.getCompoundName(id)
            # db = self.getCompoundDb(id)
            # dbId = self.getCompoundDbId(id)
            # dbLink = self.getCompoundDbLink(id)
            ppm = self.getCompoundPpm(id)
            adduct = self.getCompoundAdduct(id)
            identified = self.getCompoundIdentified(id)
            return {"formula":formula,"ppm":ppm,"adduct":adduct,"identified":identified}
        else:
            return None

    def getCompoundInfoFromElement(self, compound):

        """ 
        return all compound information from compound element
        """
        id = self.getCompoundId(compound)
        formula = self.getCompoundFormulaFromElement(compound)
        # name = self.getCompoundNameFromElement(compound)
        # db = self.getCompoundDbFromElement(compound)
        # dbId = self.getCompoundDbIdFromElement(compound)
        # dbLink = self.getCompoundDbLink(id)
        inchikey = self.getCompoundInchikeyFromElement(compound)
        ppm = self.getCompoundPpmFromElement(compound)
        adduct = self.getCompoundAdductFromElement(compound)
        identified = self.getCompoundIdentifiedFromElement(compound)
        return {"id":id,"formula":formula, "inchikey":inchikey, "ppm":ppm,"adduct":adduct,"identified":identified}

    def getCompoundDbsFromElement(self, compound):

        """ 
        return list of dbs in a compound from compound element
        """

        dbs = compound.xpath("./dbset/db")
        if len(dbs) > 0:
            return dbs
        else:
            return None


    def getDbNameFromElement(self, db):

        """
        return db name from a db element
        """

        db_name = db.xpath("./db_name/text()")[0]
        return db_name


    def getDbIdentifierFromElement(self, db):

        """
        return db name from a db element
        """

        identifier = db.xpath("./identifier/text()")[0]
        return identifier


    def getCompoundNameFromElement(self, db):

        """
        return db name from a db element
        """

        compound_name = db.xpath("./compound_name/text()")[0]
        return compound_name


    def getDbInfoFromElement(self, db):

        """ 
        return all db information from db element
        """

        db_name = self.getDbNameFromElement(db)
        identifier = self.getDbIdentifierFromElement(db)
        compound_name = self.getCompoundNameFromElement(db)
        return {"db_name":db_name, "identifier":identifier, "compound_name":compound_name}


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


    def getComparisonsFromElement(self, peak):

        """ 
        return list of comparisons in a peak from peak element
        """

        comparisons = peak.xpath("./comparisonset/comparison")
        if len(comparisons) > 0:
            return comparisons
        else:
            return None


    def getComparisonId(self,comparison):

        """ 
        return id of comparison from comparison element
        """

        id = comparison.xpath("./@id")[0]
        return int(id)


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


    def getComparisonLogfcFromElement(self, comparison):

        """ 
        return comparison log fold change from comparison element
        """

        logfc = comparison.xpath("./logfc/text()")[0]
        return logfc


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


    def getComparisonPvalueFromElement(self, comparison):

        """ 
        return comparison Pvalue from comparison element
        """

        pvalue = comparison.xpath("./pvalue/text()")[0]
        return pvalue


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


    def getComparisonAdjPvalueFromElement(self, comparison):

        """ 
        return comparison adjusted Pvalue from comparison element
        """

        adjPvalue = comparison.xpath("./adjpvalue/text()")[0]
        return adjPvalue


    def getComparisonLogOddsFromElement(self, comparison):

        """ 
        return comparison log odds from comparison element
        """

        logOdds = comparison.xpath("./logodds/text()")[0]
        return logOdds


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


    def getComparisonInfoFromElement(self, comparison):

        """ 
        return all db information from db element
        """

        id = self.getComparisonId(comparison)
        logfc = self.getComparisonLogfcFromElement(comparison)
        pvalue = self.getComparisonPvalueFromElement(comparison)
        adjpvalue = self.getComparisonAdjPvalueFromElement(comparison)
        logodds = self.getComparisonLogOddsFromElement(comparison)
        return {"id":id, "logfc":logfc, "pvalue":pvalue, "adjpvalue":adjpvalue, "logodds":logodds}


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

    def getSampleReferenceIdsFromElement(self,peak):

        """ 
        return list of samples ids in a peak from peak id
        """

        sampleReferences = peak.xpath("./sample_intensity_set/sample_reference/@id")
        if len(sampleReferences) > 0:
            return map(int, sampleReferences)
        else:
            return None

    def getSampleReferencesFromElement(self,peak):

        """ 
        return list of sample elements in a peak from peak element
        """

        sampleReferences = peak.xpath("./sample_intensity_set/sample_reference")
        if len(sampleReferences) > 0:
            return sampleReferences
        else:
            return None

    def getCalibrationReferencesFromElement(self,peak):

        """ 
        return list of calibration sample elements in a peak from peak element
        """

        calibrationReferences = peak.xpath("./calibration_intensity_set/calibration_reference")
        if len(calibrationReferences) > 0:
            return calibrationReferences
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

    def getSampleReferenceIntensityFromElement(self, sampleReference):

        """ 
        return sample peak intensity from sample reference element
        """

        intensity = sampleReference.xpath("./intensity/text()")[0]
        try:
            return float(intensity)
        except ValueError:
            return 0

    def getCalibrationReferenceIntensityFromElement(self, calibrationReference):

        """ 
        return sample peak intensity from sample reference element
        """

        intensity = calibrationReference.xpath("./intensity/text()")[0]
        try:
            return float(intensity)
        except ValueError:
            return 0

    def getSampleReferenceId(self, sampleReference):

        """ 
        return sample reference id from sample reference element
        """

        id = sampleReference.xpath("./@id")[0]
        return int(id)

    def getCalibrationReferenceId(self, calibrationReference):

        """ 
        return sample reference id from sample reference element
        """

        id = calibrationReference.xpath("./@id")[0]
        return int(id)

    def getPathways(self):

        """
        return pathway elements list
        """

        pathways = self.tree.xpath("//pathway")
        return pathways
        #if len(pathways) > 0:
        #	return pathways
        #else:
        #	return None


    def getPathwayId(self,pathway):

        """ 
        return id of pathway from pathway element
        """

        id = pathway.xpath("./@id")[0]
        return id


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


    def getPathwayNameFromElement(self,pathway):

        """ 
        return pathway name from pathway element
        """

        name = pathway.xpath("./name/text()")[0]
        return name


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


    def getPathwayCompoundNumberFromElement(self,pathway):

        """ 
        return number of compound in pathway from pathway element
        """

        compoundNumber = pathway.xpath("./compound_number/text()")[0]
        return int(compoundNumber)


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


    def getPathwayInfoFromElement(self, pathway):

        """
        return all pathway info from pathway element
        """

        id = self.getPathwayId(pathway)
        name = self.getPathwayNameFromElement(pathway)
        compoundNumber = self.getPathwayCompoundNumberFromElement(pathway)
        return {"id":id,"name":name,"compoundNumber":compoundNumber}


    def getCompoundsInPathwayFromElement(self, pathway):

        """
        return list of compound in pathway from pathway element
        """

        compoundsInPathway = pathway.xpath("./compound_in_pathwayset/compound_in_pathway")
        if len(compoundsInPathway) > 0:
            return compoundsInPathway
        else:
            return None


    def getCompoundInPathwayIdFromElement(self, compound_in_pathway):

        """ 
        return id of compound_in_pathway from compound_in_pathway element
        """

        id = compound_in_pathway.xpath("./@id")[0]
        return int(id)



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

# class Peak:

# 	def __init__(self, mass, rt):
# 		self.mass = mass
# 		self.rt = rt
# 		self.compounds = []
# 		self.samplepeaks = []
# 		self.comparisonpeaks = []

# class Samplepeak:

# 	def __init__(self, intensity, sample):
# 		self.intensity = intensity
# 		self.sample = sample

# class Comparisonpeak:

# 	def __init__(self, logFC, Pvalue, adjPvalue, comparison):
# 		self.logFC = logFC
# 		self.Pvalue = Pvalue
# 		self.adjPvalue = adjPvalue
# 		self.comparison = comparison

# class Compound:

# 	def __init__(self, formula, name, db, db_id, ppm, adduct, std):
# 		self.formula = formula
# 		self.name = name
# 		self.db = db
# 		self.db_id = db_id
# 		# self.db_link = db_link
# 		self.ppm = ppm
# 		self.adduct = adduct
# 		self.std = std

# 	def print_out(self):
# 		print "formula :",self.formula
# 		print "name ",self.name
# 		print "db ",self.db
# 		print "db_id ",self.db_id
# 		print "ppm ",self.ppm
# 		print "adduct ",self.adduct
# 		print "std ",self.std

# class Sample:

# 	def __init__(self, name):
# 		self.name = name

# class Comparison:

# 	def __init__(self, name):
# 		self.name = name


# def main():
# 	xmltree = Xmltree("pimpfile.xml")
# 	# print xmltree.root
# 	# print etree.tostring(xmltree.root, pretty_print=True)
# 	# print xmltree.tree.xpath("//sample")[4].attrib["id"]
# 	print "______________________________________________________________________"
# 	print "id of first peak in the file: ",xmltree.allPeaks()[0].attrib["id"]
# 	# print "All compounds in the file: "
# 	print "number of peaks :"
# 	print len(xmltree.allPeaks())
# 	print "number of compounds :"
# 	print len(xmltree.allCompounds())
# 	print "members in the group id=10 :"
# 	print xmltree.getMembers(10)
# 	print "name of group id=10 :"
# 	print xmltree.getGroupName(10)
# 	print "name of member id=40 :"
# 	print xmltree.getMemberName(40)
# 	print "name of sample id=6 :"
# 	print xmltree.getSampleName(6)
# 	print "member ids in comparison id=1 :"
# 	print xmltree.getMemberReferenceId(1)
# 	print xmltree.getPeakMass(1)
# 	print xmltree.getPeakInfo(1)
# 	print xmltree.getCompoundIds(1)
# 	print xmltree.getCompoundInfo(1)
# 	print xmltree.getComparisonIds(1)
# 	print xmltree.getComparisonLogfc(1,1)
# 	print xmltree.getComparisonPvalue(1,1)
# 	print xmltree.getComparisonAdjPvalue(1,1)
# 	print xmltree.getComparisonInfo(1,1)
# 	print xmltree.getSampleReferenceIds(1)
# 	print xmltree.getSampleReferenceIntensity(1,3)
# 	print xmltree.getPathwayIds()
# 	print xmltree.getPathwayInfo(1)
# 	print xmltree.getCompoundInPathway(1)
# # def getSample


# if __name__ == "__main__":
# 	main()