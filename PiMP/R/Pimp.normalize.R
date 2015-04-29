Pimp.normalize <- function(data=matrix(), method=c("quantile", "none")) {
	#match normalisation type
	method <- match.arg(method)

	#normalise - add other options e.g. loess etc.
	norm.data <- switch(
		method,
		quantile = normalizeQuantiles(data),
		none = data
	)

	colnames(norm.data) <- colnames(data)
	rownames(norm.data) <- rownames(data)

	return(norm.data)
}