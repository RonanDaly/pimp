.welcome <- function(interval, seconds) {
	flashes <- as.integer(seconds / interval + 1)
	for(i in 1:flashes) {
		if(i%%2) {
			cat("\r", sprintf("%60s", paste("Welcome! Pimping your metabolome in", floor(interval*(flashes-i)), "seconds")))	
		}
		else {
			cat("\r", sprintf("%60s", ""))
		}
		flush.console() 
		Sys.sleep(interval)
	}
	cat("\r", sprintf("%60s", ""), "\n")
}

.goodbye <- function(interval, seconds) {
	flashes <- as.integer(seconds / interval + 1)
	for(i in 1:flashes) {
		if(i%%2) {
			cat("\r", sprintf("%60s", paste(" You've been Pimped. Goodbye! ")))	
		}
		else {
			cat("\r", sprintf("%60s", ""))
		}
		flush.console() 
		Sys.sleep(interval)
	}
	cat("\r", sprintf("%60s", ""), "\n")
}

getJavaHeapSize <- function(default=2048) {
	java.params <- getOption("java.parameters")

	if(!is.null(java.params)) {
		java.params <- as.character(unlist(strsplit(java.params, " ")))
		
		heapsize.idx <- grep("-Xmx", as.character(unlist(strsplit(java.params, " "))))
		if(length(heapsize.idx) > 0) {
			heapsize <- gsub("\\D", "", java.params[heapsize.idx])
			return(heapsize)
		}
		else {
			return(default)
		}
	}
	else {
		return(default)
	}	
}

dir.create.ifNotExist = function(path, showWarnings = TRUE, recursive = FALSE, mode = "0777") {
  ifelse(!dir.exists(path), dir.create(path, showWarnings, recursive, mode), FALSE)
}

initialisePiMPLogging = function() {
	print('Initialising PiMP logging')
	if ( is.na(Sys.getenv('PIMP_LOG_LEVEL', unset=NA)) ) {
		Sys.setenv(PIMP_LOG_LEVEL='WARNING')
	}
	logLevel = Sys.getenv('PIMP_LOG_LEVEL')
	print(paste('PiMP log level set to', logLevel))
	if ( is.na(Sys.getenv('PUMP_LOG_LEVEL', unset=NA)) ) {
		Sys.setenv(PUMP_LOG_LEVEL=logLevel)
	}
	logging::logReset()
	logging::basicConfig(logLevel)
	logger <- getPiMPLogger('Pimp.extra.initialisePiMPLogging')
	handler = getHandler('basic.stdout')
	handler$formatter = function (record) {
	    text <- paste(record$levelname, record$timestamp, record$logger, '0', '0', '|', record$msg)
	}
	logerror('Logging at ERROR level', logger=logger)
	logwarn('Logging at WARNING level', logger=logger)
	loginfo('Logging at INFO level', logger=logger)
	logdebug('Logging at DEBUG level', logger=logger)
	logfine('Logging at FINE level', logger=logger)
	logfiner('Logging at FINER level', logger=logger)
	logfinest('Logging at FINEST level', logger=logger)
}

getPiMPLogger = function(name) {
	logLevel = Sys.getenv('PIMP_LOG_LEVEL', unset='WARNING')
	return(getLogger(name, level=logging::loglevels[logLevel]))
}

# This method will only work correctly in a single threaded process. If for some reason,
# multiple analyses are done in a single process, the logging setup will need to be changed.
setPiMPLoggerAnalysisID = function(analysis.id) {
	logger <- getPiMPLogger('Pimp.extra.setPiMPLoggerAnalysisID')
	loginfo('Setting analysis ID in logger to %s', analysis.id, logger=logger)
	handler = getHandler('basic.stdout')
	handler$formatter = function (record) {
	    text <- paste(record$levelname, record$timestamp, record$logger, '0', '0', analysis.id, '|', record$msg)
	}
	loginfo('Analysis id set', logger=logger)
}

getDefaultSettings = function() {
  mzmatch.filters = list(rsd=TRUE, iqr=FALSE, noise=TRUE, n=FALSE, offset=FALSE,
                         mindetections=TRUE, minscanid=FALSE, maxscanid=FALSE,
                         mintetentiontime=FALSE, maxretentiontime=FALSE,
                         minmass=FALSE, maxmass=FALSE, minintensity=TRUE, maxintensity=FALSE)
  
  mzmatch.params = list(rsd=0.5, iqr=0.5, rt.alignment='obiwarp', noise=0.8, ppm=2,
                        order=3, maxrt=120, rtwindow=30, id.rtwindow=0.05,
                        combination='set', mindetections=4, minintensity=5000,
                        adducts.positive='M+H,M+ACN+Na,M+Na,M+K,M+ACN+H',
                        adducts.negative='M-H,M-ACN+Na,M-Na,M-K,M-ACN+H')
  
  mzmatch.outputs = list(alignment.folder="analysis/%s/combined_rt.alignment",
                         combined.folder="analysis/%s/combined",
                         combined.rsd.filtered.folder="analysis/%s/combined_RSD_filtered",
                         combined.rsd.rejected.folder="analysis/%s/combined_RSD_rejected",
                         final.combined.peakml.file="analysis/%s/final_combined.peakml",
                         final.combined.noise.filtered.file="analysis/%s/final_combined_nf.peakml",
                         final.combined.simple.filtered.file="analysis/%s/final.combined_sf.peakml",
                         final.combined.gapfilled.file="analysis/%s/final_combined_gapfilled.peakml",
                         final.combined.related.file="analysis/%s/final_combined_related.peakml",
                         final.combined.basepeaks.file="analysis/%s/final_combined_basepeaks.peakml",
                         final.combined.related.id.file="analysis/%s/final_combined_related_identified.peakml",
                         final.combined.related.stds.id.file="analysis/%s/final_combined_related_stds_identified.peakml",
                         final.combined.basepeaks.id.file="analysis/%s/final_combined_basepeaks_identified.peakml",
                         final.combined.related.id.txt="analysis/%s/mzmatch_output.txt",
                         final.combined.related.stds.id.txt="analysis/%s/mzmatch_output_stds.txt",
                         stds.xml.db="analysis/stds_db.xml",
                         analysis.folder="analysis",
                         polarity.folder="analysis/%s")
  
  xcms.params = list(method='centWave', ppm=3, peakwidth=c(5,100), snthresh=2,
                     prefilter=c(2,500), integrate=1, mzdiff=0.001,
                     verbose.columns=TRUE, fitgauss=FALSE)
  
  peakml.params = list(ionisation='detect', addscans=2, writeRejected=FALSE,
                       ApodisationFilter=TRUE, ppm=0, rtwin=0)
  return(list(mzmatch.filters=mzmatch.filters, mzmatch.params=mzmatch.params, mzmatch.outputs=mzmatch.outputs,
              xcms.params=xcms.params, peakml.params=peakml.params))
}

createError <- function() {
        return(createError2())
}

createError2 <- function() {
        stop('throwing from createError2')
}
