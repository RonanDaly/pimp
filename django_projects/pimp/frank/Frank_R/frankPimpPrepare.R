
frankPimpPrepare <- function (source_directory, ms1_peaks, file_pol_df){

    print ('MS1 peaks passed now in frankPimpPrep')

    frags <- get_empty_df()
    polarities <- c("positive", "negative")

    for (pol in polarities){

        new_frags <- runPolarityGroups(ms1_peaks, file_pol_df, pol)
        frags <- rbind(frags, new_frags)
    }

    print ('All Fragments returned from method 3')
    print (head(frags))
    return (frags)
}

get_empty_df <- function() {

    # make an empty dataframe possbibly not the way to do this but worth a try
    frags_colnames <- c("peakID", "MSnParentPeakID", "msLevel", "rt", "mz", "intensity",
                        "Sample", "GroupPeakMSn", "CollisionEnergy")
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
        polarity <- frag_f_pol$polarity

    # Run method 3 to get the fragments
        frags <- run_create_peak_method_3(ms1, frag_file)
    }

  return(frags)
}

