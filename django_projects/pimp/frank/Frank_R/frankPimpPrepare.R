
frankPimpPrepare <- function (source_directory, ms1_peaks, file_pol_df){

    print ('MS1 peaks passed now in frankPimpPrep, head of ms1 peaks is')
    print (head(ms1_peaks))

    #Create an empty df
    frags <- get_empty_df()

    #frags <- runPolarityGroups(ms1_peaks, file_pol_df)

    source(paste(getwd(), '/frank/Frank_R/frankPeakSet3.R', sep=""))
    ms1     <- ms1_peaks


    #Get the name of the fragment file
    frag_file <- toString(file_pol_df$filename)

    # Run method 3 to get the fragments

    frags <- run_create_peak_method_3(ms1, frag_file)

    #Add the sourceFile to the fragments returned as a Vector (reqd by Frank)

     sampleList <- frags[, 'Sample']
     sourcefiles <- basename(frag_file)
     sourcePeakList <- factor(sampleList, labels = sourcefiles)
     frags[, "SourceFile"] <- sourcePeakList


    peaks <- as.data.frame(frags)
    print ('Head and tail Fragments returned from method 3')
    print (head(peaks))
    print (tail(peaks))
    return (peaks)
}

get_empty_df <- function() {

    # make an empty dataframe possbibly not the way to do this but worth a try
    frags_colnames <- c("peakID", "MSnParentPeakID", "msLevel", "rt", "mz", "intensity",
                        "Sample", "GroupPeakMSn", "CollisionEnergy", "SourceFile")
    frag_df <- data.frame(t(rep(NA, length(frags_colnames))))
    frag_df <- frag_df[-1, ] # delete first row of all NAs

    return (frag_df)

}

runPolarityGroups <- function (ms1_df, frag_pol_df){

    print ('Running a polarity group')

    source(paste(getwd(), '/frank/Frank_R/frankPeakSet3.R', sep=""))
    ms1     <- ms1_df
    frags <- get_empty_df()


     #Get the name of the fragment file
     frag_file <- toString(frag_pol_df$filename)

     # Run method 3 to get the fragments
      frags <- run_create_peak_method_3(ms1, frag_file)

      #Add the sourceFile to the fragments returned as a Vector (reqd by Frank)

      sampleList <- frags[, 'Sample']
      sourcefiles <- basename(frag_file)
      sourcePeakList <- factor(sampleList, labels = sourcefiles)
      frags[, "SourceFile"] <- sourcePeakList
      print ("returning a single polarity from method 3")

  return(frags)
}

