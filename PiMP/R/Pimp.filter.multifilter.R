Pimp.noiseFilter <- function(in_file, out_file, noise) {
    mzmatch.ipeak.filter.NoiseFilter(i=in_file, o=out_file, v=TRUE, codadw=noise)
}

Pimp.simpleFilter <- function(in_file, out_file, ppm, minintensity, mindetections) {
    mzmatch.ipeak.filter.SimpleFilter(i=in_file, o=out_file, v=TRUE,
        ppm=ppm, minintensity=minintensity, mindetections=mindetections)
}

Pimp.filter.multifilter <- function(file=NULL, mzmatch.filters=list(), mzmatch.params=list(), mzmatch.outputs=list()) {
    #filters <- list(...)
    if(!file.exists(file)) stop(paste("File", file, "does not exist!"))

    filters <- mzmatch.filters[which(mzmatch.filters==TRUE)]

    if(filters$noise && is.numeric(mzmatch.params$noise))
    {
        mzmatch.ipeak.filter.NoiseFilter(i=file, o=mzmatch.outputs$final.combined.noise.filtered.file, v=TRUE, codadw=mzmatch.params$noise)
        file <- mzmatch.outputs$final.combined.noise.filtered.file
    }

    filter.args <- names(formals(mzmatch.ipeak.filter.SimpleFilter))

    submitted.args <- grep(paste(names(filters), collapse="|"), filter.args, value=TRUE)
    values <- match(submitted.args, names(mzmatch.params))

    if(length(values)>0) {
        if(!any(is.na(values)) || !any(is.na(mzmatch.params[values])))
        {
            cat(paste("mzmatch.ipeak.filter.SimpleFilter(i=\"", file, "\",o=\"", mzmatch.outputs$final.combined.simple.filtered.file,"\",v=TRUE,", paste(names(mzmatch.params[values]), mzmatch.params[values], sep="=", collapse=","), ")", sep=""))
            eval(parse(text=paste("mzmatch.ipeak.filter.SimpleFilter(i=\"", file, "\",o=\"", mzmatch.outputs$final.combined.simple.filtered.file,"\",v=TRUE,", paste(names(mzmatch.params[values]), mzmatch.params[values], sep="=", collapse=","), ")", sep="")))
            file <- mzmatch.outputs$final.combined.simple.filtered.file
        } else {
            stop("Requested filter value missing.")
        }
    }

    if(!file.exists(file)) stop(paste(file, "does not exist"))

    return(file)
}