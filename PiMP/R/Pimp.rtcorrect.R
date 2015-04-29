Pimp.rtcorrect <- function(xset=xcmsSet(), method=c("obiwarp", "loess", "none"), peakml.params=list(), mzmatch.outputs=list(), nSlaves=0, verbose=TRUE) {

	##RT Correct using xcms alignment algorithm.
	xset.aln <- switch(
		method,
		obiwarp = .obiwarp(xset=xset),
		loess 	= .loess(xset=xset), 
		none = xset
	)

	#Split xcms set into multiple sets, 1 per sample.
	xseto <- split(xset.aln, filepaths(xset.aln))

	#Set up cluster for parallel processing
	if(nSlaves > 1) {
		cl <- makeCluster(nSlaves, outfile="errors.txt")
		registerDoParallel(cl)
	}
	else {
		registerDoSEQ()
	}

	#Create new output file names
	#peakml.files <- sub("\\.mzxml", "\\.peakml", basename(filepaths(xset.aln)), ignore.case=TRUE)
	#peakml.files <- file.path(mzmatch.outputs$polarity.folder, sub("\\.mzxml", "\\.peakml", basename(filepaths(xset.aln)), ignore.case=TRUE))
	peakml.files <- file.path(mzmatch.outputs$polarity.folder, sub("\\.mzxml|\\.mzml|\\.mzdata", "\\.peakml", basename(names(xseto)), ignore.case=TRUE))
	cat(peakml.files)
	#Need to get specified Java heapsize here. Barfs if called by function within foreach loop
	heapsize <- getJavaHeapSize()

	foreach(i=1:length(peakml.files), .packages=c("PiMP", "mzmatch.R", "rJava"), .export=c("xseto", "peakml.files", "peakml.params", "heapsize"), .combine='c') %dopar% {
		mzmatch.init(memorysize=heapsize, version.1=FALSE)

		#Write out PeakML file
		PeakML.xcms.write.SingleInstance(xset = xseto[[i]], 
                  outputfile = peakml.files[i], ionisation = peakml.params$ionisation, 
                  addscans = peakml.params$addscans, writeRejected = peakml.params$writeRejected, 
                  ApodisationFilter = peakml.params$ApodisationFilter, ppm=5)
	}

	#Stop parallel cluster
	if(nSlaves > 1) {
		stopCluster(cl)
	}

	if(any(!file.exists(peakml.files))) {
		stop("Some files not created.")
	}

	return(peakml.files)
}

## Alignment algorithm functions

.obiwarp <- function(xset=NULL) {
	xset.aln<-retcor(xset, method="obiwarp",profStep=0.01)
}

.loess <- function(xset=NULL) {
	xset.aln<-retcor(xset, method="loess",family="symmetric")
}