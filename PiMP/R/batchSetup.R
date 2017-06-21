#library(XML)

getFileCreatedTime <- function(f) {
    inf = file.info(f)
    inf$mtime
}

getMLFileCreatedTime <- function(f) {
  logger <- getPiMPLogger('Pimp.batchSetup.getMLFileCreatedTime')

  loginfo(f, logger=logger)
  tree = xmlTreeParse(f)
  r = xmlRoot(tree)
  time = xmlGetAttr(r[['mzML']][['run']], 'startTimeStamp')
  as.POSIXct(strptime(time, format="%Y-%m-%dT%H:%M:%S"))
}

# This function creates the batch information structure that is a sufficient
# record of the measurement set up. The structure is a data frame, identified
# by the data file(sample) and contains columns for the batch, time the measurement
# was made, the sequence file the batch information was found from, the type
# of a particular sample (e.g. QC, normal sample), and the peakml, mzxml and
# raw files associated with the sample.
# INPUTS:
# sequenceFiles - A vector of CSV files that contain the batch information
# typeColumnName - The name of the column in the CSV files that contains the sample type information
# fileColumnName - The name of the column in the CSV files that contains the file information
# peakmlFileDirectory - The directory root, under which, peakML files are stored.
# rawFileDirectory - The directory root, under which, RAW files are stored.
# mzxmlFileDirectory - The directory root, under which, mzXML files are stored.
# mzmlFileDirectory - The directory root, under which, mzML files are stored.
createBatchInformation <- function(sequenceFiles, typeColumnName, fileColumnName, peakmlFileDirectory, rawFileDirectory, mzxmlFileDirectory, mzmlFileDirectory ) {
    batch = 1
    batchColumn = c()
    idColumn = c()
    timeColumn = c()
    sequenceFileColumn = c()
    typeColumn = c()
    peakmlFileColumn = c()
    mzxmlFileColumn = c()
    rawFileColumn = c()
    mzmlFileColumn = c()
    
    for (f in sequenceFiles) {
        data = read.csv(f, skip=1, header=TRUE, stringsAsFactors=FALSE)
        idString = paste(data[[fileColumnName]], collapse='|')
    mzmlfs = dir(path=mzmlFileDirectory,pattern=paste0('(', idString, ').mzML'),recursive=TRUE,full.names=TRUE)
        #rawfs = dir(path=rawFileDirectory,pattern=paste0('(', idString, ').raw'),recursive=TRUE,full.names=TRUE)
        #mzxmlfs = dir(path=mzxmlFileDirectory,pattern=paste0('(', idString, ').mzXML'),recursive=TRUE,full.names=TRUE)
        #peakmlfs = dir(path=peakmlFileDirectory,pattern=paste0('(', idString, ').peakml'),recursive=TRUE,full.names=TRUE)

        for (i in 1:nrow(data)) {
            dataFileId = data[i,fileColumnName]
            mzmlf = mzmlfs[grepl(paste0(dataFileId, '.mzML'), mzmlfs)]
            rawf = paste0(rawFileDirectory, '/', sub('\\.mzML', '\\.raw', mzmlf))
                  #rawf = rawfs[grepl(paste0(dataFileId, '.raw'), rawfs)]
                  mzxmlf = paste0(mzxmlFileDirectory, '/', sub('\\.mzML', '\\.mzXML', mzmlf))
                  peakmlf = paste0(mzxmlFileDirectory, '/', sub('\\.mzML', '\\.peakml', mzmlf))
            #print(rawf)
            #print(mzxmlf)
            #mzxmlf = mzxmlfs[grepl(paste0(dataFileId, '.mzXML'), mzxmlfs)]
            #peakmlf = peakmlfs[grepl(paste0(dataFileId, '.peakml'), peakmlfs)]

            if ( length(mzmlf) > 0 && file.exists(mzmlf) ) {
                ctime = getMLFileCreatedTime(mzmlf)
                batchColumn = append(batchColumn, batch)
                idColumn = append(idColumn, dataFileId)
                timeColumn = append(timeColumn, ctime)
                sequenceFileColumn = append(sequenceFileColumn, f)
                typeColumn = append(typeColumn, data[i, typeColumnName])
                peakmlFileColumn = append(peakmlFileColumn, peakmlf)
                rawFileColumn = append(rawFileColumn, rawf)
                mzxmlFileColumn = append(mzxmlFileColumn, mzxmlf)
                mzmlFileColumn = append(mzmlFileColumn, mzmlf)
            }
        }
        batch = batch + 1        
    }
    if ( length(timeColumn) == 0 ) {
      stop('No batch information. Length timeColumn: ', length(timeColumn))
    }
    offsets = as.numeric(difftime(timeColumn, timeColumn[1], units='hours'))    
    createBatchInformation = data.frame(row.names=idColumn, batchColumn, offsets,
        sequenceFileColumn, as.factor(typeColumn), peakmlFileColumn, rawFileColumn,
        mzxmlFileColumn, mzmlFileColumn, stringsAsFactors=FALSE)
    names(createBatchInformation) = c('batch', 'time', 'sequenceFile', 'type', 'peakmlFile', 'rawFile', 'mzxmlFile', 'mzmlFile')
    createBatchInformation
}

createBatchInformationFromGroups <- function(groups, files) {
  logger = logging::getLogger('createBatchInformationFromGroups')

  longNames = c()
  longIds = c()
  batch = c()
  for (n in names(groups)) {
    numIds = length(groups[[n]])
    longNames = append(longNames, rep(n, numIds))
    longIds = append(longIds, groups[[n]])
    for (b in groups[[n]]) {
      batchName = strsplit(b, split='_', fixed=TRUE)[[1]][1]
      batch = append(batch, batchName)
    }
  }
  df = data.frame(row.names=longIds,type=longNames,batch=batch)
  
  shortFiles = c()
  for (f in files) {
    bName = strsplit(basename(f), split='.', fixed=TRUE)[[1]][1]
    shortFiles = append(shortFiles, bName)
  }
  
  reorderedFiles = c()
  reorderedTimes = c()
  for (id in row.names(df)) {
    index = match(id, shortFiles)
    loginfo('files[%d]: %s', index, files[index], logger=logger)
    reorderedFiles = append(reorderedFiles, files[index])
    reorderedTimes = append(reorderedTimes, getMLFileCreatedTime(files[index]))
  }
  
  df$mzmlFile = reorderedFiles
  df$time = reorderedTimes
  df = df[order(df$time),]
  offsets = as.numeric(difftime(df$time, df$time[1], units='hours'))
  df$time = offsets
  df
}

# Get the IDs of samples with the given sample type
getWantedIds <- function(batchInformation, wantedIds) {
    rownames(batchInformation[batchInformation[,'type'] %in% wantedIds,])
}

# Get the sample names for each measurement in the 'raw' PeakML data
getMeasurementColumn <- function(data) {
    mNames = colnames(data$peakDataMtx)
    data$sampleNames[data$peakDataMtx[,which(mNames == 'MEASUREMENTID')]]
}

# Set up a data frame that contains the neccessary information for modelling
# the QC samples
getQCData <- function(allData, batchInformation, qcId) {
    qcIds = which(batchInformation$type == qcId)
    qcFiles = rownames(batchInformation[qcIds,])

    measurementNumbers = which(allData$sampleNames %in% qcFiles)
    mNames = colnames(allData$peakDataMtx)

    qcData = allData$peakDataMtx[allData$peakDataMtx[,which(mNames == 'MEASUREMENTID')] %in% measurementNumbers,]
    peakFiles = allData$sampleNames[qcData[,which(mNames == 'MEASUREMENTID')]]
    #peaks = unique(qcData[,which(mNames == 'GROUPID')])
    #numPeaks = length(peaks)
    #uniqueGroups = unique(batchInformation$batch)

    data = data.frame(time=batchInformation[peakFiles,'time'], group=batchInformation[peakFiles,'batch'], peak=qcData[,which(mNames == 'GROUPID')], intensity=log(qcData[,which(mNames == 'MAXINTENSITY')]))
}

#removeNonQCPeaks <- function(qcData, allData) {
#	qcPeaks = unique(qcData$peak)
#	mNames = colnames(allData$peakDataMtx)
#	keepPeaks = allData$peakDataMtx[,which(mNames == 'MEASUREMENTID')] %in% qcPeaks
#	allData$peakDataMtx = allData$peakDataMtx[keepPeaks,]
#	allData$chromDataList = allData$chromDataList[keepPeaks]
#	allData$sampleGroups = allData$sampleGroups[keepPeaks]
#	allData
#}
