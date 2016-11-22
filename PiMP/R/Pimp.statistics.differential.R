fixContrasts <- function(contrasts) {
	sapply(strsplit(contrasts, ','), FUN = function(x) paste(x[1], x[2], sep='-'))
}

makeContrastString <- function(contrast) {
  splitContrast = split(contrast$level, contrast$group)
  groups = as.numeric(names(splitContrast))
  contrastStrings = lapply(splitContrast, function(x) paste0('(', paste(x, collapse='+'), ')/', length(x)))
  if ( groups[1] < groups[2] ) {
    retval = paste0(contrastStrings[[1]], '-', contrastStrings[[2]])
  } else {
    retval = paste0(contrastStrings[[2]], '-', contrastStrings[[1]])
  }
  return(retval)
}


Pimp.statistics.differential <- function(data=matrix(), contrasts=NULL, method="ebayes", repblock=NULL) {

	method <- match.arg(method)

	if(!is.numeric(data))
		stop("data object not in correct format.")
	
	retval = list()
	
	# For each comparison in the contrasts table
	comparisons = unique(contrasts$comparison)
	for ( i in 1:length(comparisons) ) {
	  comparison = comparisons[i]
	  # Get the contrast of interest
	  contrast = contrasts[contrasts$comparison == comparison,]
	  # Make sure we only have one factor at a time and two groups at a time
	  factorName = as.character(unique(contrast$factor))
	  stopifnot( length(factorName) == 1 )
	  stopifnot( length(unique(contrast$group)) == 2 )
	  
	  if( !all.equal(colnames(data), as.character(rownames(sample.metadata))) )
	    stop("Sample order in data and groups.matrix objects do not match.")
	  if(method=="ebayes") {
	      combined.classvector <- sample.metadata[,factorName]
	      design <- model.matrix(~0+combined.classvector)
	      colnames(design) <- levels(combined.classvector)
  	    contrast.matrix <- makeContrasts(contrasts=makeContrastString(contrast), levels=design)
  	    
  	    if(!is.null(repblock)) {
  	      dupcor <- duplicateCorrelation(data, design=design, block=repblock)
  	      fit <- lmFit(data, design=design, block=repblock, correlation=dupcor$cons)
  	    } else {
  	      fit <-lmFit(data, design)
  	    }
  	    
  	    fit <- contrasts.fit(fit, contrast.matrix)
  	    fit <- eBayes(fit)
  	    retval[[as.character(comparison)]] = fit
  	 }
	}
	return(retval)
}
