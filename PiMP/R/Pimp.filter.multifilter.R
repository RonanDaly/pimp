Pimp.filter.multifilter <- function(file=NULL, mzmatch.filters=list(), mzmatch.params=list(), mzmatch.outputs=list()) {
	#filters <- list(...)
	if(!file.exists(file)) stop(paste("File", file, "does not exist!"))

	filters <- mzmatch.filters[which(mzmatch.filters==TRUE)]

	if(filters$noise && is.numeric(mzmatch.params$noise))
	{
		mzmatch.ipeak.filter.NoiseFilter(i=file, o=mzmatch.outputs$final.combined.noise.filtered.file, v=T, codadw=mzmatch.params$noise, JHeapSize=4096)
		file <- mzmatch.outputs$final.combined.noise.filtered.file
	}
	
	filter.args <- names(formals(mzmatch.ipeak.filter.SimpleFilter))

	submitted.args <- grep(paste(names(filters), collapse="|"), filter.args, value=TRUE)
	values <- match(submitted.args, names(mzmatch.params))

	if(length(values)>0) {
		if(!any(is.na(values)) || !any(is.na(mzmatch.params[values]))) 
		{
			cat(paste("mzmatch.ipeak.filter.SimpleFilter(i=\"", file, "\",o=\"", mzmatch.outputs$final.combined.simple.filtered.file,"\",v=T, JHeapSize=4096,", paste(names(mzmatch.params[values]), mzmatch.params[values], sep="=", collapse=","), ")", sep=""))
			eval(parse(text=paste("mzmatch.ipeak.filter.SimpleFilter(i=\"", file, "\",o=\"", mzmatch.outputs$final.combined.simple.filtered.file,"\",v=T, JHeapSize=4096,", paste(names(mzmatch.params[values]), mzmatch.params[values], sep="=", collapse=","), ")", sep="")))
			file <- mzmatch.outputs$final.combined.simple.filtered.file
		} else {
			stop("Requested filter value missing.")
		}
	}

	if(!file.exists(file)) stop(paste(file, "does not exist"))

	return(file)
}