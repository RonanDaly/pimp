Pimp.exportToExcel <- function(file=NULL, databases=character(), stds.db=NULL, raw.data=data.frame(), groups=list(), identification=data.frame(), preprocessed=list(), diff.stats=NULL, toptables=list(), pathway.stats=data.frame(), identified.compounds.by.pathway=list(), compound.ids=character(), compound.std.ids=character(), compound.info=data.frame()) {
	if(is.null(file)) {
		file <- paste("analysis_", format(Sys.time(), "%Y%m%d%H%M%S"), ".xlsx", sep="")
	}
	file.copy(system.file("xlsx", "analysis.xlsx", package=getPackageName()), file.path(getwd(), file))
	if(!file.exists(file)) {
		stop(paste(file, "not found."))
	}
	workbook = loadWorkbook(file, create = FALSE) #check whether exists
	
	#setStyles(workbook)

	##raw data sheet
	message("Creating Raw Sheet")
	raw.data.sheet <- .createRawSheet(workbook=workbook, raw.data=raw.data, groups=groups)

	##pathway sheet
	message("Creating Pathway Data")
	pathway.sheet <- .createPathwaySheet(workbook=workbook, pathway.stats=pathway.stats, identified.compounds.by.pathway=identified.compounds.by.pathway, compound.std.ids=compound.std.ids, compound.info=compound.info, toptables=toptables)

	##identification
	message("Creating Identification Sheet")
	identification.sheet <- .createIdentificationSheet(workbook=workbook, identification=identification, databases=databases, stds.db=stds.db)

	##comparison sheet
	if(ncol(diff.stats$contrasts) > 1) {
		message("Creating Comparison Sheet")	
		comparison.sheet <- .createComparisonSheet(workbook=workbook, diff.stats=diff.stats, preprocessed=preprocessed, identification=identification)
	}

	##contrast sheet
	message("Creating Contrasts Sheets")	
	contrasts.sheets <- .createContrastSheets(workbook=workbook, toptables=toptables, identification=identification)

	##potential sheet - those that may be interesting, but can't do stats
	message("Creating Potential Sheet")
	potential.sheet <- .createPotentialSheet(workbook=workbook, raw.data=raw.data, groups=groups, toptables=toptables, identification=identification)


	message("Sheets Created")

	saveWorkbook(workbook)

	message("Workbook saved")

	return(file)
}

.createRawSheet <- function(workbook=workbook(), raw.data=data.frame(), groups=list()) {
	raw.data.sheet <- createSheet(workbook, name="RawData")
	writeWorksheet(workbook, data=raw.data, sheet="RawData", header=TRUE, rownames="ID")
	setColumnWidth(workbook, sheet="RawData", column=1:ncol(raw.data))
	gc(reset=TRUE)
	return(raw.data)
}

.createIdentificationSheet <- function(workbook=workbook(), identification=data.frame(), databases=character(), stds.db=NULL) {
	#create id sheet
	sheet <- createSheet(workbook, name="Identification")
	#createName(workbook, name = "Identification", formula = "Identification!$A$1")
	#old.columns <- c("")
	identification <- identification[,c("id", "mass", "RT", "formula", "DB", "DBID", "names", "ppm", "adduct", "publishable", "InChIKey")]
	colnames(identification) <- c("ID", "Mass", "RT", "Formula", "DB", "DBID", "Name", "PPM", "Adduct", "Identification", "InChIKey")
	writeWorksheet(workbook, data=identification, sheet="Identification", header=TRUE)
	#writeNamedRegion(workbook, data=identification, name="Identification", header=TRUE)
	setColumnWidth(workbook, sheet="Identification", column=1:getLastColumn(workbook, "Identification"))
	gc(reset=TRUE)


	db.col <- which(names(identification)=="DB")
	dbid.col <- which(names(identification)=="DBID")
	#stds.db <- file_path_sans_ext(basename(stds.db))
	
	if(!is.null(stds.db) && file.exists(stds.db)) {	
		stds.db <- file_path_sans_ext(basename(stds.db))
		stds.idx <- which(identification$DB==stds.db)
		#stds.rows <- unlist(sapply(stds.idx,rep, times=getLastColumn(workbook, "Identification"),simplify=F))
		#stds.cols <- rep(1:getLastColumn(workbook, "Identification"), times=length(stds.idx))
		#setCellStyle(workbook, sheet="Identification", row=stds.rows + 1, col=stds.cols, cellstyle=getCellStyle(workbook, name="Bold"))
		setCellStyle(workbook, sheet="Identification", row=stds.idx + 1, col=db.col, cellstyle=getCellStyle(workbook, name="Bold"))
		gc(reset=TRUE)
	}

	#add external links

	db.idx <- which(identification$DB != stds.db)
	urls <- apply(identification[db.idx, c("DBID", "DB")], 1, function(x) {get.db.url(id=x['DBID'], db=x['DB'])})
	formula <- paste('HYPERLINK("', urls, '", "', identification$DBID[db.idx], '")', sep="")
	setCellFormula(workbook, "Identification", row=db.idx + 1, col=dbid.col, formula=formula)
	gc(reset=TRUE)
	setCellStyle(workbook, sheet="Identification", row=db.idx + 1, col=dbid.col, cellstyle=getCellStyle(workbook, name="Hyperlink"))
	for(d in 1:length(databases)) {
		db <- basename(file_path_sans_ext(databases[d]))
	 	db.idx <- which(identification$DB==db)

	 	ids <- identification$DBID[db.idx]
	 	urls <- sapply(ids, function(id){eval(parse(text=paste("get.", db, ".url('", id, "')", sep="")))})
	 	formula <- paste('HYPERLINK("', urls, '", "', ids, '")', sep="")
	 	setCellFormula(workbook, "Identification", row=db.idx + 1, col=dbid.col, formula=formula)
	 	setCellStyle(workbook, sheet="Identification", row=db.idx + 1, col=dbid.col, cellstyle=getCellStyle(workbook, name="Hyperlink"))
	}
	gc(reset=TRUE)

	return(sheet)	
}

.createComparisonSheet <- function(workbook=workbook(), diff.stats=NULL, preprocessed=list(), identification=data.frame()) {

	##differential statistics
	sheet <- createSheet(workbook, name="Comparison")
	#createName(workbook, name = "Comparison", formula = "Comparison!$A$1")
	

	#get table of significantly changed metabolites
	results <- decideTests(diff.stats)[,]

	#get fold changes and order as per results objec
	fold.changes <- topTable(diff.stats, number=length(diff.stats$coef[,1]), genelist=data.frame(Mass=preprocessed$Mass, RT=preprocessed$RT))
	row.idx <- match(rownames(results), rownames(fold.changes))
	fold.changes <- fold.changes[row.idx, c("Mass", "RT", gsub("-", ".", colnames(diff.stats$contrasts)))] #############change to do by names
	colnames(fold.changes) <- c("Mass", "RT", colnames(diff.stats$contrasts))

	#add results to Excel sheet
	writeWorksheet(workbook, data=fold.changes, sheet="Comparison", header=TRUE, rownames="ID")
	setColumnWidth(workbook, sheet="Comparison", column=1:getLastColumn(workbook, "Comparison"))

	col.idx <- match(colnames(results), colnames(fold.changes))
	for(i in seq(along = colnames(results))) {
		column <- colnames(results)[i]
		message(column)

		fold.bins <- fold.bins()

		for(j in 1:length(fold.bins)) {
			up.idx <- which(results[,column]==1 & fold.changes[,column] >= fold.bins[j]) #which(results[,column]==1)
			if(length(up.idx) > 0) {
				setCellStyle(workbook, sheet = "Comparison", row = up.idx + 1, col = col.idx[i] + 1, cellstyle = getCellStyle(workbook, name=paste("Up_bin_", j, sep="")))
			}

			down.idx <- which(results[,column]==-1 & fold.changes[,column] <= -fold.bins[j]) #down.idx <- which(results[,column]==-1)
			if(length(down.idx) > 0) {
				setCellStyle(workbook, sheet = "Comparison", row = down.idx + 1, col = col.idx[i] + 1, cellstyle = getCellStyle(workbook, name=paste("Down_bin_", j, sep="")))
			}
		}
	}

	# message("FOLD", class(rownames(fold.changes)))
	# message("ID", class(identification$id))
	link.idx <- which(rownames(fold.changes) %in% identification$id)
	# links <- rownames(fold.changes)[link.idx]
	# message("LINKS", links)

	formula <- paste('HYPERLINK("#Identification!A"&MATCH("', rownames(fold.changes)[link.idx], '",Identification!A1:A', getLastRow(workbook, "Identification"),',0),"', rownames(fold.changes)[link.idx], '")', sep="")
	#for(i in 1:length(formula)) {
		setCellFormula(workbook, "Comparison", row=link.idx + 1, col=1, formula=formula)
		setCellStyle(workbook, sheet="Comparison", row=link.idx + 1, col=1, cellstyle=getCellStyle(workbook, name="Hyperlink"))
	#}

	gc(reset=TRUE)

	return(sheet)
}

.createContrastSheets <- function(workbook=workbook(), toptables=list(), identification=data.frame()) {
	#contrast.sheets <-list()
	for(i in 1:length(names(toptables))) {
		print(paste(i,"\n"))
		#contrast.sheet <- createSheet(workbook, sheetName=names(toptables)[i])
		sheet <- createSheet(workbook, name=names(toptables)[i])
		#createName(workbook, name = names(toptables)[i], formula = paste(names(toptables)[i],"!$A$1",sep=""))
		table <- toptables[[names(toptables)[i]]]

		#writeNamedRegion(workbook, data=table, name=names(toptables)[i], header=TRUE)
		writeWorksheet(workbook,data=table,sheet=names(toptables)[i], header=TRUE, rownames="ID")
		setColumnWidth(workbook, sheet=names(toptables)[i], column=1:getLastColumn(workbook, names(toptables)[i]))

		link.idx <- which(rownames(table) %in% identification$id)
		formula <- paste('HYPERLINK("#Identification!A"&MATCH("', rownames(table)[link.idx], '",Identification!A1:A', getLastRow(workbook, "Identification"),',0),"', rownames(table)[link.idx], '")', sep="")
		setCellFormula(workbook, names(toptables)[i], row=link.idx + 1, col=1, formula=formula)
		setCellStyle(workbook, sheet=names(toptables)[i], row=link.idx + 1, col=1, cellstyle=getCellStyle(workbook, name="Hyperlink"))
	}
	gc(reset=TRUE)
}

.createPathwaySheet <- function(workbook=workbook(), pathway.stats=data.frame(), identified.compounds.by.pathway=list(), compound.std.ids=character(), compound.info=data.frame(), toptables=list()) {
	createSheet(workbook, name="Pathways")
	#createName(workbook, name = "Pathways", formula = "Pathways!$A$1")
	pathway.stats$id <- sub("path:", "", as.character(pathway.stats$id))
	names(identified.compounds.by.pathway) <- sub("path:", "", names(identified.compounds.by.pathway))
	colnames(pathway.stats)[1:6] <- c("Name", "ID", "Number of compounds", "Annotated", "Identified", "Coverage")
	writeWorksheet(workbook,data=pathway.stats,sheet="Pathways", header=TRUE)
	setColumnWidth(workbook, sheet="Pathways", column=1:getLastColumn(workbook, "Pathways"))
	
	#whole pathway markup
	putative.idx <- match("Number of compounds", colnames(pathway.stats))
	urls <- generate.kegg.pathway.links(pathway.ids=pathway.stats$ID, identified.compounds.by.pathway=identified.compounds.by.pathway, stds=compound.std.ids)
	
	if(length(urls) > 0) {
		.setExternalURLs(workbook=workbook, sheet="Pathways", urls=urls, link.names=pathway.stats$`Number of compounds`, rows.idx=1:length(urls), column.idx=putative.idx)
	}

	for(i in 1:length(toptables)) {
		contrast <- names(toptables)[i]
		column.idx <- match(contrast, colnames(pathway.stats))
		fold.changes <- get.significant.kegg.compounds(identification=compound.info, toptable=toptables[[i]], p.value.cutoff=0.05)
		sig.pathways <- which(pathway.stats[,contrast] > 0)
		urls <- generate.kegg.pathway.links(pathway.ids=pathway.stats$ID[sig.pathways], identified.compounds.by.pathway=identified.compounds.by.pathway, stds=compound.std.ids, fold.changes=fold.changes)
		#message("No. URLs ", length(urls), "\n")
		if(length(urls) > 0) {
			.setExternalURLs(workbook=workbook, sheet="Pathways", urls=urls, link.names=pathway.stats[sig.pathways,contrast], rows.idx=sig.pathways, column.idx=column.idx)
		}
	}
	gc(reset=TRUE)
}

.createPotentialSheet <- function(workbook=workbook(), raw.data=data.frame(), groups=list(), toptables=list(), identification=data.frame()) {
	
	potential <- data.frame()
	for(i in 1:length(toptables)) {
		contrast <- names(toptables)[i]
		members <- unlist(strsplit(names(toptables)[i], "-"))
		
		tt <- toptables[[i]]
		
		potential.ids <- rownames(tt)[which(is.na(tt$P.Value))]
		if(length(potential.ids) > 0) {
			potential.data <- raw.data[potential.ids, unlist(groups[members])]

			potential.idx <- apply(
				potential.data, 
				1, 
				function(x){
					.is.potential(x[unlist(groups[members[1]])]) || 
					.is.potential(x[unlist(groups[members[2]])])
				}
			)
			ID <- potential.ids[potential.idx]
			if(length(ID) > 0) {
				potential.data <- cbind(ID, raw.data[ID, c("Mass", "RT")])
				potential.data$Contrast <- contrast
				potential <- rbind(potential, potential.data)
			}
		}
	}

	if(nrow(potential) > 0) {
		sheet <- createSheet(workbook, name="Potentials")
		writeWorksheet(workbook,data=potential,sheet="Potentials", header=TRUE)
		setColumnWidth(workbook, sheet="Potentials", column=1:getLastColumn(workbook, "Potentials"))

		link.idx <- which(potential$ID %in% identification$id)
		if(length(link.idx) > 0) {
			formula <- paste('HYPERLINK("#Identification!A"&MATCH("', potential$ID[link.idx], '",Identification!A1:A', getLastRow(workbook, "Identification"),',0),"', potential$ID[link.idx], '")', sep="")
			setCellFormula(workbook, "Potentials", row=link.idx + 1, col=1, formula=formula)
			setCellStyle(workbook, sheet="Potentials", row=link.idx + 1, col=1, cellstyle=getCellStyle(workbook, name="Hyperlink"))	
			gc(reset=TRUE)
		}

		return(sheet)
	}
}

.is.potential <- function(group.data=numeric(), cutoff=2/3) {
	return( ( length(which(group.data > 0)) / length(group.data) ) >= cutoff )
}

.setExternalURLs <- function(workbook=workbook(), sheet=character(), urls=character(), link.names=character(), rows.idx=integer(), column.idx=integer()) {
	if(length(urls)!=length(link.names)) {
		stop("Different numbers of URLs and link names.")
	}
	if(length(urls)==0) {
		stop("No URLs given.")
	} 
	if(length(link.names)==0) {
		stop("No link names given.")
	}

	#calculate lengths of hyperlink formulae - max 255 char in excel
	formula.lengths <- nchar(get.excel.hyperlink("", "")) + nchar(urls) + nchar(link.names)
	shorten.idx <- which(formula.lengths >= 255)

	#shorten if >= 255
	if(length(shorten.idx) > 0) {
		short.urls <- sapply(urls[shorten.idx], shortenURL)
		urls[shorten.idx] <- short.urls
	}

	#remove NAs - don't provide a link for these
	na.urls <- which(is.na(urls))

	if(length(na.urls) > 0) {
	 	urls <- urls[-na.urls]
	 	rows.idx <- rows.idx[-na.urls]
	 	link.names <- link.names[-na.urls]
	}

	#generate links and set
	hyperlinks <- get.excel.hyperlink(urls, link.names)

	setCellFormula(workbook, sheet, row=rows.idx+1, col=column.idx, formula=hyperlinks)
	setCellStyle(workbook, sheet=sheet, row=rows.idx+1, col=column.idx, cellstyle=getCellStyle(workbook, name="Hyperlink"))
}

get.excel.hyperlink <- function(url, name) {
	if(is.numeric(name)) {
		return(sprintf('HYPERLINK("%s",%d)', url, name))
	}
	else {
		return(sprintf('HYPERLINK("%s","%s")', url, name))
	}
}

get.significant.kegg.compounds <- function(identification=data.frame(), toptable=data.frame(), p.value.cutoff=0.05) {
	#sig.metabolites.idx <- which(toptable$adj.P.Val < p.value.cutoff)
	# sig.up <- rownames(toptable)[which(toptable$logFC > 0 & toptable$adj.P.Val < p.value.cutoff)]
	# sig.down <- rownames(toptable)[which(toptable$logFC < 0 & toptable$adj.P.Val < p.value.cutoff)]
	
	# #kegg.identification <- identification[which(identification$DB=="kegg"),]
	# kegg.up <- as.character(identification$DBID)[which(identification$id %in% sig.up)]
	# kegg.down <- as.character(identification$DBID)[which(identification$id %in% sig.down)]
	# kegg.both <- intersect(kegg.up, kegg.down)
	sig.up <- sapply(fold.bins(), function(x){.get.significant(toptable=toptable, fold.change=x, identification=identification, method="up")}, simplify=FALSE)
	sig.down <- sapply(-fold.bins(), function(x){.get.significant(toptable=toptable, fold.change=x, identification=identification, method="down")}, simplify=FALSE)
	sig.both <- intersect(unique(unlist(sig.up)), unique(unlist(sig.down)))

	names(sig.up) <- fold.bins()
	names(sig.down) <- -fold.bins()


	return(list(up=sig.up, down=sig.down, both=sig.both))

	
	
}

.get.significant <- function(toptable=NULL, fold.change=numeric(), identification=data.frame(), p.value.cutoff=0.05, method=c("up", "down")) {
		sig.filter <- switch(
			method,
			up   = function(f,t,p){which(t$logFC > f & t$adj.P.Val < p)},
			down = function(f,t,p){which(t$logFC < f & t$adj.P.Val < p)}
		)
		sig <- rownames(toptable)[sig.filter(fold.change, toptable, p.value.cutoff)]
		sig.id <- as.character(identification$DBID)[which(identification$id %in% sig)]
		return(sig.id)
	}

.get.significant.kegg.compounds <- function(toptable=NULL, p.value.cutoff=0.05, method=c("up", "down")) {



}

generate.kegg.pathway.links <- function(pathway.ids=character(), identified.compounds.by.pathway=list(), stds=character(), fold.changes=list()) {
	if(length(pathway.ids) > 0) {
		urls <- sapply(pathway.ids, function(id) {
			compounds <- identified.compounds.by.pathway[[id]]
	 		markup <- generate.kegg.markup(compounds=compounds, stds=stds, fold.changes=fold.changes)
	 		url <- get.kegg.pathway.url(id, markup$compounds, markup$fg.col, markup$bg.col)
		})
		return(urls)
	}
}

generate.kegg.markup <- function(compounds=character(), stds=character(), fold.changes=list()) {
	##check all vectors same length
	##bg main color, fg border
	fg.col <- rep(Pimp.colours$annotated, length(compounds))
	bg.col <- rep(Pimp.colours$annotated, length(compounds))

	if(length(stds) > 0) {
		fg.col[compounds %in% stds] <- Pimp.colours$identified
		bg.col[compounds %in% stds] <- Pimp.colours$identified
	}

	if(length(fold.changes) > 0) {

		bg.col <- .set.fc.colours(compounds=compounds, markup=bg.col, fold.changes=fold.changes$up, colours=kegg.up.colours())
		bg.col <- .set.fc.colours(compounds=compounds, markup=bg.col, fold.changes=fold.changes$down, colours=kegg.down.colours())
		# bg.col[compounds %in% fold.changes$up] <- "red"
		# bg.col[compounds %in% fold.changes$down] <- "blue"
		bg.col[compounds %in% fold.changes$both] <- "purple"
	}
	#fg.col[fg.col=="pink"] <- ""%2332cd32 %236f9a4b
	#bg.col[bg.col=="pink"] <- ""
	return(list(compounds=compounds, fg.col=fg.col, bg.col=bg.col))
}
.set.fc.colours <- function(compounds=character(), markup=character(), fold.changes=numeric(), colours=character()) {
	if(length(fold.changes)!=length(colours)) {
		stop("Number of fold change bins does not match the number of colours.")
	}
	for(i in 1:length(fold.changes)) {
		markup[compounds %in% fold.changes[[i]]] <- colours[i]
	}
	return(markup)
}
