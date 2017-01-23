Pimp.identify.metabolites <- function(in_file=character(), databases=character(), groups=list(), mzmatch.outputs=list(), mzmatch.params=list(), polarity=character()) {

	#check file exists - which file?
	#check databases exist - warn
	#check stds exist

	data <- NULL
	#required annotation columns
  	annot <- "identification,ppm,adduct,relation.id,relation.ship,codadw,charge"

  	if(length(databases) > 0) {
	  	for(d in 1:length(databases)) {

	  		db.df <- Pimp.identify.metabolites.by.db(file=mzmatch.outputs$final.combined.related.file,
	  			database=databases[d],
	  			groups=groups,
	  			annot=annot,
	  			adducts=mzmatch.params[[paste("adducts", polarity, sep=".")]],
	  			ppm=mzmatch.params$ppm,
	  			mzmatch.outputs=mzmatch.outputs)

			data <- .merge.data.frames(df1=data, df2=db.df, database=databases[d])
	   	}
	}

   	if(!is.null(mzmatch.outputs$stds.xml.db)) {
		parent.ion <- switch(polarity, positive = "M+H", negative = "M-H")
		db.df <- Pimp.identify.metabolites.by.db(file=mzmatch.outputs$final.combined.related.file,
  			database=mzmatch.outputs$stds.xml.db,
  			groups=groups,
  			annot=annot,
 			adducts=parent.ion,
  			ppm=mzmatch.params$ppm,
  			rtwindow=mzmatch.params$id.rtwindow,
  			rtwindowrelative=TRUE,
  			mzmatch.outputs=mzmatch.outputs)

		data <- .merge.data.frames(df1=data, df2=db.df, database=mzmatch.outputs$stds.xml.db)
	}

	if(length(databases)==0 && ! file.exists(mzmatch.outputs$stds.xml.db)) {
		warning("No Standards or External databases.")
		mzmatch.ipeak.convert.ConvertToText(i=mzmatch.outputs$final.combined.related.id.file,o=mzmatch.outputs$final.combined.related.id.txt,v=TRUE,annotations=annot)
		data <- .parseMzMatchOutput(file=mzmatch.outputs$final.combined.related.id.txt, groups=groups)
	}

	##add polarity
	data$polarity <- polarity

	return(data)
}

Pimp.identify.metabolites.by.db <- function(file=NULL, database=NULL, groups=list(), annot=NULL, mzmatch.outputs=list(), adducts=NULL, ppm=NULL, rtwindow=NULL, rtwindowrelative=FALSE) {
	outfile <- .generateIdentifiedFileName(file=mzmatch.outputs$final.combined.related.id.file, database=database)
	mzmatch.ipeak.util.Identify(i=mzmatch.outputs$final.combined.related.file, v=TRUE,o=outfile, ppm=ppm, rtwindow=rtwindow, rtwindowrelative=rtwindowrelative, databases=database,   ###, rtwindowrelative=TRUE
		adducts=adducts)#, polarity=polarity)

	txtfile <- .generateIdentifiedFileName(file=mzmatch.outputs$final.combined.related.id.txt, database=database)
  	mzmatch.ipeak.convert.ConvertToText(i=outfile,o=txtfile,v=TRUE,annotations=annot)
  	data <- .parseMzMatchOutput(file=txtfile, groups=groups)

  	return(data)
}

.generateIdentifiedFileName <- function(file=NULL, database=NULL) {
	paste(file_path_sans_ext(file),
	paste(basename(file_path_sans_ext(database)),
	file_ext(file), sep="."), sep="_")
}

.merge.data.frames <- function(df1=NULL, df2=NULL, database=NULL) {
	if(!is.null(df1) && !all.equal(rownames(df1), rownames(df2))) {
		stop("Rownames do not match.")
	}

	#unlist(strsplit(paste("identification,ppm,adduct"), ","))
	column.idx <- c("identification", "ppm", "adduct")
	annot.idx <- match(column.idx, names(df2))
	names(df2)[annot.idx] <- paste(file_path_sans_ext(basename(database)), names(df2)[annot.idx], sep="_")

	if(!is.null(df1)) {
		df2 <- df2[,annot.idx]
		return(cbind(df1, df2))
	} else {
		col.order <- 1:ncol(df2)
		col.order <- c(col.order[-annot.idx], annot.idx)
		return(df2[,col.order])
	}
}

.parseMzMatchOutput <- function(file=NULL, groups=list()) {
	if(!file.exists(file)) {
		stop(paste(file, "does not exist"))
	}

	raw.data <- read.table(file=file, sep="\t", quote="", comment.char="", header=TRUE, na.strings=c("NA",""), stringsAsFactors=FALSE, check.names=FALSE)
	id.idx <- which(colnames(raw.data)=="id")
  	mass.idx <- which(colnames(raw.data)=="mass")
	names(raw.data)[mass.idx] <- "Mass"
	raw.data <- raw.data[,-id.idx]


	##########################################################
	## Temporary code.  Andris needs to fix PeakML.Read so it doesn't barf when a peakset has 0 peaks.
	samples.idx <- match(as.character(unlist(groups)), colnames(raw.data))
	missing.samples <- which(is.na(samples.idx))
	if(length(missing.samples) > 0) {
		raw.data[,unlist(groups)[missing.samples]] <- 0
	}
	##
	##########################################################

	samples.idx <- sort(match(as.character(unlist(groups)), colnames(raw.data)))

	#generate checksum
	rownames(raw.data) <- apply(raw.data[,c(1,2,samples.idx)], 1, digest, algo="sha1")

	#paranoid checksum check
	if(!all.equal(rownames(raw.data), unique(rownames(raw.data)))) {
		stop("Non-unique checksums found when generating IDs!!!")
	}

	return(raw.data)
}