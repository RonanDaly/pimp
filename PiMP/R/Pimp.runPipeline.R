Pimp.runPipeline <- function(files=list(), groups=list(), comparisonNames=character(), contrasts=character(), standards=character(), databases=character(), normalization="none", nSlaves=0, reports=c("excel", "xml"), batch.correction=FALSE, verbose=TRUE, ...) {
	logger <- getPiMPLogger('Pimp.runPipeline')

	# options(java.parameters=paste("-Xmx",1024*8,"m",sep=""))
	# library(PiMP)

	##set java to headless mode - prevents MacOS barfing in spreadsheet generation
	.jcall("java/lang/System","S","setProperty","java.awt.headless","true")

	##
	## Initial checks ensuring all required information is present
	##

	#Set non-default parameters
	args <- list(...)
	analysis.id <- NULL
	if("analysis.id" %in% names(args)) {
		analysis.id <- args$analysis.id
	}

	#Check that all files exist
	if(any(!file.exists(unlist(files))))
		stop(cat("The following files were not found:", unlist(files)[which(!file.exists(unlist(files)))], sep="\n"))

	
	#Check all files have a corresponding file of the opposite polarity if both positive and negative files are present
	if(length(files$positive) > 0 && length(files$negative) > 0) {
		if(!all.equal(basename(files$positive), basename(files$negative))) {
			stop("Positive and Negative sample names do not match.")
		}
	}
	
	#Check all samples in groups have corresponding file
	file.samples <- sort(unique(file_path_sans_ext(basename(unlist(files)))))
	group.samples <- sort(as.character(unlist(groups)))
	
	files.not.in.groups <- setdiff(file.samples, group.samples)
	groups.not.in.files <- setdiff(group.samples, file.samples)

	if(length(files.not.in.groups)) {
		stop(paste("The following samples are found in files, but not in a group: ", paste(files.not.in.groups, collapse=", ")))
	}

	if(length(groups.not.in.files)) {
		stop(paste("The following samples are found in groups, but not found in files: ", paste(groups.not.in.files, collapse=", ")))
	}
	


	#Check contrasts information for the statistics calculations exist
	if(!all(unique(unlist(strsplit(contrasts, ","))) %in% names(groups))) {
		logerror('contrasts: %s', contrasts, logger=logger)
		logerror('groups: %s', groups, logger=logger)
		stop("Some contrast levels not found in groups.")
	}

	##if batch correcting check files are mzML.
	if(batch.correction) {
		message("Batch correction enabled. Checking file types.")
		if(!all(file_ext(unlist(files))=="mzML")) {
  			stop("Incorrect file type detected. mzML files required. Unable to batch correct.")
  		}
	}

	##create analysis directory
	if(!is.null(analysis.id)) {
		message(paste0("Setting analysis directory to: ", paste(mzmatch.outputs$analysis.folder, analysis.id, sep="_")))
		mzmatch.outputs <- lapply(mzmatch.outputs, function(x) {
								  sub(paste0("^", mzmatch.outputs$analysis.folder), 
								  	  paste0(mzmatch.outputs$analysis.folder, "_", analysis.id), x)
								}
							)
		#mzmatch.outputs$analysis.folder = paste(mzmatch.outputs$analysis.folder, analysis.id, sep="_")
	} 
	dir.create(mzmatch.outputs$analysis.folder)
	#print(mzmatch.params$ppm)

	#Generate STDs annotation XML file
	stds <- NULL
	if(length(standards) > 0 && 'standard' %in% databases) {
		stds  <- Pimp.stds.createAnnotationFile(files=standards, outfile=mzmatch.outputs$stds.xml.db)
	} else {
		mzmatch.outputs$stds.xml.db <- NULL
	}
	databases = databases[ ! databases == 'standard']

	
	##Get external annotation database info - using our own DBs rather than the out of data MzMatch ones which are out of date.
	DBS <- dir(system.file("dbs", package=getPackageName()), full.names=TRUE, pattern=paste(databases, ".*\\.xml$", sep="", collapse="|"), ignore.case=TRUE)
	
	if(length(DBS)!=length(databases)) {
		stop("Not all annotation databases found.")
	}


	##
	## Processing of raw data files
	##
	
	#Process mzXML files for each polarity
	if(length(files$positive) > 0) {
		raw.data.pos <- Pimp.processRawData(files=files$positive, groups=groups, databases=DBS, mzmatch.params=mzmatch.params, mzmatch.outputs=mzmatch.outputs, peakml.params=peakml.params, xcms.params=xcms.params, polarity="positive", batch.correction=batch.correction, nSlaves=nSlaves)
	}
	
	if(length(files$negative) > 0) {
		raw.data.neg <- Pimp.processRawData(files=files$negative, groups=groups, databases=DBS, mzmatch.params=mzmatch.params, mzmatch.outputs=mzmatch.outputs, peakml.params=peakml.params, xcms.params=xcms.params, polarity="negative", batch.correction=batch.correction, nSlaves=nSlaves)
	}

	
	#Data are returned in data.frame with checksum as peak id.  Row bind if two polarities
	if(exists("raw.data.pos") && exists("raw.data.neg")) {
		loginfo('Two polarities exist', logger=logger)

		logdebug('Positive rownames: %s', rownames(raw.data.pos), logger=logger)
		logdebug('Negative rownames: %s', rownames(raw.data.neg), logger=logger)
		if(length(intersect(rownames(raw.data.pos), rownames(raw.data.neg)))!=0) {
			stop(paste("None unique rownames across negative and positive metabolites."))
		}

		raw.data.pos.names = names(raw.data.pos)
		raw.data.neg.names = names(raw.data.neg)
		logdebug('Positive names: %s', raw.data.pos.names, logger=logger)
		logdebug('Negative names: %s', raw.data.neg.names, logger=logger)
		isEqualNames = all.equal(raw.data.pos.names, raw.data.neg.names)
		loginfo('isEqualNames: %s', isEqualNames, logger=logger)
		if(!isTRUE(isEqualNames)) {
			stop(paste("Columns for positive and negative data do not match."))
		}

		save(file="raw.data.pos.RData", raw.data.pos)
		save(file="raw.data.neg.RData", raw.data.neg)

		raw.data <- rbind(raw.data.pos, raw.data.neg) #check columns
	} else if(exists("raw.data.pos")) {
		save(file="raw.data.pos.RData", raw.data.pos)
		raw.data <- raw.data.pos
	} else if(exists("raw.data.neg")) {
		save(file="raw.data.neg.RData", raw.data.neg)
		raw.data <- raw.data.neg
	} else {
		stop("No Raw Data objects exist.")
	}


	##
	## Preparation of raw data for statistics
	##
	
	#Remove analysis samples from data for statistical analysis
	data.groups <- groups[!names(groups) %in% c("QC", "Blank", "Standard")]

	#Preprocess raw data for statistical analysis. Keep BP plus those matching to STD, set 0s to NA
	preprocessed <- .preProcessRawData(raw.data=raw.data, groups=data.groups)

	#Normalization if required. Default is "none"
	norm.data <- Pimp.normalize(preprocessed$data, method=normalization)

	#Log 2 transform data - required for parametric stats (normal distribution required), compariable up/down fold changes
	norm.data <- log2(norm.data)


	##
	## Statistics - PCA, Differential statistics, Pathways - Would be good to do Over/under represented pathways, but tricky unless just use those matched to standards
	##

	##differential analysis using ebayes
	diff.stats <- Pimp.statistics.differential(data=norm.data, groups=data.groups, contrasts=contrasts, method="ebayes", repblock=NULL)
	toptables <- lapply(1:ncol(diff.stats$contrasts), function(i){topTable(diff.stats, coef=i, genelist=data.frame(Mass=preprocessed$Mass, RT=preprocessed$RT), number=length(diff.stats$coef[,1]), confint=TRUE)})      #[,c("Mass", "RT", "logFC","P.Value","adj.P.Val")]
	names(toptables) <- comparisonNames

	#pca plot coloured by groups
	pca <- Pimp.statistics.pca(data=norm.data, groups=data.groups, file="pca.svg")

	##
	## Output
	##

	#ids 
	identification <- Pimp.report.generateIdentifications(raw.data=raw.data, databases=DBS, stds.db=mzmatch.outputs$stds.xml.db)

	#pathway stuff
	compound.ids <- unique(as.character(identification$DBID[which(identification$DB=="kegg")]))
	compound.std.ids <- unique(as.character(identification$DBID[which(identification$DB=="kegg" & identification$publishable=="Identified")]))
	compound.info <- identification[which(identification$DB=="kegg"),]

	if ( 'kegg' %in% databases ) {
		identified.compounds.by.pathway <- .get.identified.compounds.by.pathways(ids=compound.ids, compounds2Pathways=compounds2Pathways)
		pathway.stats <- Pimp.report.generatePathwayStatistics(pathways=pathways, compound.info=compound.info, compound.std.ids=compound.std.ids, identified.compounds.by.pathway=identified.compounds.by.pathway, toptables=toptables)
	} else {
		identified.compounds.by.pathway = list()
		pathway.stats = data.frame()
	}

	#excel
	if("excel" %in% reports) {
		Pimp.exportToExcel(databases=databases, stds.db=mzmatch.outputs$stds.xml.db, raw.data=raw.data, groups=data.groups, identification=identification, preprocessed=preprocessed, diff.stats=diff.stats, toptables=toptables, pathway.stats=pathway.stats, identified.compounds.by.pathway=identified.compounds.by.pathway, compound.ids=compound.ids, compound.std.ids=compound.std.ids, compound.info=compound.info)
	}

	message("XML Reports")

	if("xml" %in% reports) {
		if(!exists("db")) {
			warning("No database connection.  Unable to generate XML file.")			
		}
		else if(is.null(analysis.id)) {
			warning("No analysis ID.  Unable to generate XML file.")	
		}
		else {
			Pimp.exportToXML(id=analysis.id, raw.data=raw.data, identification=identification, toptables=toptables, pathway.stats=pathway.stats, identified.compounds.by.pathway=identified.compounds.by.pathway, db=db)
		}
	}
	
	#save analysis and session information
	sessionInfo <- sessionInfo()
	save(sessionInfo, file="sessionInfo.RData")
	save.image(paste0(mzmatch.outputs$analysis.folder, ".RData"))

}

.preProcessRawData <- function(raw.data=data.frame(), groups=list()) {

	##select only columns of samples of interest i.e. no QC, blanks, stds
	intensities.idx <- match(as.character(unlist(groups)), colnames(raw.data))
	
	#get rows containing basepeaks or match to standard
	basepeaks <- which(raw.data$relation.ship=="bp" | raw.data$relation.ship=="potential bp")
	stds <- which(!is.na(raw.data$stds_db_identification))

	data <- as.matrix(raw.data[unique(basepeaks,stds),intensities.idx]) #subset to produce data for statistical analysis
	# NB The gap filler must have fillAll=TRUE to make sure we aren't setting missing peaks to 1, i.e. the only
	# peaks that should be set to 1 are those that have levels too low to detect.
	data[data==0] <- 1.0 ##convert 0s to 1s
	data[is.na(data)] <- 1.0 ##convert NAs to 1s

	Mass <- raw.data[unique(basepeaks,stds),'Mass']
	RT <- raw.data[unique(basepeaks,stds),'RT']

	return(list(data=data, Mass=Mass, RT=RT))
}

Pimp.my.metabolome <- function(..., seconds=5, interval=0.5) {
	.welcome(interval, seconds)
	Pimp.runPipeline(...)
	.goodbye(interval, seconds)
}


