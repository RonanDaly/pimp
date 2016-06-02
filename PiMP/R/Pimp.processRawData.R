Pimp.processRawData <- function(files=character(), groups=list(), databases=character(), xcms.params=list(), peakml.params=list(), mzmatch.params=list(), mzmatch.outputs=list(), polarity=c("positive", "negative"), verbose=TRUE, nSlaves=0, batch.correction=FALSE) {
	logger <- getPiMPLogger('Pimp.processRawData')
	loginfo('files: %s', files, logger=logger)
	loginfo('groups: %s', groups, logger=logger)
	loginfo('mzmatch.outputs: %s', mzmatch.outputs, logger=logger)
	##
	## Initial checks ensuring all required information is present
	##

	#Check that all files exist
	if(any(!file.exists(files)))
		stop(cat("The following files were not found:", files[which(!file.exists(files))], sep="\n"))

	#Check whether standards XML files exists - warn if not
	if(is.null(mzmatch.outputs$stds.xml.db) || !file.exists(mzmatch.outputs$stds.xml.db))
		warning("No standards database found.  Identification using retention times can not be done.")

	#Check whether external XML annotation files exist - warn if not
	if(length(databases) < 1)
		warning("No external databases found. No external identification will be done")

	
	##Get mzXML files parent directory.  Modify output file names for this polarity.
	#parent.dir <- unique(dirname(files))
	#if(length(parent.dir) > 1)
	#	stop("Sample files in multiple directories.")	

	#stds.xml.db.idx <- match("stds.xml.db", names(mzmatch.outputs))
	#mzmatch.outputs[-stds.xml.db.idx] <- lapply(mzmatch.outputs[-stds.xml.db.idx], function(x){file.path(parent.dir, x)})
	mzmatch.outputs <- lapply(mzmatch.outputs, sprintf, polarity)
	loginfo('mzmatch.outputs: %s', mzmatch.outputs, logger=logger)
	dir.create.ifNotExist(mzmatch.outputs$polarity.folder)
	##
	## Process mzXML files
	##
	
	#Generate xcmsSet
	if(verbose){ message("Generating xcmsSet.") }

	xset <- xcmsSet(files, 
		method=xcms.params$method, ppm=xcms.params$ppm, peakwidth=xcms.params$peakwidth, 
		snthresh=xcms.params$snthresh, prefilter=xcms.params$prefilter, integrate=xcms.params$integrate, 
		mzdiff=xcms.params$mzdiff, verbose.columns=xcms.params$verbose.columns, fitgauss=xcms.params$fitgauss, nSlaves=nSlaves
	)

	#Correct Retention Times and write out individual PeakML files.
	if(verbose) { message("Correcting retention times.") }
	
	peakml.files <- Pimp.rtcorrect(xset=xset, method=mzmatch.params$rt.alignment, peakml.params=peakml.params, mzmatch.outputs=mzmatch.outputs, nSlaves=nSlaves)	
	loginfo('peakml.files: %s', peakml.files, logger=logger)
	
	#Combine files by group, RSD filter if required (Not convinced we should be using this filter) and combine group files
	#combined directory
	combined.dir <- ifelse(mzmatch.params$rt.alignment != "none", mzmatch.outputs$alignment.folder, mzmatch.outputs$combined.folder) #"combined_rt.alignment", "combined"
	loginfo('combined.dir: %s', combined.dir, logger=logger)
	if(verbose) { message("Combined directory ", combined.dir) }
	
	#combine and RSD
	final.combined.peakml <- Pimp.combine.peakml(files=peakml.files, combined.dir=combined.dir, groups=groups, mzmatch.filters=mzmatch.filters, mzmatch.outputs=mzmatch.outputs, nSlaves=nSlaves)
	loginfo('final.combined.peakml: %s', final.combined.peakml, logger=logger)
	if(verbose) { message("Final combined file", final.combined.peakml) }


	#Filter data (Noise, minintensity, mindetections by default).  Should probably move this to R.
	#Uses "soft" filters. i.e. for minintensity as long as one sample is above threshold function keeps everything.
	filtered.file <- Pimp.filter.multifilter(file=final.combined.peakml, mzmatch.filters=mzmatch.filters, mzmatch.params=mzmatch.params, mzmatch.outputs=mzmatch.outputs)

	
	#Gapfilling
	PeakML.GapFiller(
		filename=filtered.file, 
		ionisation=peakml.params$ionisation,
		Rawpath=NULL, 
		outputfile=mzmatch.outputs$final.combined.gapfilled.file, 
		ppm=peakml.params$ppm, 
		rtwin=peakml.params$rtwin,nSlaves=0,
		fillAll=TRUE
  	)

	#Stop if gapfilling has barfed
  	if(!file.exists(mzmatch.outputs$final.combined.gapfilled.file))
  		stop(paste("Gapfilled file", mzmatch.outputs$final.combined.gapfilled.file, "does not exist!"))


  	#######Implementation of Ronan's batch correction code.
  	if(batch.correction) {
  		message("Batch Correcting.")
  		if(!all(file_ext(files)=="mzML")) {
  			stop("Incorrect file type detected. mzML files required. Unable to batch correct.")
  		}

  		corrected.file <- sub("gapfilled", "gapfilled_corrected", mzmatch.outputs$final.combined.gapfilled.file)
  		samplesToKeep <- names(groups[!names(groups) %in% "Blank"])
  		message(paste(mzmatch.outputs$final.combined.gapfilled.file, corrected.file, samplesToKeep))
  		batchCorrect(groups, files, mzmatch.outputs$final.combined.gapfilled.file, corrected.file, samplesToKeep)

  		if(!file.exists(corrected.file)) {
  			stop(paste("Batch corrected file", corrected.file, "does not exist!"))
  		}

  		mzmatch.outputs$final.combined.gapfilled.file <- corrected.file
  	}

  	##Sort related peaks
	mzmatch.ipeak.sort.RelatedPeaks(i=mzmatch.outputs$final.combined.gapfilled.file, v=T,o=mzmatch.outputs$final.combined.related.file,basepeaks=mzmatch.outputs$final.combined.basepeaks.file,ppm=mzmatch.params$ppm, rtwindow=mzmatch.params$rtwindow)

	#No return value from MZMatch functions. Stop if related peaks has barfed
	if(!file.exists(mzmatch.outputs$final.combined.related.file))
  		stop(paste("Related peaks file", mzmatch.outputs$final.combined.related.file, "does not exist!"))

  	#No return value from MZMatch functions. Identify peaks using defined external annotation DBs and STDSot

  	data <- Pimp.identify.metabolites(databases=databases, groups=groups, mzmatch.outputs=mzmatch.outputs, mzmatch.params=mzmatch.params, polarity=polarity)

  	return(data)

}

getStartTimeStamp <- function(file) {
	doc <- xmlTreeParse(file)
	top <- xmlRoot(doc)
 	return(xmlAttrs(top[['mzML']][['run']])[["startTimeStamp"]])
}
