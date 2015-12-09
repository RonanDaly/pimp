Pimp.exportToXML <- function(id=NULL, raw.data=data.frame(), identification=data.frame(), toptables=list(), pathway.stats=data.frame(), identified.compounds.by.pathway=list(), ...) {

    if(is.null(id)) {
        stop("No analysis id found.")
    }

    if(nrow(raw.data)==0) {
        stop("No raw.data found.")
    }

    if(nrow(identification)==0) {
        stop("No identification data found")
    }

    if(!exists("db")) {
        warn("No database connection.  Unable to create XML file.")
        return()
    }
    
	#con <- dbConnect("SQLite", dbname = "~/Downloads/sqlite3.db")

    experiment_id <- getExperimentID(db, id)

    experiment.samples <- getExperimentSamples(db, experiment_id)

    ##QCs
    controls <- getExperimentControls(db, experiment.id)

    #get required controls.  Currently only blanks
    blank.idx <- which(controls$type=="blank")
    controls <- controls[blank.idx,]
    #control.pos <- file.path("calibration_samples", "POS", controls$name)
    #control.neg <- file.path("calibration_samples", "NEG", controls$name)

    #files$positive <- c(files$positive, control.pos)
    #files$negative <- c(files$negative, control.neg)

    #if(nrow(controls) > 0) {
    #    groups$Blank <- file_path_sans_ext(controls$name)
    #}

	doc <- newXMLDoc()

	##top node
    gpimp <- newXMLNode("gpimp:pimp_analysis", 
    	doc = doc, 
    	namespace = c(
    		gpimp="http://puma.ibls.gla.ac.uk/ns/gpimp/1.0",
    		xsi="http://www.w3.org/2001/XMLSchema-instance"
    	),
    	attrs=c(
        	"xsi:schemaLocation"="http://puma.ibls.gla.ac.uk/ns/gpimp/1.0 http://puma.ibls.gla.ac.uk/ns/gpimp/1.0/pimp_framework.xsd",
        	id=id
        )
    )

    ##settings
    settings <- newXMLNode("settings", parent=gpimp)

    ##group set
    groupset <- newXMLNode("groupset", parent=settings)

    ##get experiment groups
    message("Writing group information...")

    experiment.groups <- getExperimentGroups(db, experiment_id)
    control.groups <- getControlGroups(db, experiment.id)

    experiment.groups <- rbind(experiment.groups, control.groups)

    for(i in 1:nrow(experiment.groups)) {
        group <- newXMLNode("group", attrs=c("id"=experiment.groups$id[i]), parent=groupset)
        group.name <- newXMLNode("name", experiment.groups$name[i], parent=group)
        member.set <- newXMLNode("memberset", parent=group)

        group.members <- getExperimentGroupMembersAll(db, experiment.groups$id[i])

        for(j in 1:nrow(group.members)) {
            member <- newXMLNode("member", attrs=c("id"=group.members$id[j]), parent=member.set)
            member.name <- newXMLNode("name", group.members$name[j], parent=member)

            if(experiment.groups$name[i]=="calibration_group") {
                samples <- getControlMemberSamples(db, group.members$id[j])
            }
            else {
                samples <- getMemberSamples(db, group.members$id[j])
            }

            sample.set <- newXMLNode("sampleset", parent=member)
            for (k in 1:nrow(samples)) {
                sample <- newXMLNode("sample", attrs=c("id"=samples$id[k]), parent=sample.set)
                sample.name <- newXMLNode("name", samples$name[k], parent=sample)
            }
        }
    }

    ##member comparison set
    message("Writing comparison information...")

    member.comparison.set <- newXMLNode("member_comparison_set", parent=settings)

    experiment.comparisons <- getExperimentComparisons(db, experiment_id)
    for(i in nrow(experiment.comparisons)) {
        contrasts <- experiment.comparisons$contrast
        cntrls <- experiment.comparisons$control
        con = unlist(strsplit(cntrls, '-'))
        if ( con[1] == '0' ) {
            cont = unlist(strsplit(contrasts, '-'))
            contrasts = paste0(cont[2], '-', cont[1])
            experiment.comparisons$contrast[i] <- contrasts
        }
    }

    for(i in 1:nrow(experiment.comparisons)) {
        member.comparison <- newXMLNode("member_comparison", attrs=c("id"=experiment.comparisons$id[i]), parent=member.comparison.set)
        comparison.members <- getExperimentComparisonMembers(db, experiment.comparisons$id[i])
        sapply(comparison.members, function(x) newXMLNode("member_reference", attrs=c("id"=x), parent=member.comparison))
    }


    ##parameters
    message("Writing parameter information...")

    parameterset <- newXMLNode("parameterset", parent=settings)

    parameters <- getAnalysisParameters(db, id)

    for(i in 1:nrow(parameters)) {
        name <- parameters$name[i]
        value <- parameters$value[i]
        state <- as.logical(parameters$state[i])
        if(state && !is.na(value)) {
            parameter <- newXMLNode("parameter", attrs=c("type"="numeric_conditional_parameter"), parent=parameterset)
            newXMLNode("name", name, parent=parameter)
            numeric_conditional_parameter <- newXMLNode("numeric_conditional_parameter", parent=parameter)
            newXMLNode("state", "on", parent=numeric_conditional_parameter)
            newXMLNode("value", value, parent=numeric_conditional_parameter)
        }
        else if (state && is.na(value)) {
            parameter <- newXMLNode("parameter", attrs=c("type"="conditional_parameter"), parent=parameterset)
            newXMLNode("name", name, parent=parameter)
            conditional_parameter <- newXMLNode("conditional_parameter", parent=parameter)
            newXMLNode("state", "on", parent=conditional_parameter)
        }
    }


    ##peakset
    message("Writing peak information...")

    peakset <- newXMLNode("peakset", parent=gpimp)

    samples.idx <- match(file_path_sans_ext(experiment.samples$name), colnames(raw.data))

    identification <- .generateCompoundIds(identification)

    #compound.id <- 1
    for(i in 1:nrow(raw.data)) {
        cat(paste(i,"of",nrow(raw.data), "my custom message", "\r"))
        peak.id <- rownames(raw.data)[i]
        peak <- newXMLNode("peak", attrs=c("id"=peak.id), parent=peakset)
        newXMLNode("mass", raw.data$Mass[i], parent=peak)
        newXMLNode("retention_time", raw.data$RT[i], parent=peak)
        newXMLNode("polarity", raw.data$polarity[i], parent=peak)
        newXMLNode("type", raw.data$relation.ship[i], parent=peak)

        #identification
        compoundset <- newXMLNode("compoundset", parent=peak)
        comparisonset <- newXMLNode("comparisonset", parent=peak) 
        identified.idx <- which(peak.id == identification$id)
        if(length(identified.idx) > 0) {
            identified.subset <- identification[identified.idx,]
            #identified.subset$idx <- identified.idx

            no.inchi.idx <- which(as.character(identified.subset$InChIKey)=="")
            inchi.idx <- which(as.character(identified.subset$InChIKey)!="")

            inchi.subset <- unique(identified.subset[inchi.idx, c("id", "formula", "ppm", "adduct", "InChIKey", "publishable", "compound.id")])
            no.inchi.subset <- identified.subset[no.inchi.idx,] #check about adduct
            #inchi.subset <- inchi.sub
            if(nrow(inchi.subset) > 0) {
                for(j in 1:nrow(inchi.subset)) {
                    compound <- newXMLNode("compound", attrs=c("id"=inchi.subset$compound.id[j]), parent=compoundset)
                    newXMLNode("formula", inchi.subset$formula[j], parent=compound)
                    newXMLNode("inchikey", inchi.subset$InChIKey[j], parent=compound)
                    newXMLNode("ppm", inchi.subset$ppm[j], parent=compound)
                    newXMLNode("adduct", inchi.subset$adduct[j], parent=compound)
                    newXMLNode("identified", inchi.subset$publishable[j], parent=compound)
                    ##add inchi
                    #annotation name????????
                    compound.idx <- which(as.character(identified.subset$InChIKey)==inchi.subset$InChIKey[j])
                    dbset <- newXMLNode("dbset", parent=compound)
                    for(k in 1:length(compound.idx)) {
                        db <- newXMLNode("db", parent=dbset)
                        newXMLNode("db_name", identified.subset$DB[compound.idx[k]], parent=db)
                        newXMLNode("identifier", identified.subset$DBID[compound.idx[k]], parent=db)
                        newXMLNode("compound_name", identified.subset$name[compound.idx[k]], parent=db)
                    }

                    #compound.id <- compound.id + 1
                }
            }

            if(nrow(no.inchi.subset) > 0) {
                for(j in 1:nrow(no.inchi.subset)) {
                    compound <- newXMLNode("compound", attrs=c("id"=no.inchi.subset$compound.id[j]), parent=compoundset)
                    newXMLNode("formula", no.inchi.subset$formula[j], parent=compound)
                    newXMLNode("inchikey", parent=compound)
                    newXMLNode("ppm", no.inchi.subset$ppm[j], parent=compound)
                    newXMLNode("adduct", no.inchi.subset$adduct[j], parent=compound)
                    newXMLNode("identified", no.inchi.subset$publishable[j], parent=compound)
                    dbset <- newXMLNode("dbset", parent=compound)
                    db <- newXMLNode("db", parent=dbset)
                    newXMLNode("db_name", no.inchi.subset$DB[j], parent=db)
                    newXMLNode("identifier", no.inchi.subset$DBID[j], parent=db)
                    newXMLNode("compound_name", no.inchi.subset$name[j], parent=db)
                    ##add inchi
                    #compound.id <- compound.id + 1
                }
            }

            # for(j in 1:length(compound.idx)) {
            #     compound <- newXMLNode("compound", attrs=c("id"=compound.idx[j]), parent=compoundset)
            #     newXMLNode("formula", identification$formula[compound.idx[j]], parent=compound)
            #     newXMLNode("name", identification$name[compound.idx[j]], parent=compound)
            #     newXMLNode("db", identification$DB[compound.idx[j]], parent=compound)
            #     newXMLNode("dbid", identification$DBID[compound.idx[j]], parent=compound)
            #     # url <- get.compound.url(id=identification$DBID[compound.idx[j]], db=identification$DB[compound.idx[j]])
            #     # if(!is.null(url)) {
            #     #     newXMLNode("dblink", url, parent=compound)
            #     # }
            #     newXMLNode("ppm", identification$ppm[compound.idx[j]], parent=compound)
            #     newXMLNode("adduct", identification$adduct[compound.idx[j]], parent=compound)
            #     newXMLNode("identified", identification$publishable[compound.idx[j]], parent=compound)
            # }
        }

            #comparisons            
        for(k in 1:nrow(experiment.comparisons)) {
            tt <- toptables[[experiment.comparisons$name[k]]]
            peak.idx <- match(peak.id, rownames(tt))
            if(!is.na(peak.idx) && !is.na(tt$P.Value[peak.idx])){
                comparison <- newXMLNode("comparison", attrs=c("id"=experiment.comparisons$id[k]), parent=comparisonset) 
                newXMLNode("logfc", tt$logFC[peak.idx], parent=comparison)
                newXMLNode("pvalue", tt$P.Value[peak.idx], parent=comparison)
                newXMLNode("adjpvalue", tt$adj.P.Val[peak.idx], parent=comparison)
                newXMLNode("logodds", tt$B[peak.idx], parent=comparison)
            }
        }            
    
                    ##add sample intensities
        sampleintensityset <- newXMLNode("sample_intensity_set", parent=peak)
        for(l in 1:nrow(experiment.samples)) {
            samplereference <- newXMLNode("sample_reference", attrs=c("id"=experiment.samples$id[l]), parent=sampleintensityset)
            newXMLNode("intensity", raw.data[i,samples.idx[l]], parent=samplereference)
        }

        control.idx <- match(file_path_sans_ext(controls$name), colnames(raw.data))
        calibrationintensityset <- newXMLNode("calibration_intensity_set", parent=peak)
        if(length(control.idx)>0) {
            for(l in 1:nrow(controls)) {
                calibrationreference <- newXMLNode("calibration_reference", attrs=c("id"=controls$id[l]), parent=calibrationintensityset)
                newXMLNode("intensity", raw.data[i,control.idx[l]], parent=calibrationreference)
            }
        }


        

    }

    message("Writing pathway information...")

    pathwayset <- newXMLNode("pathwayset", parent=gpimp)

    pathway.compounds <- identification[which(identification$DB=="kegg"),]    

    for(i in seq(length = nrow(pathway.stats))) {
        pathway <- newXMLNode("pathway", attrs=c("id"=pathway.stats$id[i]), parent=pathwayset)
        newXMLNode("name", pathway.stats$name[i], parent=pathway)
        newXMLNode("compound_number", pathway.stats$number.compounds[i], parent=pathway)
        compound_in_pathwayset <- newXMLNode("compound_in_pathwayset", parent=pathway)

        dbid.idx <- which(
            pathway.compounds$DBID %in% identified.compounds.by.pathway[[pathway.stats$id[i]]], 
            arr.ind=T
            )
        lapply(
            unique(pathway.compounds[dbid.idx,'compound.id']),
            #1, 
            function(x) {
                #newXMLNode("compound_in_pathway", attrs=c("id"=as.integer(x['compound.id'])), parent=compound_in_pathwayset)
                newXMLNode("compound_in_pathway", attrs=c("id"=as.integer(x)), parent=compound_in_pathwayset)
            }
        )
    }





       #b = newXMLNode("bar", parent = n)
     
          # suppress the <?xml ...?>
    saveXML(doc, file=paste0("analysis_", id, ".xml"))#, prefix = '<?xml version="1.0" encoding="utf-8" ?>\n')

    #dbdisconnect(db)
}

.generateCompoundIds <- function(identification=data.frame()) {
    inchi.idx <- which(identification$InChIKey!="")
    inchi <- identification$InChIKey[inchi.idx]
    unique.inchi <- unique(inchi)
    inchi.compound.id <- 1:length(unique.inchi)

    inchi.compound.idx <- match(inchi,unique.inchi)
    identification$compound.id[inchi.idx] <- inchi.compound.id[inchi.compound.idx]

    no.inchi.idx <- which(identification$InChIKey=="")
    no.inchi.compound.id <- (1:length(no.inchi.idx)) + max(inchi.compound.id)
    identification$compound.id[no.inchi.idx] <- no.inchi.compound.id

    return(identification)
}

#select experiment_id, params_id from experiments_analysis where id= 1; #experiment_id=1, params_id=1
