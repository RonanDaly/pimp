library()

# TODO: this can be done in Python
getNeededString = function(name) {
    Sys.getenv(name, unset=NA)
}

# TODO: this can be done in Python
getString = function(name, default) {
    Sys.getenv(name, unset=default)
}

# TODO: this can be done in Python
getInteger = function(name, default) {
    value = getNeededString(name)
    if ( is.na(value) ) {
        return(default)
    }
    return(as.numeric(value))
}

getDatabaseConnection <- function() {
    library(PiMPDB)
    dbtype = getNeededString('PIMP_DATABASE_ENGINE')
    if ( dbtype == 'django.db.backends.mysql' ) {
        DATABASE_TYPE = 'mysql'
        PIMP_DATABASE_NAME = getNeededString('MYSQL_DATABASE')
        PIMP_DATABASE_USER = getNeededString('MYSQL_USER')
        PIMP_DATABASE_PASSWORD = getNeededString('MYSQL_PASSWORD')
    } else if ( dbtype == 'django.db.backends.sqlite3' ) {
        DATABASE_TYPE = 'sqlite'
        PIMP_DATABASE_NAME = file.path(getNeededString('PIMP_BASE_DIR'), getNeededString('SQLITE_DATABASE_FILENAME'))
        PIMP_DATABASE_USER = ''
        PIMP_DATABASE_PASSWORD = ''
    } else {
        stop(paste('The database type', dbtype, 'is not recognised'))
    }

    db <- new("PiMPDB",
        dbuser=PIMP_DATABASE_USER,
        dbpassword=PIMP_DATABASE_PASSWORD,
        dbname=PIMP_DATABASE_NAME,
        dbhost=getString('PIMP_DATABASE_HOST', ''),
        dbport=getInteger('PIMP_DATABASE_PORT', 0),
        dbtype=DATABASE_TYPE
	)
	return(db)
}

# TODO: this can be done in Python
Pimp.getAnalysisParams <- function(analysis_id) {

    logger <- getPiMPLogger('Pimp.getAnalysisParams')
    setPiMPLoggerAnalysisID(analysis_id)

    db = getDatabaseConnection()
    pimp.params = getDefaultSettings()

    analysis.params <- getAnalysisParameters(db, analysis_id)
    param.idx <- which(analysis.params$state==1 | analysis.params$state==0)
    if(length(param.idx) > 0) {
        params <- analysis.params[param.idx,]
        loginfo('Setting params', logger=logger)

        for(i in 1:nrow(params)) {
            logdebug('Name: %s Value: %s', params$name[i], params$value[i], logger=logger)

            if (params$state[i] == 1) {

                if(params$name[i]=="ppm") {
                    pimp.params$xcms.params$ppm <- params$value[i]
                    pimp.params$mzmatch.params$ppm <- params$value[i]
                }
                else if(params$name[i]=="rt.alignment") {
                    pimp.params$mzmatch.params$rt.alignment <- "obiwarp"
                }
                else if(params$name[i]=="rtwindow") {
                    pimp.params$mzmatch.params$id.rtwindow <- params$value[i]
                }
                else {
                    if(is.na(params$value[i])){
                        pimp.params$mzmatch.params[[params$name[i]]] <- TRUE
                    }
                    else {
                        pimp.params$mzmatch.params[[params$name[i]]] <- params$value[i]
                    }

                }
            }
            pimp.params$mzmatch.filters[[params$name[i]]] = as.logical(params$state[i])
        }
    }
    return(pimp.params)

}

# format mzmatch outputs to insert the analysis id and polarity into the strings
Pimp.getFormattedMzmatchOutputs <- function(analysis_id, polarity, mzmatch_outputs) {

    #mzmatch_outputs <- lapply(mzmatch_outputs, function(x) {
    #    sub(paste0("^", mzmatch_outputs$analysis.folder),
    #        paste0(mzmatch_outputs$analysis.folder, "_", analysis_id), x)
    #})
    mzmatch_outputs <- lapply(mzmatch_outputs, sprintf, polarity)
    return(mzmatch_outputs)

}

# TODO: this can be done in Python ..?
Pimp.createAnalysisDir <- function(analysis_id, pimp_params, working_dir) {

    logger <- getPiMPLogger('Pimp.createAnalysisDir')
    setPiMPLoggerAnalysisID(analysis_id)
    loginfo('Setting working dir to %s: ', working_dir, logger=logger)
    setwd(working_dir)
    mzmatch.outputs <- pimp_params$mzmatch.outputs

    ##create analysis directory
    if(!is.null(analysis_id)) {
        message(paste0("Setting analysis directory to: ", paste(mzmatch.outputs$analysis.folder, analysis_id, sep="_")))
        mzmatch.outputs <- lapply(mzmatch.outputs, function(x) {
            sub(paste0("^", mzmatch.outputs$analysis.folder),
                paste0(mzmatch.outputs$analysis.folder, "_", analysis_id), x)
        }
        )
        #mzmatch.outputs$analysis.folder = paste(mzmatch.outputs$analysis.folder, analysis_id, sep="_")
    }
    dir.create(mzmatch.outputs$analysis.folder)

    loginfo('Analysis dir created at %s', mzmatch.outputs$analysis.folder, logger=logger)

    # update the value back into pimp_params
    pimp_params$mzmatch.outputs <- mzmatch.outputs
    return(pimp_params)

}

# generate the full database paths and also the standard xml if needed
Pimp.generateStdXml <- function(standards, databases, pimp_params, wd) {

    logger <- getPiMPLogger('Pimp.generateStdXml')
    loginfo('Setting working directory to %s', wd, logger=logger)
    setwd(wd)
    mzmatch.outputs <- pimp_params$mzmatch.outputs

    #Generate STDs annotation XML file
    stds <- NULL
    if(length(standards) > 0 && 'standard' %in% databases) {
        stds  <- Pimp.stds.createAnnotationFile(files=standards, outfile=mzmatch.outputs$stds.xml.db)
    } else {
        mzmatch.outputs$stds.xml.db <- NULL
    }
    databases = databases[ ! databases == 'standard']

    ##Get external annotation database info - using our own DBs rather than the out of data MzMatch ones which are out of date.
    DBS <- dir(system.file("dbs", package=getPackageName()), full.names=TRUE, pattern=paste(databases, ".*\\.xml$", sep="", collapse="|"), ignore.case=TRUE)

    if(length(DBS)!=length(databases)) {
        stop("Not all annotation databases found.")
    }

    output <- list(databases=databases, DBS=DBS)
    return(output)

}

# -----------------------------------------------------------------------------
# to check from here onwards
# -----------------------------------------------------------------------------

Pimp.runStats.save <- function(raw.data.pos, raw.data.neg,
                               analysis_id, factors, metadata, contrasts,
                               databases, DBS, mzmatch_outputs, mzmatch_params, saveFixtures, wd) {

    save(raw.data.pos, raw.data.neg,
         analysis_id, factors, metadata, contrasts,
         databases, DBS, mzmatch_outputs, mzmatch_params, saveFixtures, wd,
         file='runStats.RData')

    Pimp.runStats(raw.data.pos, raw.data.neg,
                    analysis_id, factors, metadata, contrasts, comparisonNames,
                    databases, DBS, mzmatch_outputs, mzmatch_params, saveFixtures, wd)

}

Pimp.runStats <- function(raw.data.pos, raw.data.neg,
                               analysis_id, factors, metadata, contrasts, comparisonNames,
                               databases, DBS, mzmatch_outputs, mzmatch_params, saveFixtures, wd) {

    setwd(wd)
    logger <- getPiMPLogger('Pimp.runStats')
    setPiMPLoggerAnalysisID(analysis_id)

    normalization <- 'none'
    reports <- 'xml'

    # is this still necessary???????
    # set java to headless mode - prevents MacOS barfing in spreadsheet generation
    .jcall("java/lang/System","S","setProperty","java.awt.headless","true")

    # extract the actual parameters
    mzmatch.outputs <- mzmatch_outputs

    #Data are returned in data.frame with checksum as peak id.  Row bind if two polarities
    if(exists("raw.data.pos") && exists("raw.data.neg")) {
        loginfo('Two polarities exist', logger=logger)

        logfine('Positive rownames: %s', rownames(raw.data.pos), logger=logger)
        logfine('Negative rownames: %s', rownames(raw.data.neg), logger=logger)
        if(length(intersect(rownames(raw.data.pos), rownames(raw.data.neg)))!=0) {
            stop(paste("None unique rownames across negative and positive metabolites."))
        }

        raw.data.pos.names = names(raw.data.pos)
        raw.data.neg.names = names(raw.data.neg)
        logdebug('Positive names: %s', raw.data.pos.names, logger=logger)
        logdebug('Negative names: %s', raw.data.neg.names, logger=logger)
        isEqualNames = all.equal(raw.data.pos.names, raw.data.neg.names)
        loginfo('isEqualNames: %s', isEqualNames, logger=logger)
        if(!isTRUE(isEqualNames)) {
            stop(paste("Columns for positive and negative data do not match."))
        }

        save(file="raw.data.pos.RData", raw.data.pos)
        save(file="raw.data.neg.RData", raw.data.neg)

        raw.data <- rbind(raw.data.pos, raw.data.neg) #check columns
    } else if(exists("raw.data.pos")) {
        save(file="raw.data.pos.RData", raw.data.pos)
        raw.data <- raw.data.pos
    } else if(exists("raw.data.neg")) {
        save(file="raw.data.neg.RData", raw.data.neg)
        raw.data <- raw.data.neg
    } else {
        stop("No Raw Data objects exist.")
    }

    ##
    ## Preparation of raw data for statistics
    ##

    #Remove analysis samples from data for statistical analysis
    row.names(metadata) = metadata$sample
    metadata$sample = NULL
    sample.metadata = metadata[na.omit(match(colnames(raw.data), row.names(metadata))),]

    #Preprocess raw data for statistical analysis. Keep BP plus those matching to STD, set 0s to NA
    preprocessed <- .preProcessRawData(raw.data=raw.data, sample.metadata, factors, minintensity = mzmatch_params$minintensity)

    #Normalization if required. Default is "none"
    norm.data <- Pimp.normalize(preprocessed$data, method=normalization)

    #Log 2 transform data - required for parametric stats (normal distribution required), compariable up/down fold changes
    norm.data <- log2(norm.data)


    ##
    ## Statistics - PCA, Differential statistics, Pathways - Would be good to do Over/under represented pathways, but tricky unless just use those matched to standards
    ##

    ##differential analysis using ebayes
    diff.stats <- Pimp.statistics.differential(data=norm.data, contrasts=contrasts, method="ebayes", sample.metadata=sample.metadata, repblock=NULL)
    toptables <- lapply(diff.stats, function(fit){topTable(fit, coef=1, genelist=data.frame(Mass=preprocessed$Mass, RT=preprocessed$RT), number=length(fit$coef[,1]), confint=TRUE)})      #[,c("Mass", "RT", "logFC","P.Value","adj.P.Val")]
    names(toptables) <- names(diff.stats)

    #pca plot coloured by groups
    pca <- Pimp.statistics.pca(data=norm.data, sample.metadata=sample.metadata, factorNames = factors, file="pca.svg")

    ##
    ## Output
    ##

    #ids
    identification <- Pimp.report.generateIdentifications(raw.data=raw.data, databases=DBS, stds.db=mzmatch.outputs$stds.xml.db)

    #pathway stuff
    compound.ids <- unique(as.character(identification$DBID[which(identification$DB=="kegg")]))
    compound.std.ids <- unique(as.character(identification$DBID[which(identification$DB=="kegg" & identification$publishable=="Identified")]))
    compound.info <- identification[which(identification$DB=="kegg"),]

    if ( 'kegg' %in% databases ) {
        identified.compounds.by.pathway <- .get.identified.compounds.by.pathways(ids=compound.ids, compounds2Pathways=PiMP::compounds2Pathways)
        pathway.stats <- Pimp.report.generatePathwayStatistics(pathways=PiMP::pathways, compound.info=compound.info, compound.std.ids=compound.std.ids, identified.compounds.by.pathway=identified.compounds.by.pathway, toptables=toptables)
    } else {
        identified.compounds.by.pathway = list()
        pathway.stats = data.frame()
    }

    #excel
    #if("excel" %in% reports) {
    #    Pimp.exportToExcel(databases=databases, stds.db=mzmatch.outputs$stds.xml.db, raw.data=raw.data, groups=data.groups, identification=identification, preprocessed=preprocessed, diff.stats=diff.stats, toptables=toptables, pathway.stats=pathway.stats, identified.compounds.by.pathway=identified.compounds.by.pathway, compound.ids=compound.ids, compound.std.ids=compound.std.ids, compound.info=compound.info)
    #}

    message("XML Reports")

    if("xml" %in% reports) {
        logger$info('Getting database connection')
        db = getDatabaseConnection()
        if(!exists("db")) {
            warning("No database connection.  Unable to generate XML file.")
        }
        else if(is.null(analysis_id)) {
            warning("No analysis ID.  Unable to generate XML file.")
        }
        else {
            if ( saveFixtures ) {
                logger$info('Saving Pimp.exportToXML.Robj_fixture')
                dir.create(file.path('tests', 'fixtures'), recursive=TRUE)
                save(analysis_id, raw.data, identification, toptables, pathway.stats,
                     identified.compounds.by.pathway, contrasts, file=file.path('tests', 'fixtures', 'Pimp.exportToXML.Robj_fixture'))
            }
            Pimp.exportToXML(id=analysis_id, raw.data=raw.data, identification=identification, toptables=toptables, pathway.stats=pathway.stats, identified.compounds.by.pathway=identified.compounds.by.pathway, contrasts=contrasts, db=db)
        }
    }

    #save analysis and session information
    sessionInfo <- sessionInfo()
    save(sessionInfo, file="sessionInfo.RData")
    save.image(paste0(mzmatch.outputs$analysis.folder, ".RData"))

}

.preProcessRawData <- function(raw.data=data.frame(), sample.metadata, factorNames, minintensity=NULL) {
  if ( is.numeric(minintensity) ) {
    low_level = minintensity
  } else {
    low_level = 1
  }

	##select only columns of samples of interest i.e. no QC, blanks, stds
  intensities.idx = match(row.names(sample.metadata), colnames(raw.data))

	#get rows containing basepeaks or match to standard
	basepeaks <- which(raw.data$relation.ship=="bp" | raw.data$relation.ship=="potential bp")
	stds <- which(!is.na(raw.data$stds_db_identification))

	# If _all_ the replicates in a group are NA or 0, then replace with low level
	# Else leave alone
	smd = as.data.table(sample.metadata, keep.rownames=TRUE)
	count = smd[, list(Rows=list(.I)), by = eval(factorNames)]
	for (group in count$Rows) {
	  for (i in 1:nrow(raw.data)) {
	    if ( all(raw.data[i,group] == 0 | is.na(raw.data[i,group])) ) {
	      raw.data[i,group] = low_level
	    }
	  }
	}

	data <- as.matrix(raw.data[unique(basepeaks,stds),intensities.idx]) #subset to produce data for statistical analysis
	# NB The gap filler must have fillAll=TRUE to make sure we aren't setting missing peaks to 1, i.e. the only
	# peaks that should be set to 1 are those that have levels too low to detect.
	data[data==0] <- NA ##convert 0s to NAs

	Mass <- raw.data[unique(basepeaks,stds),'Mass']
	RT <- raw.data[unique(basepeaks,stds),'RT']

	return(list(data=data, Mass=Mass, RT=RT))
}

Pimp.my.metabolome <- function(..., seconds=5, interval=0.5) {
	.welcome(interval, seconds)
	Pimp.runPipeline(...)
	.goodbye(interval, seconds)
}