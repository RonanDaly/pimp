frankPimpPrepare <- function (source_directory, ms1_peaks, file_pol_df){


 print ('MS1 peaks passed now in frankPimpPrep')

 #Now we want to pass the MS1 peaks with the fragment file of equal polarity.
 print ('the file polarity mapping in R')
 print (file_pol_df)

 # files <- list.files(path=source_directory, pattern= "\\.mzML$")
 # print('files')
 # fragment_file <- files[[1]]

 #frags has to be the same data structure as is returned from Method3.

 frags <- data.frame(x = character(0), y = character(0))
 source(paste(getwd(), '/frank/Frank_R/runPolarityGroups.R', sep=""))

 #Pass in the polarities that exists in the file_pol_df

 polarities <- c("positive", "negative")
 for (pol in polarities){

    new_frags <- runPolarityGroups(ms1_peaks, file_pol_df, pol)
    frags <- rbind(frags, new_frags)
  }

 print ('Fragmenst returned from method 3')
 print (frags)




 ## Label the peaks with the source file they were derived from ###
  #peaks <- as.data.frame(frags@peaks)
  #sourcefiles <- basename(xset@filepaths)
  #sampleList <- peaks[, 'Sample']
  #sourcePeakList <- factor(sampleList, labels = sourcefiles)
  #peaks[, "SourceFile"] <- sourcePeakList

  #return (peaks)

}