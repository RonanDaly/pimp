fixContrasts <- function(contrasts) {
	sapply(strsplit(contrasts, ','), FUN = function(x) paste(x[1], x[2], sep='-'))
}


Pimp.statistics.differential <- function(data=matrix(), groups=list(), contrasts=NULL, method="ebayes", repblock=NULL) {

	method <- match.arg(method)

	if(!is.numeric(data))
		stop("data object not in correct format.")

	#convert group list to matrix
	groups.matrix <- as.data.frame(cbind(unlist(groups), rep(names(groups), times=sapply(groups,length))))
	colnames(groups.matrix) <- c("samples", "groups")

	#check order data matches order group.matrix
	if(!all.equal(sort(colnames(data)), sort(as.character(groups.matrix$samples))))
		stop("Sample order in data and groups.matrix objects do not match.")

	if(method=="ebayes") {
		combined.classvector <- as.factor(groups.matrix$groups)
		design <- model.matrix(~0+combined.classvector)
		colnames(design) <- levels(combined.classvector)
		contrast.matrix <- makeContrasts(contrasts=fixContrasts(contrasts), levels=design)

		if(!is.null(repblock)) {
      		dupcor <- duplicateCorrelation(data, design=design, block=repblock)
      		fit <- lmFit(data, design=design, block=repblock, correlation=dupcor$cons)
    	} else {
      		fit <-lmFit(data, design)
    	}

		fit <- contrasts.fit(fit, contrast.matrix)
		fit <- eBayes(fit)
	}
	# else if(method=="t-test") {
	# 	levels <- strsplit(contrasts, "-")

	# 	lapply(levels, function(x) {
	# 		group1.idx <- which(groups.matrix$groups==x[1])
	# 		group2.idx <- which(groups.matrix$groups==x[2])

	# 		p.values <- apply(data, 1, function(y) {
	# 			t.test(y[group1.idx], y[group2.idx], "two.sided")$p.value
	# 			fold.change <- mean(y[group1.idx], na.rm=TRUE) - mean(y[group2.idx], na.rm=TRUE)
	# 		})

	# 		adj.p.values <-  p.adjust(p.values, method="BH")

			

	# 	})
	# }

	return(fit)
}