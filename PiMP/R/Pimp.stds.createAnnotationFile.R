Pimp.stds.createAnnotationFile <- function(files=character(), outfile=NULL) {
  # This is the InChIKey generated with no structure
  emptyInChIKey = 'MOSFIJXAXDLOML-UHFFFAOYSA-N'
  
  logger <- getPiMPLogger('Pimp.stds.createAnnotationFile')
  logger$info('Creating annotation file from %s, outputting to %s', files, outfile)
	stds <- .parseStandardsFiles(files=files)
	logger$info('Matching names to standard2InChIKey database')
	stds.idx <- match(tolower(stds$name), tolower(names(PiMP::standard2InChIKey)))
	inchiKeys = as.character(PiMP::standard2InChIKey[stds.idx])
	inchiKeys[inchiKeys == 'NULL'] = emptyInChIKey
	stds$inchi = inchiKeys
	RCreateXMLDB(data=stds, outputfile=outfile)
	if(!file.exists(outfile)) {
		stop(paste(outfile), "not created.")
	}
	return(stds)
}

.parseStandardsFiles <- function(files=character()) {
  logger <- getPiMPLogger('Pimp.stds.createAnnotationFile.parseStandardsFiles')
  logger$info('Parsing standards files')
	#determine type

	if(length(files)<1) {
		stop("No files found!")
	}
	
	data <- NULL
	for(i in 1:length(files)) {
		parser <- .determineFileParser(file=files[i])
		data <- rbind(data, parser(infile=files[i]))
	}
	return(data)
	#return(.parse.toxid.files(files=files))
}

.determineFileParser <- function(file=NULL) {
  logger <- getPiMPLogger('Pimp.stds.createAnnotationFile.determineFileParser')
	if(is.null(file)) {
		stop("No file found.")
	}

	if(file_ext(file) == "xlsx") {
		parser <- .parse.xlsx.file
		logger$info('Parser for %s is .parse.xlsx.file', file)
	}
	else {
		info <- readLines(con=file)
		info <- sub(",$", "", info)

		#nMetaDataLines <- NULL

		if(length(grep("Peak Num", info, ignore.case = TRUE)) > 0) {
			parser <- .parse.toxid.file
			logger$info('Parser for %s is .parse.toxid.file', file)
		}
		else if(length(grep("retentiontime", info, ignore.case = TRUE)) > 0) {
			parser <- .parse.csv.file
			logger$info('Parser for %s is .parse.csv.file', file)
		}
		else {
			stop(paste("Standards file", file, "type not recognised."))
		}
	}
	return(parser)
}

# .parseFiles <- function(files=character(), parser=NULL) {
# 	if(length(files)<1) {
# 		stop("No files found!")
# 	}

# 	if(is.null(parser)) {
# 		stop("No parser specified.")
# 	}
	
# 	data <- NULL
# 	for(i in 1:length(files)) {
# 		data <- rbind(data, parser(infile=files[i]))
# 	}
# 	return(data)
# }

.parse.csv.file <- function(infile=NULL, sep=",", quote="") {
  logger <- getPiMPLogger('Pimp.stds.createAnnotationFile.parse.csv.file')
  logger$info('Parsing csv file: %s', infile)
	if(!file.exists(infile)) stop(paste(infile, "does not exist", sep=""))

	info <- readLines(con=infile)
	info <- sub(",$", "", info)
	#nMetaDataLines <- grep("retentiontime", info, ignore.case = TRUE) - 1
	#if(length(nMetaDataLines)==0) stop(paste(file, "does not look like a ToxID file"), sep=" ")

	data <- read.csv(text=info, header=TRUE, stringsAsFactors=FALSE, quote="\"")

	id <- paste(file_path_sans_ext(basename(infile)), 1:dim(data)[1], sep="_")
	data <- cbind(id, data)

	return(data)
}

.parse.xlsx.file <- function(infile=NULL) {
  logger <- getPiMPLogger('Pimp.stds.createAnnotationFile.parse.xlsx.file')
  logger$info('Parsing xlsx file: %s', infile)
	if(!file.exists(infile)) stop(paste(infile, "does not exist", sep=""))

	##makes assumption data in first sheet.
	data <- readWorksheetFromFile(infile, sheet=1)

	if(!all(c("name", "formula", "retentiontime", "polarity") %in% colnames(data))) {
		stop(paste(infile, "does not contain the correct column names."))
	}

	return(data)
}

.parse.toxid.file <- function(infile=NULL, sep=",", quote="") {
  logger <- getPiMPLogger('Pimp.stds.createAnnotationFile.parse.toxid.file')
  logger$info('Parsing toxid file: %s', infile)
  if(!file.exists(infile)) stop(paste(infile, "does not exist", sep=" "))
    
	##find start of table by reading in a few lines and finding "Peak Num" column
	info <- readLines(con=infile)
	info <- sub(",$", "", info)
	nMetaDataLines <- grep("Peak Num", info, ignore.case = TRUE) - 1
	if(length(nMetaDataLines)==0) stop(paste(file, "does not look like a ToxID file"), sep=" ")
		
	##read in data	
	data <- read.csv(text=info, header=TRUE, skip=nMetaDataLines, stringsAsFactors=FALSE)
	
	#remove "." from column names	
	names(data) <- gsub("\\.+", "_", tolower(names(data)))

	##select only Compound_Name, Formula, Expected_RT and Actual_RT columns
	columns.idx <- match(c("compound_name", "formula", "actual_rt", "polarity"), names(data))
	data <- data[,columns.idx]

	#filter out "-" retention times
	rt.to.rm <- which(as.character(data$actual_rt)=="-")
	if(length(rt.to.rm) > 0) {
		#data <- data[-which(as.character(data$actual_rt)=="-"),]
		data <- data[-which(is.na(as.numeric(as.character(data$actual_rt)))),]
	}

	##replace "_" with "," in Compound_Name
	data$compound_name <- gsub("_", ",", as.character(data$compound_name))

	colnames(data) <- c("name", "formula", "retentiontime", "polarity") #tolower(colnames(data))

	id <- paste(file_path_sans_ext(basename(infile)), 1:dim(data)[1], sep="_")
	data <- cbind(id, data)
	
	return(data)
}