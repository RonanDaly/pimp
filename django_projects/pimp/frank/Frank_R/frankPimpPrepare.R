
frankPimpPrepare <- function (source_directory, ms1_peaks, file_pol_df){

    print ('MS1 peaks passed now in frankPimpPrep')

    # files <- list.files(path=source_directory, pattern= "\\.mzML$")
    # print('files')
    # fragment_file <- files[[1]]


    frags <- get_empty_df()
    polarities <- c("positive", "negative")

    for (pol in polarities){

        new_frags <- runPolarityGroups(ms1_peaks, file_pol_df, pol)
        #Add the sourcefile as a column to the new frags

        frags <- rbind(frags, new_frags)
    }

    peaks <- as.data.frame(frags)
    #sourcePeakList <- factor(sampleList, labels = sourcefiles)
    #peaks[, "SourceFile"] <- sourcePeakList

    print ('Head and tail of all Fragments returned from method 3')
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

runPolarityGroups <- function (ms1_df, frag_pol_df, pol){

    cat('Running a polarity group', pol)

    source(paste(getwd(), '/frank/Frank_R/frankPeakSet3.R', sep=""))
    ms1     <- subset(ms1_df,polarity==pol)
    frag_f_pol <- subset(frag_pol_df,polarity==pol)
    frags <- get_empty_df()

    #If the polarity is found in the frag_pol_df
    if (nrow(frag_f_pol)!=0) {

        #Get the name of the fragment file
        frag_file <- toString(frag_f_pol$filename)

        # Run method 3 to get the fragments
        frags <- run_create_peak_method_3(ms1, frag_file)

        #Add the sourceFile to the fragments returned as a Vector (reqd by Frank)

        sampleList <- frags[, 'Sample']
        sourcefiles <- basename(frag_file)
        sourcePeakList <- factor(sampleList, labels = sourcefiles)
        frags[, "SourceFile"] <- sourcePeakList

        print ("Method 3 returning head of peaks")
        print (head(frags))
    }
  return(frags)
}

