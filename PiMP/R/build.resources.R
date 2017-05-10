##Needed for analysis run
#pathways
#compounds
#compounds2Pathways
#kegg2InChi
#XML files
#stds

getKeggCompoundEntries <- function(compounds=keggList("compound"), kegg.limit=10) {
	compound.ids <- names(compounds)
	batches <- split(compound.ids, ceiling(seq_along(compound.ids)/kegg.limit))
	kegg <- list()
	for(i in 1:length(batches)) {
		cat("\r", sprintf("%60s", paste("Batch", i, "of", length(batches))))	
		entries <- keggGet(batches[[i]])
		kegg <- c(kegg, entries)
	}
	cat("\r", sprintf("%60s", ""), "\n")
	return(kegg)
}

getKeggPathwayInfo <- function(pathways=character(), pathways2Compounds=list()) { ##adapted from PAPi code
	#pathways <- data.frame(keggList("pathway"))
	pathways <- data.frame(pathways)
    pathways[2] <- row.names(pathways)
    row.names(pathways) <- 1:nrow(pathways)
    pathways[3] <- apply(pathways[2], 1, function(x){length(pathways2Compounds[[x]])})
    #pathways[3] <- apply(pathways[2], 1, function(x) numbcomp(x))
    colnames(pathways) <- c("name", "id", "number.compounds")
    empty.idx <- which(pathways$number.compounds==0)
    pathways <- pathways[-empty.idx,]
    return(pathways)
}

numbcomp <- function(x) { ##lifted from PAPi code
    compounds <- keggGet(x)
    compounds <- data.frame(compounds[[1]]$COMPOUND)
    compounds <- nrow(compounds)
    if (compounds == 0) {
        x <- gsub("path:map", "ko", x, fixed = TRUE)
        compounds <- try(keggGet(x), silent = TRUE)
        if ("try-error" %in% class(compounds)) {
            compounds <- 0
        }
        else {
            compounds <- data.frame(compounds[[1]]$COMPOUND)
            compounds <- nrow(compounds)
        }
    }
    return(compounds)
}



CTSBatchConvert <- function(ids=character(), from=character(), to=character()) {
    CTSresult <- CTSgetR(id=ids, from=from, to=to)
    missing.idx <- which(CTSresult[,to]=="error")
    if(length(missing.idx) > 0) {
    	CTSresult <- CTSresult[-missing.idx,]
    }
    resultlist <- as.list(as.character(CTSresult[,to]))
    names(resultlist) <- as.character(CTSresult[,from])
    return(resultlist)
}

generatePathway2Compounds <- function(pathways=character()) {
	pathway.ids <- names(pathways)
	pathway2Compounds <- sapply(pathway.ids, .getPathwayCompounds)
	names(pathway2Compounds) <- gsub("path:", "", pathway2Compounds)
	return(pathway2Compounds)
}

.getPathwayCompounds <- function(id=character(1)) {
	pathway <- keggGet(id)
	print(id)
	compounds <- pathway[[1]]$COMPOUND
	if(length(compounds)==0) {
		id <- gsub("path:map", "ko", id, fixed = TRUE)
		pathway <- try(keggGet(id), silent = TRUE)
		if ("try-error" %in% class(pathway)) {
            compounds <- NULL
        }
        else {
        	compounds <- pathway[[1]]$COMPOUND
        }
	}
	return(compounds)
}

generateCompounds2Pathways <- function(pathway2Compounds=list()) {
	compound2Pathways <- list()
	pathway.ids <- names(pathway2Compounds)
	for(i in 1:length(pathway.ids)) {
		print(i)
		pathway.id <- pathway.ids[i]
		compound.ids <- names(pathway2Compounds[[i]])
		for(j in 1:length(compound.ids)) {
			compound2Pathways[[compound.ids[j]]] <- append(compound2Pathways[[compound.ids[j]]], pathway.id)
		}
	}
	return(compound2Pathways)
}



# generateCompounds2Pathways <- function(compounds=list()) {
# 	compounds2Pathways <- list()
# 	for(i in 1:length(compounds)) {
# 		compound <- compounds[[i]]
# 		if(!is.null(compound$PATHWAY)) {
# 			compounds2Pathways[[compound$ENTRY]] <- compound$PATHWAY
# 		}
# 	}
# 	return(compounds2Pathways)
# }






build.kegg.xml <- function(kegg.compounds=list(), outxml="kegg.xml") {
	doc <- newXMLDoc()
	compounds <- newXMLNode("compounds", doc=doc)

	for(i in 1:length(kegg.compounds)) {
		cat("\r", sprintf("%60s", paste("Entry", i, "of", length(kegg.compounds))))
		kegg.compound <- kegg.compounds[[i]]
		id <- kegg.compound$ENTRY
		names <- sub(";$", "", kegg.compound$NAME)
		name <- names[1]
		other.names <- names[-1]
		formula <- gsub("\\s", "", kegg.compound$FORMULA)
		inchi <- PiMP::kegg2InChiKey[[id]]
		smiles <- ""
		description <- ""

		if(length(formula) > 0 && regexpr("\\W|R", formula) == -1 ) {

			compound <- newXMLNode("compound", parent=compounds)
			newXMLNode("id", id, parent=compound)
			newXMLNode("name", name, parent=compound)
			newXMLNode("formula", formula, parent=compound)
			newXMLNode("inchi", inchi, parent=compound)
			newXMLNode("smiles", smiles, parent=compound)
			newXMLNode("description", parent=compound)
			synonyms <- newXMLNode("synonyms", parent=compound)
			sapply(other.names, function(x) { newXMLNode("synonym", x, parent=synonyms)})
		}
	}

	saveXML(doc, file=outxml)#, prefix = '<?xml version="1.0" encoding="utf-8" ?>\n')

}





build.hmdb.xml <- function(files=character(), outxml="hmdb.xml") {
	if(length(files)==0) {
		files <- dir(pattern="*.xml")
	}

	doc <- newXMLDoc()
	compounds <- newXMLNode("compounds", doc=doc)
	for(i in 1:length(files)) {		
		cat("\r", sprintf("%60s", paste("File", i, "of", length(files))))
		hmdb.doc <- xmlParse(file=files[i])

		id <- xpathSApply(hmdb.doc, "/metabolite/accession", xmlValue)
		name <- xpathSApply(hmdb.doc, "/metabolite/name", xmlValue)
		formula <- xpathSApply(hmdb.doc, "/metabolite/chemical_formula", xmlValue)
		inchi <- sub("InChIKey=", "", xpathSApply(hmdb.doc, "/metabolite/inchikey", xmlValue)) ##need to remove "InChIKey="
		smiles <- xpathSApply(hmdb.doc, "/metabolite/smiles", xmlValue)
		description <- ""
		other.names <- xpathSApply(hmdb.doc, "/metabolite/synonyms/synonym", xmlValue)

		if(formula != ""){
			compound <- newXMLNode("compound", parent=compounds)
			newXMLNode("id", id, parent=compound)
			newXMLNode("name", name, parent=compound)
			newXMLNode("formula", formula, parent=compound)
			newXMLNode("inchi", inchi, parent=compound)
			newXMLNode("smiles", smiles, parent=compound)
			newXMLNode("description", parent=compound)
			synonyms <- newXMLNode("synonyms", parent=compound)
			sapply(other.names, function(x) { newXMLNode("synonym", x, parent=synonyms)})
		}
	}
	cat("\r", sprintf("%60s", ""), "\n")
    saveXML(doc, file=outxml)#, prefix = '<?xml version="1.0" encoding="utf-8" ?>\n')

}

build.hmdb.xml.from.file <- function(infile='hmdb_metabolites.xml', outxml="hmdb.xml") {
    doc <- read_xml(infile)

    ids = xml_text(xml_find_all(doc, '/d1:hmdb/d1:metabolite/d1:accession/text()'))
    cat('Found ids\n', file=stderr())
    names = xml_text(xml_find_all(doc, '/d1:hmdb/d1:metabolite/d1:name/text()'))
    cat('Found names\n', file=stderr())
    formulas = xml_text(xml_find_all(doc, '/d1:hmdb/d1:metabolite/d1:chemical_formula/text()'))
    cat('Found formulas\n', file=stderr())
    inchis = xml_text(xml_find_all(doc, '/d1:hmdb/d1:metabolite/d1:inchikey/text()'))
    cat('Found inchis\n', file=stderr())
    smiles = xml_text(xml_find_all(doc, '/d1:hmdb/d1:metabolite/d1:smiles/text()'))
    cat('Found smiles\n', file=stderr())
    description <- ""
    other.names = xml_find_all(doc, '/d1:hmdb/d1:metabolite/d1:synonyms')
    cat('Found other.names\n', file=stderr())

    newdoc = xml_new_document()
    compounds = xml_add_child(newdoc, 'compounds')
    pb <- txtProgressBar(min=1, max=length(ids), style=3)
    for (i in 1:length(ids)) {
        setTxtProgressBar(pb, i)
        compound = xml_add_child(compounds, 'compound')
        xml_add_child(compound, 'id', ids[i])
        xml_add_child(compound, 'name', names[i])
        xml_add_child(compound, 'formula', formulas[i])
        xml_add_child(compound, 'inchi', inchis[i])
        xml_add_child(compound, 'smiles', smiles[i])
        xml_add_child(compound, 'description')
        synonyms = xml_add_child(compound, 'synonyms')
        sapply(xml_text(xml_children(other.names[i])), function(x) xml_add_child(synonyms, 'synonym', x))
    }
    close(pb)
    write_xml(newdoc, file=outxml)
}

update.hmdb.xml <- function(inxml="hmdb.xml", outxml="hmdb-new.xml") {
	doc = read_xml(inxml)
	ids = xml_text(xml_find_all(doc, '/compounds/compound/id/text()'))
	urls = paste(get.hmdb.url(ids), '.xml', sep='')
    build.hmdb.xml(files=urls, outxml=outxml)
}

build.lipidmaps.xml <- function(file=character(), outxml="lipidmaps.xml") {
	if(length(file)==0) {
		stop("No file")
	}

	lipids <- read.table(file=file, header=TRUE, sep="\t", quote="", comment.char="")

	doc <- newXMLDoc()
	compounds <- newXMLNode("compounds", doc=doc)

	for(i in 1:nrow(lipids)) {
		cat("\r", sprintf("%60s", paste("Lipid", i, "of", nrow(lipids))))
		id <- as.character(lipids$LM_ID)[i]
		name <- ifelse(as.character(lipids$COMMON_NAME)[i]!="", as.character(lipids$COMMON_NAME)[i], as.character(lipids$SYSTEMATIC_NAME)[i])
		formula <- gsub("\\s", "", as.character(lipids$FORMULA)[i])
		inchi <- as.character(lipids$INCHI_KEY)[i]
		smiles <- ""
		description <- ""
		other.names <- NULL
		if(as.character(lipids$COMMON_NAME)[i]!="") {
			if(as.character(lipids$SYSTEMATIC_NAME)[i]!="") {
				other.names <- append(other.names, as.character(lipids$SYSTEMATIC_NAME)[i])
			}
		}
		lm_synonyms <- as.character(unlist(strsplit(as.character(lipids$SYNONYMS)[i], "; ")))
		if(length(lm_synonyms) > 0) {
			other.names <- append(other.names, lm_synonyms)
		}

		if(length(formula) > 0 && regexpr("\\W", formula) == -1) {
			compound <- newXMLNode("compound", parent=compounds)
			newXMLNode("id", id, parent=compound)
			newXMLNode("name", name, parent=compound)
			newXMLNode("formula", formula, parent=compound)
			newXMLNode("inchi", inchi, parent=compound)
			newXMLNode("smiles", smiles, parent=compound)
			newXMLNode("description", parent=compound)
			synonyms <- newXMLNode("synonyms", parent=compound)
			if(!is.null(other.names)) {
				sapply(other.names, function(x) { newXMLNode("synonym", x, parent=synonyms)})
			}
		}
	}

	cat("\r", sprintf("%60s", ""), "\n")
    saveXML(doc, file=outxml, indent=TRUE)#, prefix = '<?xml version="1.0" encoding="utf-8" ?>\n')

}