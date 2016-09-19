Pimp.combineSingle <- function(in_files, out_file, label, ppm, rtwindow, combination) {
	logger <- getPiMPLogger('Pimp.combineSingle')
    mzmatch.ipeak.Combine(
		i=paste(in_files,collapse=","),
		o=out_file,
		v=TRUE,
		label=label,
		ppm=ppm,
		rtwindow=rtwindow,
		combination=combination
    )
}

Pimp.rsdSingle <- function(in_file, out_file, rej_file, rsd) {
	logger <- getPiMPLogger('Pimp.rsdSingle')
	mzmatch.ipeak.filter.RSDFilter(
      i = in_file,
      o = out_file,
      rejected = rej_file,
      rsd = rsd,
      h = NULL,
      v = TRUE
    )
}

Pimp.combine.peakml <- function(files=character(), groups=list(), combined.dir=NULL, mzmatch.filters=list(), mzmatch.outputs=list(), mzmatch.params=list(), nSlaves=0) {

	#Create RSD directories if required
	if(mzmatch.filters$rsd)	{
		dir.create.ifNotExist(mzmatch.outputs$combined.rsd.filtered.folder)
		dir.create.ifNotExist(mzmatch.outputs$combined.rsd.rejected.folder)
    }

    dir.create.ifNotExist(combined.dir)

    if(nSlaves > 1) {
		cl <- makeCluster(nSlaves, outfile="")
		registerDoParallel(cl)
	}
	else {
		registerDoSEQ()
	}

	heapsize <- getJavaHeapSize()

	#	grouped.peakml.files <- foreach(group=names(groups), .packages="mzmatch.R", .export=c(".combinePeakmlFiles", ".mzmatch.ipeak.filter.RSDFilter", "mzmatch.ipeak.Combine", "files", "mzmatch.params", "mzmatch.init", "mzmatch.filters", "heapsize"), .combine='c', .verbose=TRUE) %dopar%
	grouped.peakml.files <- foreach(group=names(groups), .packages="mzmatch.R", .combine='c') %dopar%
	{
		logger <- getPiMPLogger('Pimp.combine.peakml.grouped.peakml.files')

		mzmatch.init(version.1=FALSE)
		##get peakml files by group
		group.files.idx <- which(basename(files) %in% paste0(groups[[group]], ".peakml"))
		group.files <- files[group.files.idx]
 		#group.files <- grep(pattern=paste(groups[[group]], "\\.peakml", sep="", collapse="|"), files, value=TRUE)

 		##created folder for combined files
 		# group.dir <- file.path(combined.dir, group)

 		# if(getOption("verbose"))
 		# 	cat(paste("Creating directory:", group.dir, "\n"))

 		# dir.create(group.dir, recursive=TRUE)

		combined.file <- file.path(combined.dir, paste(group, ".peakml", sep=""))
		loginfo('Group %s', group, logger=logger)
		combined.group.file <- .combinePeakmlFiles(files=group.files, outfile=combined.file, label=group, mzmatch.params=mzmatch.params)

		##RSD filter if required
		if(mzmatch.filters$rsd) #change in params
		{
	    	filtered.file <- file.path(mzmatch.outputs$combined.rsd.filtered.folder, basename(combined.file))
    		rejected.file <- file.path(mzmatch.outputs$combined.rsd.rejected.folder, basename(combined.file))
    		loginfo('Groupa %s', group, logger=logger)
    		.mzmatch.ipeak.filter.RSDFilter(i=combined.group.file, o=filtered.file, rejected=rejected.file, rsd=mzmatch.params$rsd, v=TRUE, JHeapSize=heapsize)
    		#check file exists
    		if(!file.exists(filtered.file)) stop(paste(filtered.file, "does not exist!\n"))
    	}

    	##set working file depending on RSD filter status
    	grouped.file <- ifelse(mzmatch.filters$rsd, filtered.file, combined.group.file)
	}

	if(nSlaves > 1) {
		stopCluster(cl)
	}

	if(length(grouped.peakml.files) > 1) {
		##test whether peaksets in file have peaks.  If not remove.  Samples included as zero when data read in.  Workaround for PeakML.Read.
		valid <- validatePeaksets(files=grouped.peakml.files)
		if ( !all(valid) ) {
			logwarn("Some files have no peaks. They will be discarded. This will probably cause errors later when combining across modes", logger=logger)
			logwarn("Files are %s", grouped.peakml.files[!valid], logger=logger)
		}
		loginfo("VALID %s", valid, logger=logger)
		return(.combinePeakmlFiles(files=grouped.peakml.files[valid], outfile=mzmatch.outputs$final.combined.peakml.file, mzmatch.params=mzmatch.params, heapsize=heapsize))
	}
	else {
		file.copy(grouped.peakml.files, mzmatch.outputs$final.combined.peakml.file)
		return(mzmatch.outputs$final.combined.peakml.file)
	}

}

.combinePeakmlFiles <- function(files=NULL, outfile=NULL, label=NULL, mzmatch.params=list(), heapsize=2048, verbose=TRUE) {
	logger <- getPiMPLogger('Pimp.combine.peakml.combinePeakmlFiles')
	if(length(files) == 0) stop("No data files specified.")
	if(any(!file.exists(files))) stop(cat("The following files were not found:", files[which(!file.exists(files))], sep="\n"))

	if(verbose)
	{
		loginfo("Files to be combined: %s", files, logger=logger)
	}

    mzmatch.ipeak.Combine(
		i=paste(files,collapse=","),
		v=TRUE,
		rtwindow=mzmatch.params$rtwindow, #rt.mins.to.secs(mzmatch.defaults$RTw), #check in secs
		o=outfile,
		combination=mzmatch.params$combination,
		ppm=mzmatch.params$ppm,
		label=label
    )

    if(!file.exists(outfile)) stop(paste("ERROR:", outfile, "does not exist!", sep=" "))

	return(outfile)
}

.mzmatch.ipeak.filter.RSDFilter <- function (JHeapSize = 2048, i = NULL, o = NULL, rejected = NULL,
    rsd = NULL, h = NULL, v = NULL)  {
  mzmatch.ipeak.filter.RSDFilter(
    i = i,
    o = o,
    rejected = rejected,
    rsd = rsd,
    h = h,
    v = v

  )
}

validatePeaksets <- function(files=NULL) {
	return(sapply(files, function(x){.getNumberPeaksets(x) > 0}))
}

.getNumberPeaksets <- function(file=NULL) {
	PeakMLtree <- xmlInternalTreeParse(file)
	nrPeakSets <- as.numeric(sapply(getNodeSet(PeakMLtree, "/peakml/header/nrpeaks"), xmlValue))
	return(nrPeakSets)
}