Pimp.report.generatePDF <- function(peakml=NULL, xlsx=NULL, databases=character(), outDirectory="chromatograms", sampleGroups = NULL, layoutMtx = NULL, ppm = 3, trendPlots = NULL, useArea = FALSE, peakRTWindow = 30, excludeFromPlots = NULL) {
    logger <- getPiMPLogger('Pimp.processRawData.report.generatePDF')
	##Read PeakML data
	PeakMLData <- PeakML.Read(peakml, ionisation = "neutral", NULL)

	##Read from report
	if (file.exists(xlsx)) {
        xls.rawData <- readWorksheetFromFile(file=xlsx, sheet="RawData")#read.xlsx(xlsx, sheetName="RawData")
        xls.identification <- readWorksheetFromFile(file=xlsx, sheet="Identification")
    }

    ## Reading the PeakML file
    massCorrection <- PeakML.Methods.getMassCorrection(filename=peakml)
    if (massCorrection < 0){
        sampleType = "NEG"
    } else if (massCorrection > 0){
        sampleType = "POS"
    } else {
        sampleType = "NONE"
    }

    ##### Sample Groups ##########
    phenoData <- PeakML.Methods.getPhenoData(PeakMLData$sampleClasses, PeakMLData$sampleNames, PeakMLData$peakDataMtx)
    ## To enable the user to change the order of the samples
    if (is.null(sampleGroups)) sampleGroups <- unique(phenoData)

    exclude <- NULL
    if (!is.null(excludeFromPlots)) {
        exclude <- which(sampleGroups %in% excludeFromPlots)
        if (length(excludeFromPlots)!=length(exclude)){
            stop("The sample group you wanted to exlude from the final output does not exist in the sample groups")
        }
    }

    ##### Plot Order ##########
    ## The plots we want in the output file, replace empty with what ever we want at a later point
    if (is.null(trendPlots)) trendPlots <- c("TREND", "EMPTY", "EMPTY", "EMPTY")
    ## The layoutMtx to layout the PDF file.

    if (length(sampleGroups)>22) {
        if (is.null(layoutMtx)){
            stop("You have more than 22 samples to plot. Please specify an appropriate layout matrix.\n")
        } else {
            plotOrder <- c(sampleGroups, trendPlots)
        }
    } else {
        numSG <- length(sampleGroups)
        if (numSG < 7){
            if (is.null(layoutMtx)) layoutMtx <- matrix(c(1,1,1,1,1,1,2, 3,4,5,6,7,8,9, 10,10,11,12,12,13,13),3,7, byrow=TRUE)
            plotOrder <- c(sampleGroups, rep("EMPTY", 7-numSG), trendPlots)
        } else if (numSG >= 7 & numSG <=14){
            if (is.null(layoutMtx)) layoutMtx <- matrix(c(1,1,1,1,1,1,2, 3,4,5,6,7,8,9, 10,11,12,13,14,15,16, 17,17,18,19,19,20,20),4,7, byrow=TRUE)
            plotOrder <- c(sampleGroups, rep("EMPTY", 14-numSG), trendPlots)
        } else if (numSG > 14 & numSG <=21){
            if (is.null(layoutMtx)) layoutMtx <- matrix(c(1,1,1,1,1,1,2, 3,4,5,6,7,8,9, 10,11,12,13,14,15,16, 17,18,19,20,21,22,23, 24,24,25,26,26,27,27),5,7, byrow=TRUE)
            plotOrder <- c(sampleGroups, rep("EMPTY", 21-numSG), trendPlots)
        }

    }

    outDirectory <- file.path(dirname(peakml), outDirectory)
    dir.create (outDirectory, showWarnings = FALSE)

    ## xls.rawData
    ## xls.identification

    for (i in 1:nrow(xls.rawData)){

        raw.peakid <- as.character(xls.rawData$ID[i])
        raw.peakmass <- as.numeric(xls.rawData$Mass[i])
        if (version.1==FALSE) raw.peakmass <-  raw.peakmass + massCorrection
        raw.peakrt <- as.numeric(xls.rawData$RT[i])
        raw.relationid <- as.numeric(xls.rawData$relation.id[i])
        raw.relationship <- as.character(xls.rawData$relation.ship[i])
        raw.charge <- as.character(xls.rawData$charge[i])

        idData <- xls.identification[which(xls.identification$ID == as.character(raw.peakid)),]
        id.name <- unique(idData$Name)
        id.formula <- unique(idData$Formula)
        id.adducts <- unique(idData$Adduct)
        #id.pathways <- unique(unlist(strsplit(as.character(idData$Pathways), ",")))
        loginfo('%d %s .....', i, raw.peakid, logger=logger)
        annotations <- list("peakID"=raw.peakid, "peakMass"=raw.peakmass, "peakRT"=raw.peakrt,
                            "peakName"=id.name, "formula"=id.formula, "relationID"=raw.relationid,
                            "relationShip"=raw.relationship, "charge"=raw.charge)

        ## Get Peak Groups within that RT and Mass window. This is very very important as the first hit in that RT and Mass Window is not guaranteed to be the correct peak for that met.
        peakGroups <- mzmatch.pipeline.plot.getPeakGroups (PeakMLData, raw.peakmass, raw.peakrt, ppm, peakRTWindow)

        if (!is.null(unlist(peakGroups))){
            chromatograms <- mzmatch.pipeline.plot.getChromatograms (PeakMLData, peakGroups, phenoData, sampleGroups)

            ## To generate the pdf plots
            pdfFile <- paste(outDirectory, "/", annotations$peakID, ".pdf", sep="")
            pdf (file=pdfFile, paper="a4", height=10, width=7)

            ## Page 1 Will have the info about each peak
            ## (PeakMLdata, groupid, sampleClasses=NULL, xaxis=TRUE, Title=NULL, mar=c(2,1,0,1))
            loutMtx <- matrix(c(1,2,2,2, 3,3,4,4), 2, 4, byrow=TRUE)
            layout(loutMtx, heights=c(0.4, rep(1, nrow(loutMtx)-1)), TRUE)
            mzmatch.pipeline.plot.plotPeakInfo(PeakMLData, peakGroups, sampleGroups, annotations)


            ## Page 2
            ## Create the layout for the pdf
            layout(layoutMtx, heights=c(0.4, rep(1, nrow(layoutMtx)-1)), TRUE)
            ## Reading the list of targets in the mol formula file
            mzmatch.pipeline.plot.plotSamples(PeakMLData, chromatograms, annotations, sampleType, sampleGroups, plotOrder, useArea, excludeFromPlots)

            ## mzmatch.pipeline.plot.plotRelatedPeaks(
            dev.off()
        } else{
            loginfo("No peaks found with mass: %s and its isotopes", annotations[["peakMass"]], logger=logger)
        }
    }
}