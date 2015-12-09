Pimp.report.generatePathwayStatistics <- function(pathways=pathways, compound.info=compound.info, compound.std.ids=compound.std.ids, identified.compounds.by.pathway=identified.compounds.by.pathway, toptables=toptables) {
	pathway.stats <- pathways#[-which(pathways$number.compounds==0),]
	#pathway.stats$id <- sub("path:", "", pathway.stats$id)
	putative.compounds <- identified.compounds <- unique.peaks <- percentage.represented <- rep(0, length(pathway.stats$id))
	diff.metab <- matrix(ncol=length(toptables), nrow=length(pathway.stats$id), data=0, dimnames=list(1:length(pathway.stats$id), names(toptables)))

	#kegg.info <- identification[which(identification$DB=="kegg"),]

	for(i in 1:length(pathway.stats$id)) {
		#putative compounds
		compounds <- identified.compounds.by.pathway[[pathway.stats$id[i]]]
		putative.compounds[i] <- length(compounds)
		#unique metabolites - think about best way to do this!
		# unique.peaks.idx <- compound.info which(compound.info$DBID %in% compounds)
		# unique.peaks[i] <- length(unique()) 

		#percentage represented
		percentage.represented[i] <- round(((length(compounds) / pathway.stats$number.compounds[i]) * 100), digits=1)
		#stds matched
		identified.compounds[i] <- length(which(compounds %in% compound.std.ids))
		#differentially metabolised compounds
		for(j in 1:length(toptables)) {
			contrast <- names(toptables)[j]
			table <- toptables[[contrast]]
			sig.metabolites <- rownames(table)[which(table$adj.P.Val < 0.05)]
			sig.compound.ids <- unique(compound.info$DBID[which(compound.info$id %in% sig.metabolites)])  ##check!!!
			diff.metab[i,contrast] <- length(which(compounds %in% sig.compound.ids))
		}

		
	}

	pathway.stats <- cbind(pathway.stats, putative.compounds, identified.compounds, percentage.represented, diff.metab)
	pathway.stats <- pathway.stats[-which(pathway.stats$putative.compounds==0),]
	#pathway.stats <- pathway.stats[with(pathway.stats, order(-percentage.represented, -number.compounds, id)),]
	max.active <- sort(sapply(names(toptables), function(x){ max(pathway.stats[,x])}), decreasing=TRUE)
	sort.order <- match(c(names(max.active), "percentage.represented"), colnames(pathway.stats))
	pathway.stats <- pathway.stats[do.call(order, -pathway.stats[,sort.order]),]
	#pathway.stats <- pathway.stats[order(-pathway.stats[,sort.order]),]

	pathway.stats$putative.compounds <- pathway.stats$putative.compounds - pathway.stats$identified.compounds

	return(pathway.stats)
}

.get.identified.compounds.by.pathways <- function(ids=character(), compounds2Pathways=list()) {
	compounds.id.by.pathway <- list()
	#for(i in 1:length(ids)) {
	for ( id in ids ) {

		# compound.pathways <- names(compounds2Pathways[[paste('cpd:',id,sep="")]])
		#print(ids[i])
		compound.pathways <- compounds2Pathways[[id]]
		if(!is.null(compound.pathways)) {
			for(cp in 1:length(compound.pathways)) {
				pathway <- compound.pathways[cp]
				compounds.id.by.pathway[[pathway]] <- append(compounds.id.by.pathway[[pathway]], id)
			}
		}
	}
	return(compounds.id.by.pathway)
}
	