Pimp.report.generateIdentifications <- function(raw.data=data.frame(), databases=character(), stds.db=NULL) {
    if(dim(raw.data)[1] == 0) {
        stop("raw.data does not contain any data.")
    }
    if(length(databases) == 0) {
        stop("No annotation databases provided.")
    }
    if(!is.null(stds.db) && !file.exists(stds.db)) {
        warning(paste(stds.db, "does not exist."))
    }

    #create vector of all DBs for identification
    if(is.null(stds.db) || !file.exists(stds.db)) {
        all.databases <- databases
    } else {
        all.databases <- c(databases, stds.db)
    }

    external <- .build.external.db.lookup(databases=all.databases)


    identification.cols <- c("id", "mass", "RT", "DB", "DBID", "ppm", "adduct")

    #identification.cols <- c("id", "mass", "RT", "formula", "DB", "DBID", "name", "ppm", "adduct", "publishable")
    #identification.cols <- c("id", "mass", "RT", "formula", "DB", "DBID", "name", "InChi", "ppm", "adduct", "publishable")

    identification.list <- list()
    row <- 1
    for (i in 1:dim(raw.data)[1]) {
        id <- rownames(raw.data)[i]
        mass <- raw.data[i,'Mass']
        rt <- raw.data[i,'RT']
        for (d in 1:length(all.databases)) {
            db <- basename(file_path_sans_ext(all.databases[d]))
            if(!is.na(raw.data[i,paste(db, "identification", sep="_")])) {
                db.ids <- unlist(strsplit(as.character(raw.data[i,paste(db, "identification", sep="_")]), ",\\s+", perl=TRUE))
                db.ppms <- unlist(strsplit(as.character(raw.data[i,paste(db, "ppm", sep="_")]), ",\\s+", perl=TRUE))
                db.adducts <- unlist(strsplit(as.character(raw.data[i,paste(db, "adduct", sep="_")]), ",\\s+", perl=TRUE))
                #db.names <- unlist(strsplit(as.character(raw.data[i,paste(db, "name", sep="_")]), ",\\s+", perl=TRUE))
                #db.inchi <- unlist(strsplit(as.character(raw.data[i,paste(db, "InChi", sep="_")]), ",\\s+", perl=TRUE))
                #db.formulas <- unlist(strsplit(as.character(raw.data[i,paste(db, "formula", sep="_")]), ",\\s+", perl=TRUE))
                for (j in 1:length(db.ids)) {
                    identification.list[[row]] <- c(id, mass, rt, db, db.ids[j], db.ppms[j], db.adducts[j])
                    row <- row+1
                }
            }
            #else if(is.null(raw.data[i,paste(db, "identification", sep="_")])) {message(i)}
        }
    }
    identification <- as.data.frame(do.call("rbind", identification.list), stringsAsFactors=FALSE)
    names(identification) <- identification.cols
    identification$mass <- as.numeric(identification$mass)
    identification$RT <- as.numeric(identification$RT)

    identification$names <- as.character(external[as.character(identification$DBID), "name"])
    identification$formula <- as.character(external[as.character(identification$DBID), "formula"])
    identification$InChIKey <- as.character(external[as.character(identification$DBID), "inchi"])
    identification$publishable <- "Annotated"
    #identification <- .identify.stds.in.external.db(identification=identification, databases=databases, stds.db=stds.db)

    if(!is.null(stds.db) && file.exists(stds.db)) {
        identification <- .identify.stds.in.external.db(identification=identification, external=external, stds.db=basename(file_path_sans_ext(stds.db)))
    }

    return(identification)
}

.build.external.db.lookup <- function(databases=character()) {
    external <- data.frame()
    for(i in 1:length(databases)) {
        c <- xmlToDataFrame(xmlChildren(xmlRoot(xmlParse(file=databases[i]))))[,c("id", "name", "formula", "inchi")]
        rownames(c) <- as.character(c$id)
        external <- rbind(external, c)
    }
    return(external)
}

.identify.stds.in.external.db <- function(identification=data.frame(), external=data.frame(), stds.db=character()) {
    identification$publishable <- "Annotated"
    stds.idx <- which(identification$DB==stds.db )
    #identification$publishable[stds.idx] <- "Identified"

    for(i in 1:length(stds.idx)) {
        std.id <- as.character(identification$id[stds.idx[i]])
        std.inchi <- as.character(identification$InChIKey[stds.idx[i]])
        inchi.idx <- which(identification$id==std.id & identification$InChIKey==std.inchi)
        identification$publishable[inchi.idx] <- "Identified"
    }

    return(identification)

}

# .identify.stds.in.external.db <- function(identification=data.frame(), databases=character(), stds.db=NULL) {
# 	if(dim(identification)[1] == 0) {
# 		stop("raw.data does not contain any data.")
# 	}
# 	if(!any(file.exists(databases))) {
# 		stop("Some XML databases do not exist.")
# 	}
# 	if(is.null(stds.db) | !file.exists(stds.db)) {
# 		stop("Unable to find standards XML database.")
# 	}

# 	stds.db <- file_path_sans_ext(basename(stds.db))

# 	stds.idx <- which(identification$DB==stds.db)
# 	stds <- identification[stds.idx,]

# 	publishable <- rep("Annotated", dim(identification)[1])
# 	publishable[stds.idx] <- "Identified"

# 	#for each database
# 	for(d in 1:length(databases)) {
# 		# if(databases[d]=="stds_db") {
# 		# 	next
# 		# }
# 		message(file_path_sans_ext(basename(databases[d])))
# 		doc <- xmlParse(databases[d])

# 		#detect formula type in XML [M1];[C39H82N2O6P+]n or C39H82N2O6P+
# 		is.extended <- .is.extended.formula(doc)
# 		#find matches by name/formula to std hit
# 		for(s in 1:dim(stds)[1]) {
# 			id <- as.character(stds[s,'id'])
# 			name <- as.character(stds[s,'name'])
# 			formula <- as.character(stds[s,'formula'])

# 			hits <- unique(xpathSApply(doc, 
# 				.build.xpath.query(name, ifelse(is.extended,.convert.formula(formula),formula)), xmlValue, simplify=TRUE 
# 			))

# 			if(length(hits) > 0) {
# 				for(h in 1:length(hits)) {
# 					publish <- which(
# 						identification[,'id']==id &
# 						identification[,'DB']==basename(file_path_sans_ext(databases[d])) &
# 						identification[,'DBID']==hits[h] &
# 						identification[,'formula']==formula &
# 						identification[,'name']==name)

# 					if(length(publish)>0) {
# 						publishable[publish] <- "Identified"
# 					}	
# 				}
# 			}
# 		}
# 	}
# 	identification$publishable <- publishable
# 	return(identification)
# }

# .build.xpath.query <- function(name, formula) {
# 	return(paste(
# 		"//compound[",
# 			"(", 
# 				"./name[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')=\"", tolower(name), "\"] or ",
# 	    		"./synonyms/synonym[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')=\"", tolower(name), "\"]", 
# 	    	")", 
# 		" and ./formula[text()=\"", formula, "\"]]/id", sep="")
# 	)
# }

# .is.extended.formula <- function(doc) {
# 	is.extended <- grepl("\\[\\w+\\];\\[\\w+|\\+|\\-\\]n", xpathSApply(doc, "//compound/formula", xmlValue), perl=T)
# 	if(all(is.extended)) {
# 		return(TRUE)
# 	}
# 	else if(all(!is.extended)) {
# 		return(FALSE)
# 	}
# 	else {
# 		stop("Mixed formula types in XML annotation file.")
# 	}
# }

# .convert.formula <- function(formula) {
# 	return(paste("[M1];[", formula, "]n", sep=""))
# 	#return(gsub("\\[M1\\];\\[(.*)\\]n", "\\1", formula))
# }