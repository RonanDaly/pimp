Pimp.exportToXML <- function(id=NULL, raw.data=data.frame(), identification=data.frame(), toptables=list(), pathway.stats=data.frame(), identified.compounds.by.pathway=list(), sample.metadata, contrasts, ...) {
    logger <- getPiMPLogger('Pimp.exportToXML')

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
    controls <- getExperimentControls(db, experiment_id)

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

  doc = read_xml(sprintf('<?xml version="1.0"?>
              <gpimp:pimp_analysis
                xmlns:gpimp="http://puma.ibls.gla.ac.uk/ns/gpimp/1.0"
                xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                xsi:schemaLocation="http://puma.ibls.gla.ac.uk/ns/gpimp/1.0 http://puma.ibls.gla.ac.uk/ns/gpimp/1.0/pimp_framework.xsd"
                id="%s"></gpimp:pimp_analysis>', id))

    ##settings
    settings = xml_add_child(doc, 'settings')

    ##group set
    groupset = xml_add_child(settings, 'groupset')

    ##get experiment groups
    message("Writing group information...")

    experiment.groups <- getExperimentGroups(db, experiment_id)
    control.groups <- getControlGroups(db, experiment_id)

    experiment.groups <- rbind(experiment.groups, control.groups)

    for(i in 1:nrow(experiment.groups)) {
        group = xml_add_child(groupset, 'group', id=as.character(experiment.groups$id[i]))
        group.name = xml_add_child(group, 'name', experiment.groups$name[i])
        member.set = xml_add_child(group, 'memberset')

        group.members <- getExperimentGroupMembersAll(db, experiment.groups$id[i])

        for(j in 1:nrow(group.members)) {
            member = xml_add_child(member.set, 'member', id=as.character(group.members$id[j]))
            member.name = xml_add_child(member, 'name', group.members$name[j])

            if(experiment.groups$name[i]=="calibration_group") {
                samples <- getControlMemberSamples(db, group.members$id[j])
            }
            else {
                samples <- getMemberSamples(db, group.members$id[j])
            }

            sample.set = xml_add_child(member, 'sampleset')
            for (k in 1:nrow(samples)) {
                if ( length(samples$id[k]) ) {
                  sample = xml_add_child(sample.set, 'sample', id=as.character(samples$id[k]))
                  sample.name = xml_add_child(sample, 'name', samples$name[k])
                } else {
                  sample = xml_add_child(sample.set, 'sample')
                  sample.name = xml_add_child(sample, 'name')
                }
            }
        }
    }

    ##member comparison set
    message("Writing comparison information...")

    member.comparison.set = xml_add_child(settings, "member_comparison_set")

    #experiment.comparisons <- getExperimentComparisons(db, experiment_id)
    #for(i in nrow(experiment.comparisons)) {
    #    contrasts <- experiment.comparisons$contrast
    #    cntrls <- experiment.comparisons$control
    #    con = unlist(strsplit(cntrls, ','))
    #    if ( con[1] == '0' ) {
    #        cont = unlist(strsplit(contrasts, ','))
    #        contrasts = paste0(cont[2], ',', cont[1])
    #        experiment.comparisons$contrast[i] <- contrasts
    #    }
    #}
    
    for (comparison in unique(contrasts$comparison)) {
      comparison_id = contrasts[contrasts$comparison == comparison,'id'][1]
      factor = contrasts[contrasts$comparison == comparison,'factor'][1]
      member.comparison = xml_add_child(member.comparison.set, 'member_comparison', id=as.character(comparison_id))
      comparison.members = [contrasts$factor == factor,'level'
    }

    for(i in 1:nrow(experiment.comparisons)) {
        member.comparison = xml_add_child(member.comparison.set, 'member_comparison', id=as.character(experiment.comparisons$id[i]))
        comparison.members <- getExperimentComparisonMembers(db, experiment.comparisons$id[i])
        sapply(comparison.members, function(x) xml_add_child(member.comparison, 'member_reference', id=as.character(x)))
    }


    ##parameters
    message("Writing parameter information...")

    parameterset = xml_add_child(settings, 'parameterset')

    parameters <- getAnalysisParameters(db, id)

    for(i in 1:nrow(parameters)) {
        name <- parameters$name[i]
        value <- parameters$value[i]
        state <- as.logical(parameters$state[i])
        if(state && !is.na(value)) {
            parameter = xml_add_child(parameterset, 'parameter', 'type'='numeric_conditional_parameter')
            xml_add_child(parameter, 'name', name)
            numeric_conditional_parameter = xml_add_child(parameter, 'numeric_conditional_parameter')
            xml_add_child(numeric_conditional_parameter, 'state', 'on')
            xml_add_child(numeric_conditional_parameter, 'value', value)
        }
        else if (state && is.na(value)) {
            parameter = xml_add_child(parameterset, 'parameter', 'type'='conditional_parameter')
            xml_add_child(parameter, 'name', name)
            conditional_parameter = xml_add_child(parameter, 'conditional_parameter')
            xml_add_child(conditional_parameter, 'state', 'on')
        }
    }


    ##peakset
    message("Writing peak information...")

    peakset = xml_add_child(doc, 'peakset')

    samples.idx <- match(file_path_sans_ext(experiment.samples$name), colnames(raw.data))

    identification <- .generateCompoundIds(identification)

    #compound.id <- 1
    nrow.raw.data = nrow(raw.data)
    for(i in 1:nrow(raw.data)) {
        logging::logfine('Peak %d of %d', i, nrow.raw.data, logger=logger)
        #cat(paste(i,"of",nrow(raw.data), "my custom message", "\r"))
        peak.id <- rownames(raw.data)[i]
        peak = xml_add_child(peakset, 'peak', id=as.character(peak.id))
        xml_add_child(peak, 'mass', raw.data$Mass[i])
        xml_add_child(peak, 'retention_time', raw.data$RT[i])
        xml_add_child(peak, 'polarity', raw.data$polarity[i])
        xml_add_child(peak, 'type', raw.data$relation.ship[i])

        #identification
        compoundset = xml_add_child(peak, 'compoundset')
        comparisonset = xml_add_child(peak, 'comparisonset')
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
                    compound = xml_add_child(compoundset, 'compound', id=as.character(inchi.subset$compound.id[j]))
                    xml_add_child(compound, 'formula', inchi.subset$formula[j])
                    xml_add_child(compound, 'inchikey', inchi.subset$InChIKey[j])
                    xml_add_child(compound, 'ppm', inchi.subset$ppm[j])
                    xml_add_child(compound, 'adduct', inchi.subset$adduct[j])
                    xml_add_child(compound, 'identified', inchi.subset$publishable[j])
                    ##add inchi
                    #annotation name????????
                    compound.idx <- which(as.character(identified.subset$InChIKey)==inchi.subset$InChIKey[j])
                    dbset = xml_add_child(compound, 'dbset')
                    for(k in 1:length(compound.idx)) {
                        db = xml_add_child(dbset, 'db')
                        xml_add_child(db, 'db_name', identified.subset$DB[compound.idx[k]])
                        xml_add_child(db, 'identifier', identified.subset$DBID[compound.idx[k]])
                        #escapedName = stringi::stri_escape_unicode(identified.subset$name[compound.idx[k]])
                        #encodedName = sub('\\\\u..(..)', '&#x\\U\\1;', escapedName, perl=TRUE)
                        xml_add_child(db, 'compound_name', identified.subset$name[compound.idx[k]])
                    }

                    #compound.id <- compound.id + 1
                }
            }

            if(nrow(no.inchi.subset) > 0) {
                for(j in 1:nrow(no.inchi.subset)) {
                    compound = xml_add_child(compoundset, 'compound', id=as.character(no.inchi.subset$compound.id[j]))
                    xml_add_child(compound, 'formula', no.inchi.subset$formula[j])
                    xml_add_child(compound, 'inchikey')
                    xml_add_child(compound, 'ppm', no.inchi.subset$ppm[j])
                    xml_add_child(compound, 'adduct', no.inchi.subset$adduct[j])
                    xml_add_child(compound, 'identified', no.inchi.subset$publishable[j])
                    dbset = xml_add_child(compound, 'dbset')
                    db = xml_add_child(dbset, 'db')
                    xml_add_child(db, 'db_name', no.inchi.subset$DB[j])
                    xml_add_child(db, 'identifier', no.inchi.subset$DBID[j])
                    #escapedName = stringi::stri_escape_unicode(no.inchi.subset$name[j])
                    #encodedName = sub('\\\\u..(..)', '&#x\\U\\1;', escapedName, perl=TRUE)
                    xml_add_child(db, 'compound_name', no.inchi.subset$name[j])
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
                comparison = xml_add_child(comparisonset, 'comparison', id=as.character(experiment.comparisons$id[k]))
                xml_add_child(comparison, 'logfc', tt$logFC[peak.idx])
                xml_add_child(comparison, 'pvalue', tt$P.Value[peak.idx])
                xml_add_child(comparison, 'adjpvalue', tt$adj.P.Val[peak.idx])
                xml_add_child(comparison, 'logodds', tt$B[peak.idx])
            }
        }            
    
                    ##add sample intensities
        sampleintensityset = xml_add_child(peak, 'sample_intensity_set')
        for(l in 1:nrow(experiment.samples)) {
            samplereference = xml_add_child(sampleintensityset, 'sample_reference', id=as.character(experiment.samples$id[l]))
            xml_add_child(samplereference, 'intensity', raw.data[i,samples.idx[l]])
        }

        control.idx <- match(file_path_sans_ext(controls$name), colnames(raw.data))
        calibrationintensityset = xml_add_child(peak, 'calibration_intensity_set')
        if(length(control.idx)>0) {
            for(l in 1:nrow(controls)) {
                calibrationreference = xml_add_child(calibrationintensityset, 'calibration_reference', id=as.character(controls$id[l]))
                xml_add_child(calibrationreference, 'intensity', raw.data[i,control.idx[l]])
            }
        }


        

    }

    message("Writing pathway information...")

    pathwayset = xml_add_child(doc, 'pathwayset')
    
    pathway.compounds <- identification[which(identification$DB=="kegg"),]    

    for(i in seq(length = nrow(pathway.stats))) {
        pathway = xml_add_child(pathwayset, 'pathway', id=as.character(pathway.stats$id[i]))
        xml_add_child(pathway, 'name', as.character(pathway.stats$name[i]))
        xml_add_child(pathway, 'compound_number', pathway.stats$number.compounds[i])
        compound_in_pathwayset = xml_add_child(pathway, 'compound_in_pathwayset')

        dbid.idx <- which(
            pathway.compounds$DBID %in% identified.compounds.by.pathway[[pathway.stats$id[i]]], 
            arr.ind=TRUE
            )
        lapply(
            unique(pathway.compounds[dbid.idx,'compound.id']),
            #1, 
            function(x) {
                #newXMLNode("compound_in_pathway", attrs=c("id"=as.integer(x['compound.id'])), parent=compound_in_pathwayset)
                xml_add_child(compound_in_pathwayset, 'compound_in_pathway', id=as.character(as.integer(x)))
            }
        )
    }





       #b = newXMLNode("bar", parent = n)
     
          # suppress the <?xml ...?>
    write_xml(doc, file=paste0("analysis_", id, ".xml"))

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
