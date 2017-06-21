fixContrasts <- function(contrasts) {
    sapply(strsplit(contrasts, ','), FUN = function(x) paste(x[1], x[2], sep='-'))
}

makeContrastString <- function(contrast) {
  splitContrast = split(contrast$level, contrast$group)
  groups = as.numeric(names(splitContrast))
  contrastStrings = lapply(splitContrast, function(x) paste0('(', paste(x, collapse='+'), ')/', length(x)))
  if ( groups[1] > groups[2] ) {
    retval = paste0(contrastStrings[[1]], '-', contrastStrings[[2]])
  } else {
    retval = paste0(contrastStrings[[2]], '-', contrastStrings[[1]])
  }
  return(retval)
}


Pimp.statistics.differential <- function(data=matrix(), contrasts=NULL, method="ebayes", sample.metadata, repblock=NULL) {

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

      if( !isTRUE(all.equal(colnames(data), as.character(rownames(sample.metadata)))) )
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

removeColinearFactors <- function(factor.metadata, factorName) {
    logger <- getPiMPLogger('Pimp.statistics.differential.removeColinearFactors')

    otherFactors = setdiff(colnames(factor.metadata), factorName)
    colinearFactors = c()
    for ( f in otherFactors ) {
        md = factor.metadata[,c(factorName, f)]
        design = model.matrix(~.-1, data=md)
        if ( ncol(design) - rankMatrix(design) > 0 ) {
            logger$warn('%s is colinear with %s: removing %s from design matrix for %s comparison', f, factorName,
                factorName, f)
            colinearFactors = append(colinearFactors, f)
        }
    }
    goodFactors = setdiff(colnames(factor.metadata), colinearFactors)
    return(factor.metadata[,goodFactors,drop=FALSE])
}

makeContrastStringMultiFactorial <- function(contrast) {
  splitContrast = split(contrast$level, contrast$group)
  groups = as.numeric(names(splitContrast))
  factorName = as.character(unique(contrast$factor))
  contrastStrings = lapply(splitContrast, function(x) paste0('(', paste(factorName, x, collapse='+', sep=''), ')/', length(x)))
  if ( groups[1] > groups[2] ) {
    retval = paste0(contrastStrings[[1]], '-', contrastStrings[[2]])
  } else {
    retval = paste0(contrastStrings[[2]], '-', contrastStrings[[1]])
  }
  return(retval)
}

removeRedundantColumns <- function(m, contrastColumns, nonContrastColumns) {
    dif = ncol(m) - rankMatrix(m)
    j = 1
    while ( dif > 0 ) {
        ncc = nonContrastColumns[-j]
        mMinusColumn = m[,c(contrastColumns, ncc)]
        if ( ncol(mMinusColumn) - rankMatrix(mMinusColumn) < dif ) {
            m = mMinusColumn
            dif = ncol(mMinusColumn) - rankMatrix(mMinusColumn)
            nonContrastColumns = ncc
        } else {
            j = j + 1
        }
    }
    return(m)
}


Pimp.statistics.differential.MultiFactorial <- function(data=matrix(), contrasts=NULL, method="ebayes", sample.metadata, repblock=NULL) {

    method <- match.arg(method)

    if(!is.numeric(data))
        stop("data object not in correct format.")

    retval = list()

    factor.metadata = sample.metadata[,as.character(unique(contrasts$factor))]

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

      if( !isTRUE(all.equal(colnames(data), as.character(rownames(sample.metadata)))) )
        stop("Sample order in data and groups.matrix objects do not match.")
      if(method=="ebayes") {
          #combined.classvector <- sample.metadata[,factorName]
          #design <- model.matrix(~0+combined.classvector)
          #colnames(design) <- levels(combined.classvector)
          reducedMetadata = removeColinearFactors(factor.metadata, factorName)
          design = model.matrix(~.-1, data=reducedMetadata, contrasts.arg=lapply(reducedMetadata, contrasts, contrasts=FALSE))
          contrastColumns = paste(as.character(contrast$factor), as.character(contrast$level), sep='')
          factorNonContrastColumns = setdiff(paste(as.character(contrast$factor), as.character(unique(factor.metadata[,factorName])), sep=''), contrastColumns)
          designReduced = design[,factorNonContrastColumns != colnames(design)]

          nonContrastColumns = colnames(designReduced)[(!(colnames(designReduced) %in% contrastColumns))]
          designReReduced = removeRedundantColumns(designReduced, contrastColumns, nonContrastColumns)



        contrast.matrix <- makeContrasts(contrasts=makeContrastStringMultiFactorial(contrast), levels=designReReduced)


        #for (cc in contrastColumns) {
        #	duplicateColumns = which(sapply(colnames(design),function(x) cc != x && identical(design[,x], design[,cc])))
        #	design = design[,!(colnames(design) %in% names(duplicateColumns)),drop=FALSE]
        #	contrast.matrix = contrast.matrix[!(row.names(contrast.matrix) %in% names(duplicateColumns)),,drop=FALSE]
        #}

        if(!is.null(repblock)) {
          dupcor <- duplicateCorrelation(data, design=design, block=repblock)
          fit <- lmFit(data, design=design, block=repblock, correlation=dupcor$cons)
        } else {
          fit <- lmFit(data, design=designReReduced)
        }

        fit <- contrasts.fit(fit, contrast.matrix)
        fit <- eBayes(fit)
        retval[[as.character(comparison)]] = fit
     }
    }
    return(retval)
}



