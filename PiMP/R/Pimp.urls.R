get.db.url <- function(id=NULL, db=NULL) {
    url <- switch(
        db,
        hmdb      = get.hmdb.url(id),
        kegg      = get.kegg.url(id),
        lipidmaps = get.lipidmaps.url(id)
        #none = data
    )
    return(url)
}

get.kegg.url <- function(id=NULL) {
    return(sprintf("http://www.genome.jp/dbget-bin/www_bget?%s", id))
}

get.hmdb.url <- function(id=NULL) {
    return(sprintf("http://www.hmdb.ca/metabolites/%s", id))
}

get.lipidmaps.url <- function(id=NULL) {
    return(sprintf("http://www.lipidmaps.org/data/LMSDRecord.php?LMID=%s", id))
}

get.compound.url <- function(id=NULL, db=NULL) {
    url <- switch(
        db,
        hmdb = get.hmdb.url(id),
        kegg = get.kegg.url(id)
    )
    return(url)
}

get.pubchem.properties.url <- function(inchi=NULL) {
    return("http://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/property/MolecularFormula,InChI,InChIKey/XML")
}

get.pubchem.properties <- function(name=NULL) {
    NoResult <- FALSE
    tryCatch(
        {
            result = getForm(
                get.pubchem.properties.url(),
                .params = c(
                    name=name
                ),
                #.opts=curlOptions(ssl.verifypeer=TRUE, cainfo=system.file("CurlSSL", "cacert.pem", package = "RCurl"))
            )
        },
        error=function(e) {
            message("Problem connecting to ", get.pubchem.properties.url())
            NoResult <<- TRUE
        }
    )

    if(!NoResult) {
        #pathApply(xmlRoot(doc1), "//nih:Properties", namespaces=c(nih="http://pubchem.ncbi.nlm.nih.gov/pug_rest"), xmlValue)
        df <- xmlToDataFrame(result)
        return(df)
    }
    else {
        return(NA)
    }
}

get.pug.ns <- function() {
    return("http://pubchem.ncbi.nlm.nih.gov/pug_rest")
}

get.goo.gl.url <- function() {
    return("https://www.googleapis.com/urlshortener/v1/url")
}

get.bitly.url <- function() {
    return("https://api-ssl.bitly.com/v3/shorten")
}

get.bitly.access_token <- function() {
    return("be9db37284447f9f1094f4fd66c37335bc761112")
}

get.kegg.pathway.url <- function(pathway.id, object.id.list, fg.color.list, bg.color.list) {
    pathway.id <- sub("path:", "", pathway.id)
    url <- sprintf("http://www.kegg.jp/kegg-bin/show_pathway?%s/",#default%%3dpink/",
        pathway.id)
    segs <- sprintf("%s%%09%s,%s", object.id.list, fg.color.list, 
        bg.color.list)
    url <- sprintf("%s%s", url, paste(segs, collapse = "/"))
    url <- .cleanUrl(url)
    return(url)
}

shortenURL <- function(url=character()) {
    NoResult <- FALSE
    tryCatch(
        {
            result = getForm(
                get.bitly.url(),
                .params = c(
                    access_token=get.bitly.access_token(),
                    longUrl=url
                ),
                .opts=curlOptions(ssl.verifypeer=TRUE, cainfo=system.file("CurlSSL", "cacert.pem", package = "RCurl"))
            )
            #Sys.sleep(2)
            # result = postForm(
            #     get.goo.gl.url(), 
            #     .opts=list(
            #         httpheader = c('Content-Type' = 'application/json', 
            #             Accept = 'application/json'),
            #         postfields = toJSON(
            #             list(
            #                 longUrl=as.character(url)
            #             )
            #         ),
            #          timeout = 10, 
            #         nosignal = TRUE
            #     )
            # )
        },
        error=function(e) {
            message("Problem connecting to ", get.bitly.url())
            NoResult <<- TRUE
        }
    )

    if(!NoResult) {
        json <- fromJSON(result, simplify=FALSE)
        return(json$data$url)
    }
    else {
        return(NA)
    }
}

.cleanUrl <- function(url)
{
     url <- gsub(" ", "%20", url, fixed=TRUE)
     url <- gsub("#", "%23", url, fixed=TRUE)
     url <- gsub(":", "%3a", url, fixed=TRUE)
     sub("http%3a//", "http://", url, fixed=TRUE)
}