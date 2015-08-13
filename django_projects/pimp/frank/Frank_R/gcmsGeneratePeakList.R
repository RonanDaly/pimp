generateGCMSPeakMatrix <- function(input_directory){
  
  require(rJava)
  require(mzmatch.R)
  # mzmatch.init(version.1=FALSE)
  mzmatch.init(12000, FALSE)
  
  xset <- xcmsSet(files=input_directory, method="centWave", ppm=2, snthresh=3, peakwidth=c(5,100),
                  prefilter=c(3,1000), mzdiff=0.001, integrate=0, fitgauss=FALSE, verbose.column=TRUE)
  inputfilenames<-xset@filepaths
  sampleList <- data.frame(inputfilenames)
  filepath <- sub("(.*\\/)([^.]+)(\\.[[:alnum:]]+$)", "\\1", levels(sampleList$inputfilenames))
  filename <- sub("(.*\\/)([^.]+)(\\.[[:alnum:]]+$)", "\\2", levels(sampleList$inputfilenames))
  peakMLFileName <- as.character(paste(filepath, filename, ".peakml", sep = ""))
  combinedPeakMLFileName <- as.character(paste(filepath, filename, "_combined", ".peakml", sep = ""))
  noisefilteredPeakMLFileName <- as.character(paste(filepath, filename, "_noise_filtered", ".peakml", sep = ""))
  minDetectionPeakMLFileName <- as.character(paste(filepath, filename, "_min_detections", ".peakml", sep = ""))
  minIntensityPeakMLFileName <- as.character(paste(filepath, filename, "_min_intensity", ".peakml", sep = ""))
  gapFilledPeakMLFileName <- as.character(paste(filepath, filename, "_gap_filled", ".peakml", sep = ""))
  mzMatchOutputPeakMLFileName <- as.character(paste(filepath, filename, "_mzmatch_output", ".peakml", sep = ""))
  basepeaksPeakMLFileName <- as.character(paste(filepath, filename, "_basepeaks", ".peakml", sep = ""))
  mzmatchTxtFileName <- as.character(paste(filepath, filename, "_output", ".txt", sep = ""))
  sampleList$outputfilenames <- peakMLFileName
  sampleList$combinedfilenames <- combinedPeakMLFileName
  sampleList$noisefilteredfilenames <- noisefilteredPeakMLFileName
  sampleList$mindetectionfilenames <- minDetectionPeakMLFileName
  sampleList$minintensityfilenames <- minIntensityPeakMLFileName
  sampleList$gapfilledfilenames <- gapFilledPeakMLFileName
  sampleList$mzmatchoutputfilenames <- mzMatchOutputPeakMLFileName
  sampleList$basepeaksfilenames <- basepeaksPeakMLFileName
  sampleList$mzmatchTxtfilenames <- mzmatchTxtFileName
  
  PeakML.xcms.write.SingleMeasurement(xset = xset, filename=sampleList$outputfilenames,
                                      ionisation="detect", ppm=5, addscans=0, ApodisationFilter=TRUE,
                                      nSlaves=1)
  
  for (index in 1:length(sampleList$outputfilenames)){
    mzmatch.ipeak.Combine(i=sampleList$outputfilenames[index], o=sampleList$combinedfilenames[index], v=T, rtwindow=60, combination="set",
                          ppm=5, nSlaves=1)
    mzmatch.ipeak.filter.NoiseFilter (i=sampleList$combinedfilenames[index],o=sampleList$noisefilteredfilenames[index],v=T,codadw=0.8)
    #     mzmatch.ipeak.filter.SimpleFilter(i=sampleList$noisefilteredfilenames[index], o=sampleList$mindetectionfilenames[index], mindetections=4, v=T)
    mzmatch.ipeak.filter.SimpleFilter(i=sampleList$noisefilteredfilenames[index], o=sampleList$minintensityfilenames[index], minintensity=1000, v=T)
    mzmatch.ipeak.sort.RelatedPeaks (i=sampleList$minintensityfilenames[index],v=T,o=sampleList$mzmatchoutputfilenames[index],basepeaks=sampleList$basepeaksfilenames[index],ppm=3,rtwindow=6)
    ### Both annot and mzmatch.ipeak.convert.ConvertToText are working ###
    annot <- paste("relation.id,relation.ship,codadw,charge")
    mzmatch.ipeak.convert.ConvertToText (i=sampleList$mzmatchoutputfilenames[index],o=sampleList$mzmatchTxtfilenames[index],v=T,annotations=annot)
  }
  
  mzXMLFiles <- as.character(levels(sampleList$inputfilenames))
  txtOutputFiles <- as.character(sampleList$mzmatchTxtfilenames)
  outputList <- data.frame(mzXMLFiles, txtOutputFiles)
  return (outputList)
}